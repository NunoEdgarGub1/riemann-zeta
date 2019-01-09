import unittest
from unittest import mock

from zeta.db import connection


class TestConnect(unittest.TestCase):

    @mock.patch('zeta.db.connection.get_cursor')
    def test_ensure_tables(self, mock_get_cursor):
        mock_get_cursor.return_value.execute.side_effect = ValueError()

        self.assertFalse(connection.ensure_tables())
