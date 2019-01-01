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

    def test_validate_address(self):
        # valid pkh address
        self.assertTrue(addresses.validate_address({
            'address': 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
            'script': b'',  # noqa: E501
            'script_pubkeys': []
        }))

        # '0279BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798 OP_CHECKSIG'  # noqa: E501
        self.assertTrue(addresses.validate_address({
            'address': 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3',  # noqa: E501
            'script': bytes.fromhex('210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ac'),  # noqa: E501
            'script_pubkeys': ['0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798']  # noqa: E501
        }))

        # invalid address
        self.assertFalse(addresses.validate_address({
            'address': 'this is not a valid address',
            'script': None,
            'script_pubkeys': []
        }))

        # script doesn't match address
        self.assertFalse(addresses.validate_address({
            'address': 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3',  # noqa: E501
            'script': b'\xac\xac',  # OP_CHECKSIG OP_CHECKSIG
            'script_pubkeys': []
        }))

        # pubkey vector doesn't match script
        self.assertFalse(addresses.validate_address({
            'address': 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3',  # noqa: E501
            'script': bytes.fromhex('210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ac'),  # noqa: E501
            'script_pubkeys': ['this is not a pubkey']  # noqa: E501
        }))

    def test_pubkeys_from_script(self):
        self.assertEqual(
            addresses.pubkeys_from_script(bytes.fromhex('210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ac')),  # noqa: E501)
            ['0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798']  # noqa: E501
        )
        self.assertEqual(
            addresses.pubkeys_from_script(bytes.fromhex('210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81788210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81799210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ae')),  # noqa: E501
            ['0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81788', '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81799', '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798']  # noqa: E501
        )

    def test_score_address(self):
        ...

    def test_find_associated_pubkeys(self):
        ...

    def test_find_by_address(self):
        ...

    def test_find_by_script(self):
        ...

    def test_find_by_pubkey(self):
        ...
