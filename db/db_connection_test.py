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
        print(insert_result)
        self.assertTrue(insert_result != 0)

        db_connection.delete_time(conn, insert_result)

    def tearDown(self):
        self.conn.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
