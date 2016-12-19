import os
import psycopg2
import urlparse
from werkzeug.datastructures import ImmutableDict

def init():
    """
    Initialize the database connection.

    The particular environment variable DATABASE_URL comes from the heroku specification for using postgres.
    """
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

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
    cur.execute("INSERT INTO calendar_events (start_time, end_time, person) VALUES (to_timestamp(%s, 'YYYY-MM-DDTHH:MI'), to_timestamp(%s,'YYYY-MM-DDTHH:MI'), %s) returning id", (start_time.isoformat(), end_time.isoformat(), person))
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
    cur.execute("SELECT * FROM calendar_events WHERE id = %s", (event_id,))
    return cur.fetchone()

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
    Edit a time object in the database.

    Takes in a psycopg2 connection, event id, and a json object containing the new data.

    Not implemented yet.
    """
    pass

def close(conn):
    """
    Closes the database connection.
    """
    conn.close()
