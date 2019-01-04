import asyncio

from riemann import tx

from zeta import utils
from zeta.electrum import eutils
from zeta.electrum.metaclient import MetaClient

from typing import Any, Dict, List, Optional
from zeta.zeta_types import ElectrumGetHeadersResponse

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
        outq     (asyncio.Queue): a queue to route incoming events to
    '''
    client = await _get_client()
    fut, q = client.subscribe('blockchain.headers.subscribe', True)  # NB: raw
    await outq.put(await fut)
    asyncio.ensure_future(utils.queue_forwarder(q, outq))


async def get_headers(
        start_height: int,
        count: int) -> ElectrumGetHeadersResponse:
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


async def get_tx(tx_id: str) -> Optional[tx.Tx]:
    '''
    Args:
        tx_id (str): hex tx_id of tx to get
    Returns:
        (riemann.tx.Tx): the deserialized transaction
    '''
    client = await _get_client()
    tx_res = await client.RPC('blockchain.transaction.get', tx_id)
    if tx_res:
        return tx.Tx.from_hex(tx_res)
    else:
        return None


async def get_tx_verbose(tx_id: str) -> Optional[Dict[str, Any]]:
    '''
    Args:
        tx_id (str): hex tx_id of tx to get
    Returns:
        (dict): the deserialized transaction
    '''
    client = await _get_client()
    tx_res = await client.RPC('blockchain.transaction.get', tx_id, True)
    if tx_res:
        return tx_res
    else:
        return None


async def subscribe_to_addresses(
        address_list: List[str],
        outq: asyncio.Queue) -> None:
    '''
    Subscribes to a list of addresses. Forwards events to a provided queue
    NB: Subscribing only triggers notification of updates
        It does NOT give any info about what the update is :(

    Args:
        client   (StratumClient): Electrum server client
        address_list (list(str)): the addresses to subscribe to
        outq     (asyncio.Queue): a queue to route incoming events to
    '''
    client = await _get_client()
    for address in address_list:
        try:
            sh = eutils.address_to_electrum_scripthash(address)
            fut, q = client.subscribe('blockchain.scripthash.subscribe', sh)
            await outq.put(await fut)
            asyncio.ensure_future(utils.queue_forwarder(q, outq))
        except ValueError:
            continue


async def get_unspents(address: str) -> List[Dict[str, Any]]:
    '''
    Args:
        address          (str): the address to check
    Returns:
        (list(dict)): tx_hash (BE), tx_pos, height, value
    '''
    client = await _get_client()
    try:
        sh = eutils.address_to_electrum_scripthash(address)
        return await client.RPC('blockchain.scripthash.listunspent', sh)
    except ValueError:
        return []


async def get_history(address: str) -> List[Dict[str, Any]]:
    '''
    Args:
        address          (str): the address to check
    Returns:
        (list(dict)): tx_hash (BE), height, fee
    '''
    client = await _get_client()
    try:
        sh = eutils.address_to_electrum_scripthash(address)
        return await client.RPC('blockchain.scripthash.get_history', sh)
    except ValueError:
        return []
