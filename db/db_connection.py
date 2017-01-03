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
        if issubclass(exc_type, psycopg2.Error):
            conn.rollback()
            print('Database transaction not successful: %s' % exc_value, file=sys.stderr)
            return True
        else:
            conn.close()
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
    cur.execute("""
        INSERT INTO calendar_events
            (start_time, end_time, person)
        VALUES
            (to_timestamp(%s, 'YYYY-MM-DDTHH:MI'), to_timestamp(%s,'YYYY-MM-DDTHH:MI'), %s)
        returning id""",
        (start_time.isoformat(), end_time.isoformat(), person)
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

def edit_time(conn, event_id, new_event_data):
    """
    TODO

    Edit a time object in the database.

    Takes in a psycopg2 connection, event id, and a json object containing the new data.

    Not implemented yet.
    """
    pass

def get_many(conn, start, end):
    """
    Get the last few time events from the database.

    As per the fullcalendar docs, the feed should take a start and end timestamp as parameters (https://fullcalendar.io/docs/event_data/events_function/)

    Takes in a psycopg2 connection and two datetime elements.
    """

    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM calendar_events
        WHERE start_time >= to_timestamp(%s, 'YYYY-MM-DDTHH:MI')
        AND start_time <= to_timestamp(%s,'YYYY-MM-DDTHH:MI')
    """, (start.isoformat(), end.isoformat()))

    conn.commit()
    tmp_l = cur.fetchall()[:]

    desc = cur.description
    ret = [ImmutableDict(dict([(desc[i].name, tmp[i]) for i in range(len(desc))])) for tmp in tmp_l]

    cur.close()
    return tmp_l

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
            SET {
                person = %s,
                start_time = to_timestamp(%s, 'YYYY-MM-DDTHH:MI'),
                end_time = to_timestamp(%s,'YYYY-MM-DDTHH:MI')
            }
            WHERE id=%s""",
            (person, start_time, end_time, event_id))
        else:
            person, start_time, end_time = datum.get('person'), datum.get('start_time'), datum.get('end_time')

            cur.execute("""
            INSERT INTO calendar_events
                (start_time, end_time, person)
            VALUES
                (to_timestamp(%s, 'YYYY-MM-DDTHH:MI'), to_timestamp(%s,'YYYY-MM-DDTHH:MI'), %s)""",
            (start_time.isoformat(), end_time.isoformat(), person))

    conn.commit()
    cur.close()


def close(conn):
    """
    Closes the database connection.
    """
    conn.close()
