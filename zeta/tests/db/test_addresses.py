import sqlite3
import unittest

from zeta.db import addresses, connection
# from zeta.zeta_types import AddressEntry


class TestAddresses(unittest.TestCase):

    def setUp(self):
        c = sqlite3.connect(':memory:')
        self._old_conn = connection.CONN
        connection.CONN = c

    def tearDown(self):
        connection.CONN = self._old_conn

    def test_address_from_row(self):
        fake_row = {
            'address': 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
            'script': bytes.fromhex('0014751e76e8199196d454941c45d1b3a323f1433bd6')  # noqa: E501
        }
        addr_entry = addresses.address_from_row(fake_row)
        for key in fake_row:
            self.assertEqual(addr_entry[key], fake_row[key])
        self.assertEqual(addr_entry['script_pubkeys'], [])
