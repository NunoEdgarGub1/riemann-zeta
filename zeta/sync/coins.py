import asyncio

from zeta import electrum  # , utils
from zeta.db import addresses, headers, prevouts

from typing import Any, List, Optional
from zeta.zeta_types import Prevout


async def sync(outq: Optional[asyncio.Queue] = None) -> None:
    asyncio.ensure_future(_track_known_addresses(outq))


async def _track_known_addresses(outq: Optional[asyncio.Queue]) -> None:
    addrs_to_track = addresses.find_all_addresses()
    for addr in addrs_to_track:
        asyncio.ensure_future(_get_address_unspents(addr, outq))
        asyncio.ensure_future(_sub_to_address(addr, outq))


async def _sub_to_address(
        addr: str,
        outq: Optional[asyncio.Queue] = None) -> None:
    ...


async def _address_sub_handler(
        inq: asyncio.Queue,
        outq: Optional[asyncio.Queue]) -> None:
    ...


async def _get_address_unspents(
        address: str,
        outq: Optional[asyncio.Queue] = None) -> None:
    '''
    Gets the unspents from an address, and stores them in the DB
    If an out queue is provided, it'll push new prevouts to the queue
    '''
    unspents = await electrum.get_unspents(address)
    prevout_list = _parse_electrum_unspents(unspents, address)

    # see if we know of any
    known_outpoints = prevouts.check_for_known_outpoints(
        [p['outpoint'] for p in prevout_list])

    # filter any we already know about
    prevout_list = list(filter(lambda p: p['outpoint'] not in known_outpoints))

    # send new ones to the outq if present
    if outq is not None:
        for prevout in prevout_list:
            await outq.put(prevout)

    # store new ones in the db
    prevouts.batch_store_prevout(prevout_list)


def _parse_electrum_unspents(
        unspents: List[Any],
        address: str) -> List[Prevout]:
    '''
    Parses Prevouts from the electrum unspent response
    Args:
        unspents (list(dict)): the electrum response
        address         (str): the address associated with the prevout
    Returns:
        (list(Prevout)): the parsed Prevouts
    '''
    prevouts: List[Prevout] = []
    for unspent in unspents:
        prevout: Prevout = {
            'outpoint': {
                'tx_id': unspent['tx_hash'],
                'index': unspent['tx_pos']
            },
            'value': unspent['value'],
            'address': address,
            'spent_at': -2,
            'spent_by': ''
        }
        prevouts.append(prevout)
    return prevouts


async def _maintain_db() -> None:
    asyncio.ensure_future(_update_children_in_mempool())
    ...


async def _update_children_in_mempool() -> None:
    while True:
        # NB: sleep at the end so that this runs once at startup

        # find all the prevouts that claim to be spent by a tx in the mempool
        child_in_mempool = prevouts.find_spent_by_mempool_tx()

        for prevout in child_in_mempool:
            # ask the electrum servers for tx info
            tx_details = await electrum.get_tx_verbose(prevout['spent_by'])

            # NB: if we don't get tx info back, that means the tx was evicted
            #     from the mempool, we should update the prevout to unspent
            if tx_details is None:
                prevout['spent_at'] = -2
                prevout['spent_by'] = ''
                prevouts.store_prevout(prevout)
                continue

            # NB: we'll accept 10 confirmations as VERY unlikely to roll back
            #     If it has 10+ confs, update its `spent_at` and store
            if tx_details['confirmations'] >= 10:
                confirming = headers.find_by_hash(tx_details['blockhash'])
                prevout['spent_at'] = confirming['height']
                prevouts.store_prevout[prevout]
                continue

        asyncio.sleep(600)
