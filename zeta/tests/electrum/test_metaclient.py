import asyncio
import unittest
# from unittest import mock
from contextlib import suppress

from zeta.electrum import metaclient


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

    def test_init(self):
        m = metaclient.MetaClient()
        self.assertEqual(m._clients, [])
        self.assertEqual(m._servers, [])
        self.assertEqual(m.protocol_version, '1.2')
        self.assertEqual(m.user_agent, 'riemann-zeta')
        self.assertEqual(m._num_clients, 2)
        self.assertEqual(m._random_set_size, 2)
        self.assertEqual(m._timeout_seconds, 5)
