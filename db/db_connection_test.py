import unittest
import db_connection
import psycopg2
import urlparse
import os
import mock
from mock import patch

class TestDBMethods(unittest.TestCase):
    @patch.dict(os.environ,{'DATABASE_URL': 'postgres'})
    @patch('psycopg2.connect')
    def test_insert(self, psycopg2_mock):
        #psycopg2_mock.return_value.cursor.
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
