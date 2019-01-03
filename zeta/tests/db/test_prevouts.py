import sqlite3

import unittest

from zeta.db import addresses, connection, prevouts


class TestPrevouts(unittest.TestCase):

    def setUp(self):
        # Replace the connection with an in-memory DB to avoid pollution
        c = sqlite3.connect(':memory:')
        c.row_factory = sqlite3.Row
        self._old_conn = connection.CONN
        connection.CONN = c
        connection.ensure_tables()

        self.prevout = {
                'outpoint': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b000000000',  # noqa: E501
                'tx_id': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b0',  # noqa: E501
                'idx': 0,
                'value': 41794084,
                'spent_at': 554702,
                'spent_by': '67253ba14ecfb8f5cf2053f7015ea5d7a335ce016321dfb3085d8181dd9e242a',  # noqa: E501
                'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'}
        self.assertTrue(addresses.store_address({'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW', 'script': b'', 'script_pubkeys': []}))  # noqa: E501
        self.assertTrue(prevouts.store_prevout(self.prevout))

    def tearDown(self):
        connection.CONN = self._old_conn

    @unittest.skip('WIP')
    def test_store_prevout(self):
        ...

    def test_prevout_from_row(self):
        self.assertEqual(
            prevouts.prevout_from_row(self.prevout),
            self.prevout)

    def test_find_by_address(self):
        self.assertEqual(
            prevouts.find_by_address(self.prevout['address']),
            [self.prevout])

    def test_find_by_tx_id(self):
        self.assertEqual(
            prevouts.find_by_tx_id(self.prevout['tx_id']),
            [self.prevout])

    def test_find_by_outpoint(self):
        self.assertEqual(
            prevouts.find_by_outpoint(self.prevout['outpoint']),
            self.prevout)

    def test_find_all_unspents(self):
        self.assertEqual(
            prevouts.find_all_unspents(),
            [])

    def test_find_by_child(self):
        self.assertEqual(
            prevouts.find_by_child(self.prevout['spent_by']),
            [self.prevout])

    def test_find_by_value_range(self):
        self.assertEqual(
            prevouts.find_by_value_range(0, 41794084, False),
            [self.prevout])

        self.assertEqual(
            prevouts.find_by_value_range(0, 41794084),
            [])
