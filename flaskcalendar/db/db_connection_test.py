from __future__ import print_function
import unittest
import db_connection
import psycopg2
from urllib.parse import urlparse
import os
import unittest.mock as mock
from unittest.mock import patch
import datetime

class TestDBMethods(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(
            database='postgres'
        )
        cur = self.conn.cursor()

        drop_table_command = "DROP TABLE if exists dummy_calendar_events;"

        create_table_command = """CREATE TABLE IF NOT EXISTS dummy_calendar_events (
            id BIGSERIAL PRIMARY KEY,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            person VARCHAR(512)
        );"""

        cur.execute(drop_table_command)
        cur.execute(create_table_command)
        self.conn.commit()
        cur.close()

    @patch.dict(os.environ,{'DATABASE_URL': 'postgres'})
    @patch('psycopg2.connect')
    def test_insert_and_delete(self, psycopg2_mock):
        psycopg2_mock.return_value = self.conn
        conn = db_connection.init()

        # insert_result should be the id of the element just inserted
        insert_result = db_connection.insert_time(conn, datetime.datetime.today(), datetime.datetime.today(), "asdf")[0]

        # id shouldn't be 0
        print("id=%s" % insert_result)
        self.assertTrue(insert_result != 0)

        db_connection.delete_time(conn, insert_result)

    @patch.dict(os.environ,{'DATABASE_URL': 'postgres'})
    @patch('psycopg2.connect')
    def test_get(self, psycopg2_mock):
        psycopg2_mock.return_value = self.conn
        conn = db_connection.init()

        insert_result = db_connection.insert_time(conn, datetime.datetime.today(),
            datetime.datetime.today(), "TESTGET_PERSON")[0]
        print(insert_result)

        fetch_result = db_connection.read_time(conn, insert_result)
        print(fetch_result)
        self.assertTrue(fetch_result.get('person') == "TESTGET_PERSON")
        db_connection.delete_time(conn, insert_result)

    @patch.dict(os.environ,{'DATABASE_URL': 'postgres'})
    @patch('psycopg2.connect')
    def test_insert_and_get_many(self, psycopg2_mock):

        time_0 = datetime.datetime(year=2011, month=2, day=5)
        num_days = 16


        timestamps = [(chr(97 + i), time_0 + datetime.timedelta(days=i), time_0 + datetime.timedelta(days=i, hours=1))
                        for i in range(num_days)]

        psycopg2_mock.return_value = self.conn
        conn = db_connection.init()

        rlts_for_deletion = []
        present_before = len(db_connection.get_many(conn, time_0, time_0 + datetime.timedelta(days=num_days)))

        for person, start_time, end_time in timestamps:
            insert_result = db_connection.insert_time(conn, start_time, end_time, person)[0]
            rlts_for_deletion.append(insert_result)

        num_results = len(rlts_for_deletion)

        fetch_result = db_connection.get_many(conn, time_0, time_0 + datetime.timedelta(days=num_days))


        for i in rlts_for_deletion:
            db_connection.delete_time(conn, i)
        self.assertTrue(len(fetch_result) == num_results + present_before)

    @patch.dict(os.environ,{'DATABASE_URL': 'postgres'})
    @patch('psycopg2.connect')
    def test_edit_many(self, psycopg2_mock):
        psycopg2_mock.return_value = self.conn
        conn = db_connection.init()

    def tearDown(self):
        self.conn.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
