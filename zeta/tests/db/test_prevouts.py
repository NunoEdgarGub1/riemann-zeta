import unittest
from zeta.db import prevouts
from zeta.zeta_types import Prevout


class TestPrevouts(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.skip('WIP')
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

    @unittest.skip('WIP')
    def test_prevout_from_row(self):
        pass

    @unittest.skip('WIP')
    def test_find_by_address(self):
        pass

    @unittest.skip('WIP')
    def test_find_by_txid(self):
        pass

    @unittest.skip('WIP')
    def test_find_by_outpoint(self):
        pass

    @unittest.skip('WIP')
    def test_find_unspents(self):
        pass
