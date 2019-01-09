import unittest
# from unittest import mock

from zeta import crypto


class TestCrypto(unittest.TestCase):

    def test_is_pubkey(self):
        self.assertTrue(crypto.is_pubkey('0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'))  # noqa: E501
        self.assertTrue(crypto.is_pubkey('0350863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'))  # noqa: E501
        self.assertTrue(crypto.is_pubkey('0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b235250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'))  # noqa: E501
        self.assertFalse(crypto.is_pubkey('aa'))
        self.assertFalse(crypto.is_pubkey('deadbeef'))
        self.assertFalse(crypto.is_pubkey('this is not hex'))
        self.assertFalse(crypto.is_pubkey('0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b235250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'))  # noqa: E501    ...

    def test_coerce_key(self):
        crypto.coerce_key('38' * 32)
        crypto.coerce_key(b'\x38' * 32)

    def test_coerce_pubkey(self):
        crypto.coerce_pubkey('0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798')  # noqa: E501
        crypto.coerce_pubkey('0350863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352')  # noqa: E501

        with self.assertRaises(ValueError) as context:
            crypto.coerce_pubkey('383838')
        self.assertIn('Unsupported pubkey format', str(context.exception))

        # not a real curve point makes ecdsa throw
        with self.assertRaises(AssertionError) as context:
            crypto.coerce_pubkey('0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b235250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352')  # noqa: E501

    def test_pow_mod(self):
        # https://www.wolframalpha.com/input/?i=(4%5E6)mod+12
        a = crypto.pow_mod(4, 6, 12)
        self.assertEqual(a, 4)
        # https://www.wolframalpha.com/input/?i=(4%5E7)mod+11
        b = crypto.pow_mod(4, 7, 11)
        self.assertEqual(b, 5)
