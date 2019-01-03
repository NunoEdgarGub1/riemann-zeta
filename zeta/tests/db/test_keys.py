import sqlite3
import unittest

from zeta import utils
from zeta.db import addresses, connection, keys


class TestKeys(unittest.TestCase):

    def setUp(self):
        c = sqlite3.connect(':memory:')
        c.row_factory = sqlite3.Row
        self._old_conn = connection.CONN
        connection.CONN = c
        connection.ensure_tables()

        self.secret = 'toast'

        self.test_key = {
            'pubkey': '0279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08',  # noqa: E501
            'privkey': b'\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01',  # noqa: E501
            'derivation': '',
            'chain': 'btc',
            'address': 'bc1q3mp3sj3x65y6xcnhcw2qkdhnk6hg9shutrm23s'}

        encrypted = self.test_key.copy()
        encrypted['privkey'] = utils.encode_aes(encrypted['privkey'],
                                                self.secret)
        self.enc_test_key = encrypted

        self.assertTrue(keys.store_key(self.test_key, self.secret))

    def tearDown(self):
        connection.CONN.close()
        connection.CONN = self._old_conn

    def test_key_from_row(self):
        self.assertEqual(
            keys.key_from_row(self.enc_test_key, self.secret),
            self.test_key)

    @unittest.skip('WIP')
    def test_store_key(self):
        ...

    def test_validate_key(self):
        # bad address
        self.assertFalse(keys.validate_key(
            {
                'pubkey': '0279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08',  # noqa: E501
                'privkey': b'\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01',  # noqa: E501
                'derivation': '',
                'chain': 'btc',
                'address': 'bc1q3mp3sj3x65y6xcnhcw2qkdhnk6hg9shutrm233'}
        ))
        # bad pubkey
        self.assertFalse(keys.validate_key(
            {
                'pubkey': '0379a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08',  # noqa: E501
                'privkey': b'\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01',  # noqa: E501
                'derivation': '',
                'chain': 'btc',
                'address': 'bc1q3mp3sj3x65y6xcnhcw2qkdhnk6hg9shutrm23s'}
        ))
        # bad privkey
        self.assertFalse(keys.validate_key(
            {
                'pubkey': '0279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08',  # noqa: E501
                'privkey': b'\x13\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01',  # noqa: E501
                'derivation': '',
                'chain': 'btc',
                'address': 'bc1q3mp3sj3x65y6xcnhcw2qkdhnk6hg9shutrm23s'}
        ))

    def test_find_by_address(self):
        res = keys.find_by_address(self.test_key['address'], self.secret)
        self.assertEqual(res, self.test_key)

    def test_find_by_pubkey(self):
        res = keys.find_by_pubkey(self.test_key['pubkey'], self.secret)
        self.assertEqual(res[0], self.test_key)

    def test_find_by_script(self):
        script = bytes.fromhex('210279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08210279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef06ac')  # noqa: E501
        self.assertTrue(
            addresses.store_address({
                'address': 'bc1q9m378m3z3facvxaddmk694p3ynqw8n644df7lynn4kpy3fmvg4tq57wx6a',  # noqa: E501
                'script': script,
                'script_pubkeys': ['0279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef08', '0279a0ac5aa3a2efba0cfab8370816580ae3a561be7e4b47c59cf8c35e38beef06']}))  # noqa: E501
        res = keys.find_by_script(script, self.secret)
        self.assertEqual(res[0], self.test_key)
