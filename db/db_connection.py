import os
import psycopg2
import urlparse


def init():
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

def insert_time(conn, start_time, end_time, person):
    cur = conn.cursor()
    cur.execute("INSERT INTO calendar_events (start_time, end_time, person) VALUES (to_timestamp(%s, 'YYYY-MM-DDTHH:MI'), to_timestamp(%s,'YYYY-MM-DDTHH:MI'), %s)", start_time.isoformat(), end_time.isoformat(), person)
    conn.commit()

def close(conn, cur):
    cur.close()
    conn.close()
