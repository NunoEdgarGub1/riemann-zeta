import sqlite3
import unittest
from zeta.db import prevouts, connection
from zeta.zeta_types import Prevout


class TestPrevouts(unittest.TestCase):

    def setUp(self):
        c = sqlite3.connect(':memory:')
        c.row_factory = sqlite3.Row
        self._old_conn = connection.CONN
        connection.CONN = c
        connection.ensure_tables()

        self.test_prevouts = {
                'outpoint': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b000000000',    # noqa: E501
                'tx_id': 'a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b0',    # noqa: E501
                'idx': 0,
                'value': 41794084,
                'spent_at': 554702,
                'spent_by': '67253ba14ecfb8f5cf2053f7015ea5d7a335ce016321dfb3085d8181dd9e242a',    # noqa: E501
                'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'
                }
        self.assertTrue(prevouts.store_prevout(self.test_prevouts))

    def tearDown(self):
        connection.CONN.close()
        connection.CONN = self._old_conn

    def test_store_prevout(self):
        prevout = Prevout(
                outpoint='a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b000000000',    # noqa: E501
                tx_id='a76f3ccd1523f75b45a20f5e40ad71b70125a2f669a58a95aab5b71cbd28a4b0',   # noqa: E501
                idx=0,
                value=41794084,
                spent_at=554702,
                spent_by='67253ba14ecfb8f5cf2053f7015ea5d7a335ce016321dfb3085d8181dd9e242a',    # noqa: E501
                address='1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'
                )
        self.assertTrue(prevouts.store_prevout(prevout))

    def test_prevout_from_row(self):
        fake_row = {
                'outpoint': '2f8478795537b70b764a8781858bab278a0e27b42e86206a1a6c72883430664200000000',    # noqa: E501
                'tx_id': '2f8478795537b70b764a8781858bab278a0e27b42e86206a1a6c728834306642',   # noqa: E501
                'idx': 0,
                'value': 2483093,
                'spent_at': 554688,
                'spent_by': 'd4765814445dae7d85735f1d15e4dfafcb231dde26fc485f6c1b2fadb24b190c',    # noqa: E501
                'address': '12Ya1zzZHuPH4ERikkfNBW8BCvGwTDfKao'
                }
        prevout_entry = prevouts.prevout_from_row(fake_row)
        for key in fake_row:
            self.assertEqual(prevout_entry[key], fake_row[key])

    def test_find_by_address(self):
        res = prevouts.find_by_address(self.test_prevouts['address'])
        self.assertEqual(res[0], self.test_prevouts)

    def test_find_by_txid(self):
        res = prevouts.find_by_txid(self.test_prevouts['tx_id'])
        self.assertEqual(res[0], self.test_prevouts)

    def test_find_by_outpoint(self):
        res = prevouts.find_by_outpoint(self.test_prevouts['outpoint'])
        self.assertEqual(res[0], self.test_prevouts)

    def test_find_unspents(self):
        unspent_prevout = {
                'outpoint': '4f52a52d229bf6cef4dc24aee32c74c073862d5389c173e0f173dd105526809900000000',    # noqa: E501
                'tx_id': '4f52a52d229bf6cef4dc24aee32c74c073862d5389c173e0f173dd1055268099',    # noqa: E501
                'idx': 0,
                'value': 41794084,
                'spent_at': 0,
                'spent_by': '',
                'address': '1GniSeeH9Ui1ZK4eyoaopNP1TnQLEgQiFW'
                }
        prevouts.store_prevout(unspent_prevout)
        res = prevouts.find_unspents(unspent_prevout['tx_id'])
        self.assertEqual(res[0], unspent_prevout)
