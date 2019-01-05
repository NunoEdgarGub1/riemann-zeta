import asyncio
import unittest
from unittest import mock
from contextlib import suppress

from zeta.electrum import electrum


async def do_nothing(arg):
    return arg


class TestElectrum(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # StackExchange Code
        # cleanly shut down any pending tasks (e.g. queue forwarders)
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            # Now we should await task to execute it's cancellation.
            # Cancelled task raises asyncio.CancelledError that we can suppress
            with suppress(asyncio.CancelledError):
                self.loop.run_until_complete(task)

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_subscribe_to_headers(self, mock_get):
        client = mock.MagicMock()
        sub_q = asyncio.Queue()

        client.subscribe.return_value = (do_nothing(6), sub_q)
        mock_get.return_value = do_nothing(client)

        async def _test():
            await sub_q.put(7)
            await sub_q.put(8)
            q = asyncio.Queue()
            await electrum.subscribe_to_headers(q)

            self.assertEqual(await q.get(), 6)
            self.assertEqual(await q.get(), 7)
            self.assertEqual(await q.get(), 8)

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_get_headers(self, mock_get):
        client = mock.MagicMock()
        client.RPC.return_value = do_nothing('fakeret')

        mock_get.return_value = do_nothing(client)

        async def _test():
            self.assertEqual(
                await electrum.get_headers(500, 2016),
                'fakeret')

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_get_tx(self, mock_get):
        client = mock.MagicMock()
        client.RPC.return_value = \
            do_nothing('010000000001011746bd867400f3494b8f44c24b83e1aa58c4f0ff25b4a61cffeffd4bc0f9ba300000000000ffffffff024897070000000000220020a4333e5612ab1a1043b25755c89b16d55184a42f81799e623e6bc39db8539c180000000000000000166a14edb1b5c2f39af0fec151732585b1049b07895211024730440220276e0ec78028582054d86614c65bc4bf85ff5710b9d3a248ca28dd311eb2fa6802202ec950dd2a8c9435ff2d400cc45d7a4854ae085f49e05cc3f503834546d410de012103732783eef3af7e04d3af444430a629b16a9261e4025f52bf4d6d026299c37c7400000000')  # noqa: E501

        mock_get.return_value = do_nothing(client)

        async def _test():
            tx = await electrum.get_tx('00' * 32)
            self.assertEqual(
                tx.tx_id.hex(),
                'd60033c5cf5c199208a9c656a29967810c4e428c22efb492fdd816e6a0a1e548')  # noqa: E501

            # NB: to test the None case we have to make new awaitables
            mock_get.return_value = do_nothing(client)
            client.RPC.return_value = do_nothing(None)
            self.assertIsNone(await electrum.get_tx('00' * 32))

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_get_tx_verbose(self, mock_get):
        client = mock.MagicMock()
        client.RPC.return_value = \
            do_nothing('77')  # noqa: E501

        mock_get.return_value = do_nothing(client)

        async def _test():
            tx = await electrum.get_tx_verbose('00' * 32)
            self.assertEqual(
                tx,
                '77')  # noqa: E501

            # NB: to test the None case we have to make new awaitables
            mock_get.return_value = do_nothing(client)
            client.RPC.return_value = do_nothing(None)
            self.assertIsNone(await electrum.get_tx_verbose('00' * 32))

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_subscribe_to_address(self, mock_get):
        client = mock.MagicMock()
        sub_q = asyncio.Queue()

        client.subscribe.return_value = (do_nothing(6), sub_q)
        mock_get.return_value = do_nothing(client)

        async def _test():
            await sub_q.put(7)
            await sub_q.put(8)
            q = asyncio.Queue()
            await electrum.subscribe_to_address(
                address='bc1qmqyekxnf4xhxffv5fnlu387sggkhd5pw2w7g5tvtmjuar6ev6d6sld5pfl',  # noqa: E501
                outq=q)

            # FIXME: using an invalid address will cause these to block forever
            #        wrap these gets in a timeout that causes the test to fail
            self.assertEqual(await q.get(), 6)
            self.assertEqual(await q.get(), 7)
            self.assertEqual(await q.get(), 8)

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_subscribe_to_addresses(self, mock_get):
        client = mock.MagicMock()
        sub_q = asyncio.Queue()

        client.subscribe.return_value = (do_nothing(6), sub_q)
        mock_get.return_value = do_nothing(client)

        async def _test():
            await sub_q.put(7)
            await sub_q.put(8)
            q = asyncio.Queue()
            await electrum.subscribe_to_addresses(
                ['bc1qmqyekxnf4xhxffv5fnlu387sggkhd5pw2w7g5tvtmjuar6ev6d6sld5pfl'],  # noqa: E501
                outq=q)

            # using an invalid address will cause these to block forever
            self.assertEqual(await q.get(), 6)
            self.assertEqual(await q.get(), 7)
            self.assertEqual(await q.get(), 8)

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_subscribe_to_address_bad_addr(self, mock_get):
        client = mock.MagicMock()
        mock_get.return_value = do_nothing(client)

        async def _test():
            q = asyncio.Queue()
            # we only want it to return. no assertions.
            await electrum.subscribe_to_address(
                address='1abc',  # noqa: E501
                outq=q)

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_subscribe_to_addresses_bad_addr(self, mock_get):
        client = mock.MagicMock()
        mock_get.return_value = do_nothing(client)

        async def _test():
            q = asyncio.Queue()
            # we only want it to return. no assertions.
            await electrum.subscribe_to_addresses(
                ['1abc'],  # noqa: E501
                outq=q)

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_get_unspents(self, mock_get):
        client = mock.MagicMock()
        client.RPC.return_value = \
            do_nothing('77')  # noqa: E501

        mock_get.return_value = do_nothing(client)

        async def _test():
            tx = await electrum.get_unspents('bc1qmqyekxnf4xhxffv5fnlu387sggkhd5pw2w7g5tvtmjuar6ev6d6sld5pfl')  # noqa: E501
            self.assertEqual(
                tx,
                '77')  # noqa: E501

            # NB: to test the [] case we have to make new awaitables
            mock_get.return_value = do_nothing(client)
            self.assertEqual(await electrum.get_unspents('00' * 32), [])

        self.loop.run_until_complete(_test())

    @mock.patch('zeta.electrum.electrum._get_client')
    def test_get_history(self, mock_get):
        client = mock.MagicMock()
        client.RPC.return_value = \
            do_nothing('77')  # noqa: E501

        mock_get.return_value = do_nothing(client)

        async def _test():
            tx = await electrum.get_history('bc1qmqyekxnf4xhxffv5fnlu387sggkhd5pw2w7g5tvtmjuar6ev6d6sld5pfl')  # noqa: E501
            self.assertEqual(
                tx,
                '77')  # noqa: E501

            # NB: to test the [] case we have to make new awaitables
            mock_get.return_value = do_nothing(client)
            self.assertEqual(await electrum.get_history('00' * 32), [])

        self.loop.run_until_complete(_test())


# EOF
