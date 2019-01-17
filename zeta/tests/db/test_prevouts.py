import sqlite3

import unittest
from unittest import mock

from zeta.db import addresses, connection, prevouts


class TestPrevouts(unittest.TestCase):

    def setUp(self):
        # Replace the connection with an in-memory DB to avoid pollution
        c = sqlite3.connect(':memory:')
        c.row_factory = sqlite3.Row
        connection.CONN = c
        connection.ensure_tables()

        self.prevout = {
                'outpoint': {
                    'tx_id': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b0',  # noqa: E501
                    'index': 0},
                'value': 41794084,
                'spent_at': 554702,
                'spent_by': '67253ba14ecfb8f5cf2053f7015ea5d7a335ce016321dfb3085d8181dd9e242a',  # noqa: E501
                'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'}
        self.prevout_as_row = {
            'outpoint': 'b0a428bd1cb7b5aa958aa569f6a22501b771ad405e0fa2455bf72315cd3c6fa700000000',  # noqa: E501
            'tx_id': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b0',  # noqa: E501
            'idx': 0,
            'value': 41794084,
            'spent_at': 554702,
            'spent_by': '67253ba14ecfb8f5cf2053f7015ea5d7a335ce016321dfb3085d8181dd9e242a',  # noqa: E501
            'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'}
        self.assertTrue(addresses.store_address({'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW', 'script': b'', 'script_pubkeys': []}))  # noqa: E501
        self.assertTrue(prevouts.store_prevout(self.prevout))

    def tearDown(self):
        connection.CONN.close()

    def test_validate_prevout(self):
        # nothing
        self.assertFalse(prevouts.validate_prevout({}))
        # value can't be negative
        self.assertFalse(prevouts.validate_prevout({'value': -1}))
        # bad address
        self.assertFalse(prevouts.validate_prevout(
            {'address': '383838', 'value': 100}))

    def test_store_prevout(self):
        # fails validation
        self.assertFalse(prevouts.store_prevout({}))

    @mock.patch('zeta.db.prevouts.validate_prevout')
    def test_store_prevout_general_failure(self, mock_val):
        mock_val.return_value = True
        self.assertFalse(prevouts.store_prevout({}))

    def test_batch_store_prevouts(self):
        p_list = [{
            'outpoint': {
                'tx_id': '33' * 32,  # noqa: E501
                'index': i},
            'value': 333333333,
            'spent_at': 5555,
            'spent_by': '44' * 32,  # noqa: E501
            'address': '36gWkx1AR4ABH9nqzzsRJ6NFMedHw6QzW3'}
            for i in range(0, 10)]
        self.assertTrue(prevouts.batch_store_prevout(p_list))
        p_list.append({})
        self.assertFalse(prevouts.batch_store_prevout(p_list))

    @mock.patch('zeta.db.prevouts.validate_prevout')
    def test_batch_store_prevouts_general_failure(self, mock_val):
        mock_val.return_value = True
        p_list = [{}, {}]
        self.assertFalse(prevouts.batch_store_prevout(p_list))

    def test_prevout_from_row(self):
        self.assertEqual(
            prevouts.prevout_from_row(self.prevout_as_row),
            self.prevout)

    def test_flatten_prevout(self):
        self.assertEqual(
            prevouts._flatten_prevout(self.prevout),
            self.prevout_as_row)

    def test_find_by_address(self):
        self.assertEqual(
            prevouts.find_by_address(self.prevout['address']),
            [self.prevout])

    def test_find_by_tx_id(self):
        self.assertEqual(
            prevouts.find_by_tx_id(self.prevout['outpoint']['tx_id']),
            [self.prevout])

    def test_find_by_outpoint(self):
        self.assertEqual(
            prevouts.find_by_outpoint(self.prevout['outpoint']),
            self.prevout)
        self.assertIsNone(prevouts.find_by_outpoint({
            'tx_id': '99' * 32,
            'index': 1393983983}))

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

    def find_spent_by_mempool_tx(self):
        self.assertEqual(
            prevouts.find_spent_by_mempool_tx(),
            [])

    def test_check_for_known_outpoints(self):
        self.assertEqual(
            prevouts.check_for_known_outpoints([self.prevout['outpoint']]),
            [self.prevout['outpoint']])

    def test_find_spent_by_mempool_tx(self):
        self.assertEqual(
            prevouts.find_spent_by_mempool_tx(),
            [])

        mempool_spent = {
            'outpoint': {
                'tx_id': '83' * 32,  # noqa: E501
                'index': 83},
            'value': 333333333,
            'spent_at': -1,
            'spent_by': '21' * 32,  # noqa: E501
            'address': '36gWkx1AR4ABH9nqzzsRJ6NFMedHw6QzW3'}
        prevouts.store_prevout(mempool_spent)

        self.assertEqual(
            prevouts.find_spent_by_mempool_tx(),
            [mempool_spent])

    def test_find_all(self):
        prevouts.find_all()
