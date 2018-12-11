import asyncio

from zeta import utils
from zeta.electrum.metaclient import MetaClient

from typing import Dict, Optional, Union

_CLIENT: Optional[MetaClient] = None


async def _get_client() -> MetaClient:
    '''
    TODO: Improve
    Gets a singleton metaclient

    Returns:
        (zeta.electrum.metaclient.MetaClient): an Electrum metaclient
    '''
    global _CLIENT

    if _CLIENT is None:
        client = MetaClient()
        await client.setup_connections()
        _CLIENT = client
        return _CLIENT
    else:
        return _CLIENT


async def subscribe_to_headers(outq: asyncio.Queue) -> None:
    '''
    Subscribes to headers list. Forwards events to a queue
    Args:
        client   (StratumClient): Electrum server client
        address_list (list(str)): the addresses to subscribe to
        outq     (asyncio.Queue): a queue to route incoming events to
    '''
    client = await _get_client()
    fut, q = client.subscribe('blockchain.headers.subscribe', True)  # NB: raw
    await outq.put(await fut)
    asyncio.ensure_future(utils.queue_forwarder(q, outq))


async def get_headers(
        start_height: int,
        count: int) -> Dict[str, Union[str, int]]:
    '''Gets a set of headers from the Electrum server
    Args:
        start_height     (int): the height of the first header
        count            (int): the number of headers to retrieve
    Returns:
        (dict):
            "count": number of headers
            "hex": concatenated headers as hex
            "max": maximum number of headers server will return
    '''
    client = await _get_client()
    return await client.RPC('blockchain.block.headers', start_height, count)
