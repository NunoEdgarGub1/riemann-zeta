import random
import asyncio

from zeta import utils
from zeta.electrum import servers

from connectrum.svr_info import ServerInfo
from connectrum.client import StratumClient
from connectrum import ElectrumErrorResponse

from typing import Any, Awaitable, List, Tuple


class MetaClient():

    def __init__(self):
        self._clients = []
        self._servers = []
        self.protocol_version = "1.2"
        self.user_agent = 'zeta'

        self._num_clients = 2
        self._random_set_size = 2
        self._timeout_seconds = 5

    async def _keepalive(self, c: StratumClient) -> None:
        while True:
            await asyncio.sleep(100)
            try:
                await c.RPC('server.ping')
            except Exception:
                self._clients = list(filter(lambda k: k != c, self._clients))
                break  # exit the loop at the first error

    async def setup_connections(self) -> None:
        while len(self._clients) < self._num_clients:
            self._clients.append(await self.new_client())

    def _get_server_info(self) -> ServerInfo:
        '''
        Selects a server randomly from the list
        Filters onions, and other protocol versions

        Returns:
            (ServerInfo): the selected server
        '''
        s = filter(lambda k: k not in self._servers, servers.SERVERS)
        s = filter(lambda k: 'onion' not in k['hostname'], s)
        s = filter(lambda k: k['version'] == self.protocol_version, s)
        server = random.choice(list(s))
        return ServerInfo(server)

    async def new_client(self) -> StratumClient:
        while True:
            try:
                server = self._get_server_info()

                client = StratumClient()

                await asyncio.wait_for(
                    client.connect(
                        server_info=server,
                        proto_code='s',
                        use_tor=False,
                        disable_cert_verify=True),
                    timeout=self._timeout_seconds)

                await asyncio.wait_for(
                    client.RPC(
                        'server.version',
                        self.user_agent,
                        self.protocol_version),
                    timeout=self._timeout_seconds)

                asyncio.ensure_future(self._keepalive(client))
                self._servers.append(str(server))
                return client

            except Exception as e:
                print('failed:', server)
                print(e, str(e))
                # fall back to top of loop and try a new server
                pass

    async def _aggregate_results(self, coros: List[Awaitable[Any]]) -> Any:
        '''
        Takes an array of awaitables, returns the most common result
        '''
        res = await asyncio.gather(*coros, return_exceptions=True)
        res = list(filter(lambda k: type(k) is not ElectrumErrorResponse, res))
        if len(res) != 0:
            res = max(res, key=res.count)
            if issubclass(type(res), Exception):
                raise res
            else:
                return res
        return None

    async def RPC(self, *args: Any) -> Any:
        '''
        Calls an electrum RPC on multiple clients
        '''
        client_set = random.choices(self._clients, k=self._random_set_size)
        coros = [c.RPC(*args) for c in client_set]
        return await self._aggregate_results(coros)

    def subscribe(self, *args) -> Tuple[Awaitable, asyncio.Queue]:
        q: asyncio.Queue = asyncio.Queue()

        client_set = random.choices(self._clients, k=self._random_set_size)
        futs_qs = [c.subscribe(*args) for c in client_set]

        futs = [k[0] for k in futs_qs]
        qs = [k[1] for k in futs_qs]

        fut = self._aggregate_results(futs)
        asyncio.ensure_future(self._aggregate_subs(qs, q))

        return fut, q

    async def _aggregate_subs(
            self,
            qs: List[asyncio.Queue],
            outq: asyncio.Queue) -> None:
        filter_queue: asyncio.Queue = asyncio.Queue()
        sent: List[Any] = []

        for q in qs:
            asyncio.ensure_future(utils.queue_forwarder(q, filter_queue))

        while True:
            msgs = [await filter_queue.get()]
            await asyncio.sleep(3)
            while not filter_queue.empty():
                msgs.append(filter_queue.get_nowait())
            if len(msgs) >= 1:
                msg = max(msgs, key=msgs.count)
                if msg not in sent:
                    sent.append(msg)
                    await outq.put(msg)
