import os
import psycopg2
from urllib.parse import urlparse
import sys
from werkzeug.datastructures import ImmutableDict

class DBContextManager:
    """
    Context manager for database connections for the calendar app's database.

    Handles psycopg2 exceptions by automatically rolling back so every operation is sort of atomic.
    """
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None and issubclass(exc_type, psycopg2.Error):
            print('Database transaction not successful: %s' % exc_value, file=sys.stderr)
            self.conn.rollback()
            return True
        else:
            if exc_type is not None:
                return
            return True


def init():
    """
    Initialize the database connection.

    The particular environment variable DATABASE_URL comes from the heroku specification for using postgres.
    """
    url = urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

def insert_time(conn, start_time, end_time, person):
    """
    Insert a calendar event into the database.

    Takes in a psycopg2 connection, two datetime.datetime types for start and end time, and a person string.

    Returns the id of the database record just inserted
    """
    cur = conn.cursor()
    if end_time is not None:
        cur.execute("""
            INSERT INTO calendar_events
                (start_time, end_time, person)
            VALUES
                (TIMESTAMP %s, TIMESTAMP %s, %s)
            returning id""",
            (start_time.isoformat(), end_time.isoformat(), person)
        )
    else:
        cur.execute("""
            INSERT INTO calendar_events
                (start_time, person)
            VALUES
                (TIMESTAMP %s, %s)
            returning id""",
            (start_time.isoformat(), person)
        )

    conn.commit()
    tmp = cur.fetchone()
    cur.close()
    return tmp

def read_time(conn, event_id):
    """
    Get a particular time event from the database.

    Takes in a psycopg2 connection and an event_id (number, resolves to long)

    Returns the data retrieved from the database.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM calendar_events WHERE id = %s", (event_id,))
    conn.commit()
    tmp = cur.fetchone()
    desc = cur.description
    cur.close()
    return ImmutableDict(dict([(desc[i].name, tmp[i]) for i in range(len(desc))]))

def delete_time(conn, event_id):
    """
    Deletes the calendar event with the given `event_id` from the database.

    Takes in a psycopg2 connection and an event_id as a number (resolves to long).

    No return value. Raises a psycopg2 error if something goes wrong.
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM calendar_events WHERE id = %s", (event_id,))
    conn.commit()
    cur.close()

def edit_time(conn, event_id, person, start_time, end_time):
    """
    TODO

    Edit a time object in the database.

    Takes in a psycopg2 connection, event id, and a json object containing the new data.

    """

    cur = conn.cursor()
    print("Event id to edit:", event_id, "// Start time for edit:", start_time, "// End time for edit:", end_time)

    if end_time is not None:
        cur.execute("""
        UPDATE calendar_events
        SET (person, start_time, end_time) =
            (%s, TIMESTAMP %s, TIMESTAMP %s)
        WHERE id=%s
        RETURNING *""",
        (person, start_time.isoformat(), end_time.isoformat(), event_id))
    else:
        cur.execute("""
        UPDATE calendar_events
        SET (person, start_time) =
            (%s, TIMESTAMP %s)
        WHERE id=%s
        RETURNING *""",
        (person, start_time.isoformat(), event_id))


    conn.commit()

    desc = cur.description
    ret_data = cur.fetchone()

    cur.close()
    return ImmutableDict(dict([(desc[i].name, ret_data[i]) for i in range(len(desc))]))

def get_many(conn, start, end):
    """
    Get the last few time events from the database.

    As per the fullcalendar docs, the feed should take a start and end timestamp as parameters (https://fullcalendar.io/docs/event_data/events_function/)

    Takes in a psycopg2 connection and two datetime elements.
    """

    cur = conn.cursor()
    cur.execute("""
    SELECT id, start_time, end_time, person FROM calendar_events
        WHERE start_time >= TIMESTAMP %s
        AND start_time <= TIMESTAMP %s
    """, (start.isoformat(), end.isoformat()))

    def convert(t):
        if t[2] is None:
            t2r = None
        else:
            t2r = t[2].isoformat()
        t1r = t[1].isoformat()
        return (t[0], t1r, t2r, t[3])

    conn.commit()
    tmp_l = list(map(convert, cur.fetchall()[:]))
    print(tmp_l)

    desc = cur.description
    ret = [ImmutableDict({
        'id': tmp[0],
        'start': tmp[1],
        'end': tmp[2],
        'title': tmp[3]
    }) for tmp in tmp_l]

    cur.close()
    return ret

def insert_or_edit_batch(conn, new_event_data):
    """
    TODO

    Edit a set of time objects in the database.

    Takes in a psycopg2 connection, and an array containing the new data.
    Each datum is in the form of a werkzeug ImmutableDict.
    """

    cur = conn.cursor()

    for datum in new_event_data:
        if datum.get('id') is not None:
            event_id, = datum.get('id')
            person = datum.get('person')
            start_time = datum.get('start_time')
            end_time = datum.get('end_time')

            cur.execute("""
            UPDATE calendar_events
            SET (person, start_time, end_time) =
                (%s, to_timestamp(%s, 'YYYY-MM-DD\\THH:MI'), to_timestamp(%s,'YYYY-MM-DD\\THH:MI'))
            WHERE id=%s""",
            (person, start_time.isoformat(), end_time.isoformat(), event_id))
        else:
            person, start_time, end_time = datum.get('person'), datum.get('start_time'), datum.get('end_time')

            cur.execute("""
            INSERT INTO calendar_events
                (start_time, end_time, person)
            VALUES
                (to_timestamp(%s, 'YYYY-MM-DD\\THH:MI'), to_timestamp(%s,'YYYY-MM-DD\\THH:MI'), %s)""",
            (start_time.isoformat(), end_time.isoformat(), person))

    conn.commit()
    cur.close()


def close(conn):
    """
    Closes the database connection.
    """
    conn.close()
