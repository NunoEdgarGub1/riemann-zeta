import unittest

from zeta.electrum import eutils


class TestEutils(unittest.TestCase):

    def test_address_to_electrum_scripthash(self):
        self.assertEqual(
            eutils.address_to_electrum_scripthash('bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3'),  # noqa: E501
            '94ef09765c3092cd7a1d9f7a6e1ff861e446fd795d1e8a93f427c42df7ffe123')

        self.assertEqual(
            eutils.address_to_electrum_scripthash('bc1qmqyekxnf4xhxffv5fnlu387sggkhd5pw2w7g5tvtmjuar6ev6d6sld5pfl'),  # noqa: E501
            '9425e22d42d44eafa895c037e23c9bafb4887738c3039b4dd8ffe84541e1d39f')

        self.assertEqual(
            eutils.address_to_electrum_scripthash('36gWkx1AR4ABH9nqzzsRJ6NFMedHw6QzW3'),  # noqa: E501
            '862acc0dbea544944a789b00e82c4a9494945d12eb0f946f3257a6e3a49ed883')
