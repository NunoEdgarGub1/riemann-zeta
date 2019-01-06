import asyncio

from zeta import electrum
from zeta.db import addresses, headers, prevouts

from typing import Any, List, Optional
from zeta.zeta_types import Prevout


async def sync(outq: Optional[asyncio.Queue] = None) -> None:
    asyncio.ensure_future(_track_known_addresses(outq))
    asyncio.ensure_future(_maintain_db(outq))


async def _track_known_addresses(outq: Optional[asyncio.Queue]) -> None:
    '''
    Tracks known addresses
    Regularly queries the db to see if we've learned of new addresses
    '''
    tracked = []
    while True:
        # Find the addresses we know
        known_addrs = addresses.find_all_addresses()
        # Figure out which ones we aren't already tracking and track them
        untracked = list(filter(lambda a: a not in tracked, known_addrs))

        # record that we tracked each of them
        for addr in untracked:
            tracked.append(addr)
            asyncio.ensure_future(_sub_to_address(addr, outq))

        # wait 10 seconds and repeat
        await asyncio.sleep(10)


async def _sub_to_address(
        addr: List[str],
        outq: Optional[asyncio.Queue] = None) -> None:
    '''
    subs to address and registers a handler
    '''
    intermediate_q: asyncio.Queue = asyncio.Queue()
    await electrum.subscribe_to_address(addr, intermediate_q)

    asyncio.ensure_future(_address_sub_handler(addr, intermediate_q, outq))


async def _address_sub_handler(
        address: str,
        inq: asyncio.Queue,
        outq: Optional[asyncio.Queue]) -> None:
    while True:
        # wait for a subscription event
        # it contains no information, so we can discard it
        await inq.get()
        # update our view of the unspents
        asyncio.ensure_future(_get_address_unspents(address, outq))


async def _get_address_unspents(
        address: str,
        outq: Optional[asyncio.Queue] = None) -> None:
    '''
    Gets the unspents from an address, and stores them in the DB
    If an out queue is provided, it'll push new prevouts to the queue
    '''
    unspents = await electrum.get_unspents(address)
    prevout_list = _parse_electrum_unspents(unspents, address)
    elec_outpoints = [p['outpoint'] for p in prevout_list]

    # see if we know of any
    known_prevouts = prevouts.find_by_address(address)
    known_outpoints = [p['outpoint'] for p in known_prevouts]

    # filter any we already know about
    new_prevouts = list(filter(
        lambda p: p['outpoint'] not in known_outpoints,
        prevout_list))

    # NB: spent_at is -2 if we think it's unspent
    #     this checks that we think unspent, but electrum thinks spent
    recently_spent = list(filter(
        lambda p: p['spent_at'] == -2 and p['outpoint'] not in elec_outpoints,
        known_prevouts))

    # send new ones to the outq if present
    if outq is not None:
        for prevout in new_prevouts:
            await outq.put(prevout)

    # store new ones in the db
    prevouts.batch_store_prevout(new_prevouts)

    # check on those recently spent
    asyncio.ensure_future(_update_recently_spent(
        address=address,
        recently_spent=recently_spent,
        outq=outq))


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


async def _update_recently_spent(
        address: str,
        recently_spent: List[Prevout],
        outq: Optional[asyncio.Queue]) -> None:
    '''
    Gets the address history from electrum
    Updates our recently spent
    '''
    # NB: Zeta does NOT use the same height semantics as Electrum
    #     Electrum uses 0 for mempool and -1 for parent unconfirmed
    #     Zeta uses -1 for mempool and -2 for no known spending tx
    # NB: defaulting to empty list accounts for the case where history is None,
    #     which will happen if we get no electrum response
    if len(recently_spent) == 0:
        return

    history: Optional[List[Any]] = await electrum.get_history(address)
    if history is None:
        history = []

    # Go through each tx in the history, start with the latest
    for item in history[::-1]:
        tx = await electrum.get_tx_verbose(item['tx_hash'])
        # determine which outpoints it spent
        spent_outpoints = [
            {'tx_id': txin['txid'], 'index': txin['vout']}
            for txin in tx['vin']]
        # TODO: make this less of a nested-if mess
        # check each prevout in our recently_spent to see which tx spent it
        for prevout in recently_spent:
            if prevout['outpoint'] in spent_outpoints:
                # if the TX spent our prevout, get its hash for spent_by
                # and its block height for spent_at
                prevout['spent_by'] = tx['hash']
                if 'blockhash' not in tx:
                    # it's in the mempool right now
                    prevout['spent_at'] = -1
                    if outq is not None:
                        await outq.put(prevout)
                elif 'blockhash' in tx:
                    header = headers.find_by_hash(tx['blockhash'])
                    if header is not None:
                        # we found its header
                        prevout['spent_at'] = header['height']
                        if outq is not None:
                            await outq.put(prevout)
                    else:
                        # we don't know its header, toss it back for later
                        prevout['spent_at'] = -2

                # we have assigned a spent_by and height. write it to the db.
                prevouts.store_prevout(prevout)


async def _maintain_db(
        outq: Optional[asyncio.Queue] = None) -> None:
    '''
    Starts any db maintenance tasks we want
    '''
    asyncio.ensure_future(_update_children_in_mempool(outq))
    ...  # TODO: What more here?


async def _update_children_in_mempool(
        outq: Optional[asyncio.Queue] = None) -> None:
    '''
    Periodically checks the DB for mempool txns that spend our prevouts
    If the txn has moved from the mempool and been confirmed 10x we update it
    '''
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
                if outq is not None:
                    await outq.put(prevout)
                continue

            # NB: we'll accept 10 confirmations as VERY unlikely to roll back
            #     if it has 10+ confs, update its `spent_at` and store
            #     we should also notify the frontend that we found it
            if tx_details['confirmations'] >= 10:
                confirming = headers.find_by_hash(tx_details['blockhash'])
                prevout['spent_at'] = confirming['height']
                prevouts.store_prevout(prevout)
                if outq is not None:
                    await outq.put(prevout)
                continue

        # run again in 10 minutes
        await asyncio.sleep(600)
