import sqlite3
import unittest
from unittest import mock

from zeta.db import checkpoint, connection, headers


class TestHeaders(unittest.TestCase):

    def setUp(self):
        c = sqlite3.connect(':memory:')
        c.row_factory = sqlite3.Row
        connection.CONN = c
        connection.ensure_tables()

        self.test_header = {
            'hash': '00000000000000000029f5e855578d7a81f4501f38093c46cb88a47664bf3c0e',  # noqa: E501
            'version': 549453824,
            'prev_block': '0000000000000000001e6525727cc0a729b1e928dff16db10d789176b59dd3eb',  # noqa: E501
            'merkle_root': '19a0368be5061871be3929e11b0e13de2c5f34e45310ca2798ebe14783413252',  # noqa: E501
            'timestamp': 1544230162,
            'nbits': '7cd93117',
            'nonce': '5507350b',
            'difficulty': 5646403851534,
            'hex': '0000c020ebd39db57691780db16df1df28e9b129a7c07c7225651e00000000000000000019a0368be5061871be3929e11b0e13de2c5f34e45310ca2798ebe1478341325212150b5c7cd931175507350b',  # noqa: E501
            'height': 552955,
            'accumulated_work': 0
        }

        self.parsed_500 = headers.parse_header('01000000459f16a1c695d04282fd9f84f4fe771121d467e5497eb1aa8bf66d8000000000cf7ef5b5c22d4edf641f0fd5fcfbcefa30acaa2fbc910206f8773e3918748504c1586e49ffff001d398eff7a')  # noqa: E501
        self.parsed_500['height'] = 500
        self.block_501 = '01000000db773c8f3b90efa51d8e40291406897062c164dff617d2a7bf64f64f00000000774328ddff50701ade3a2e1f28711643a17ad5f53f1e94639b04234fa0a5bbcf575b6e49ffff001d7232e103'  # noqa: E501
        self.block_502 = '01000000f9980503946685d96c93e577fbc9178bf36afda513d16ca79272884600000000a2211eb4bc799c5a8f144bf04cae15842c7981ceab73ab53df166eaec53b6d99275d6e49ffff001d1f75f325'  # noqa: E501

        self.assertTrue(headers.store_header(self.test_header))

    def tearDown(self):
        connection.CONN.close()

    def test_header_from_row(self):
        self.assertEqual(
            headers.header_from_row(self.test_header),
            self.test_header)

    def test_check_work(self):
        self.assertTrue(headers.check_work(self.test_header))
        for header in checkpoint.CHECKPOINTS['bitcoin_test']:
            self.assertTrue(headers.check_work(header))
        bad_header = self.test_header.copy()
        bad_header['hash'] = '77' * 32
        self.assertFalse(headers.check_work(bad_header))

    def test_make_target(self):
        self.assertEqual(
            headers.make_target(bytes.fromhex('01003456')[::-1]),
            0x00)
        self.assertEqual(
            headers.make_target(bytes.fromhex('01123456')[::-1]),
            0x12)
        self.assertEqual(
            headers.make_target(bytes.fromhex('02008000')[::-1]),
            0x80)
        self.assertEqual(
            headers.make_target(bytes.fromhex('05009234')[::-1]),
            0x92340000)

    def test_parse_difficulty(self):
        for header in checkpoint.CHECKPOINTS['bitcoin_test']:
            self.assertEqual(
                headers.parse_difficulty(bytes.fromhex(header['nbits'])),
                header['difficulty'])

    def test_parse_header(self):
        for header in checkpoint.CHECKPOINTS['bitcoin_test']:
            self.assertEqual(
                headers.parse_header(header['hex']),
                header)
        with self.assertRaises(ValueError) as context:
            headers.parse_header('33')
        self.assertIn('Invalid header received', str(context.exception))

    def test_batch_store_header(self):
        self.assertTrue(headers.batch_store_header(
            checkpoint.CHECKPOINTS['bitcoin_test']))

    @mock.patch('zeta.db.headers.check_work')
    def test_batch_store_header_failure(self, mock_check):
        mock_check.return_value = True
        self.assertFalse(headers.batch_store_header(
            [{'prev_block': '00', 'hash': '00'}]))

    @mock.patch('zeta.db.headers.parse_header')
    def test_batch_store_header_parse_string(self, mock_parse):
        mock_parse.return_value = self.test_header
        self.assertTrue(headers.batch_store_header(['']))

    def test_batch_store_header_parent_finding(self):
        # set this block as base for the chain
        self.assertTrue(headers.store_header(self.parsed_500))

        # add a couple children
        self.assertTrue(headers.batch_store_header(
            [self.block_501, self.block_502]))

        heaviest = headers.find_heaviest()[0]
        self.assertEqual(
            heaviest['hex'],
            self.block_502)
        self.assertEqual(
            heaviest['height'],
            502)

    def test_parent_height_and_work(self):
        # set this block as base for the chain
        self.assertTrue(headers.store_header(self.parsed_500))
        parsed_501 = headers.parse_header(self.block_501)
        self.assertEqual(
            headers.parent_height_and_work(parsed_501),
            (500, 0))
        self.assertEqual(
            headers.parent_height_and_work(self.parsed_500),
            (0, 0))

    def test_store_header(self):
        self.assertTrue(headers.store_header(self.parsed_500))
        self.assertTrue(headers.store_header(self.block_501))
        self.assertTrue(headers.store_header(self.block_502))

    @mock.patch('zeta.db.headers.check_work')
    def test_store_header_work_fail(self, mock_check):
        mock_check.return_value = False
        self.assertFalse(headers.store_header(self.block_501))

    def test_store_header_parent_height_0(self):
        bad_500 = self.parsed_500.copy()
        bad_500['height'] = 0
        self.assertTrue(headers.store_header(bad_500))
        self.assertTrue(headers.store_header(self.block_501))

    @mock.patch('zeta.db.headers.connection.get_cursor')
    def test_store_header_general_failure(self, mock_get_cursor):
        mock_get_cursor.return_value.execute.side_effect = ValueError()
        self.assertFalse(headers.store_header(self.parsed_500))

    def test_find_by_height(self):
        self.assertEqual(headers.find_by_height(500), [])
        self.assertTrue(headers.store_header(self.parsed_500))
        self.assertEqual(headers.find_by_height(500), [self.parsed_500])

    def test_find_by_hash(self):
        self.assertIsNone(headers.find_by_hash(self.parsed_500['hash']))
        self.assertTrue(headers.store_header(self.parsed_500))
        self.assertEqual(
            headers.find_by_hash(self.parsed_500['hash']),
            self.parsed_500)

    @mock.patch('zeta.db.headers.check_work')
    def test_find_highest(self, mock_check):
        mock_check.return_value = True

        self.assertEqual(headers.find_highest(), [self.test_header])

        same_height = self.test_header.copy()
        same_height['hash'] = '33' * 32
        self.assertTrue(headers.store_header(same_height))
        self.assertEqual(
            headers.find_highest(),
            [self.test_header, same_height])

        higher = self.test_header.copy()
        higher['height'] = 300000000
        self.assertTrue(headers.store_header(higher))
        self.assertEqual(headers.find_highest(), [higher])

    def test_find_heaviest(self):
        self.assertTrue(headers.store_header(self.parsed_500))
        self.assertEqual(
            headers.find_heaviest(),
            [self.test_header, self.parsed_500])
        self.assertTrue(headers.store_header(self.block_501))
        self.assertEqual(
            headers.find_heaviest()[0]['hex'],
            self.block_501)
        self.assertTrue(headers.store_header(self.block_502))
        self.assertEqual(
            headers.find_heaviest()[0]['hex'],
            self.block_502)
