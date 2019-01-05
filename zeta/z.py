import asyncio

from zeta.db import headers
from zeta.sync import chain
from zeta import crypto, utils

from typing import Optional


async def _status_updater() -> None:
    '''
    Prints stats about the heaviest (best) block every 10 seconds
    '''
    # wait a few seconds in case we're in bootup
    await asyncio.sleep(5)

    best = None
    while True:
        heaviest = headers.find_heaviest()

        # it'd be very strange if this failed
        # but I put in the check, which implies that it happened in testing
        if len(heaviest) != 0:
            if best and heaviest[0]['height'] > best['height']:
                print('chain tip advanced {} blocks'.format(
                    heaviest[0]['height'] - best['height']
                ))
            best = heaviest[0]
            print('Best Block: {} at {} with {} work'.format(
                best['hash'],
                best['height'],
                best['accumulated_work']
            ))
        await asyncio.sleep(15)


async def _report_new_headers() -> None:
    # print header hashes as they come in
    def make_block_hash(header_dict):
        # print the header hash in a human-readable format
        return('new header: {}'.format(
            crypto.hash256(bytes.fromhex(header_dict['hex']))[::-1].hex()))
    asyncio.ensure_future(utils.queue_printer(header_q, make_block_hash))


async def zeta(header_q: Optional[asyncio.Queue] = None) -> None:
    '''
    Main function. Starts the various tasks
    TODO: keep references to the tasks, and monitor them
          gracefully shut down conections and the DB
    '''
    asyncio.ensure_future(chain.sync(header_q))


if __name__ == '__main__':
    # start tracking
    header_q: asyncio.Queue = asyncio.Queue()
    asyncio.ensure_future(zeta(header_q))

    # wait a few seconds then start the status updater
    asyncio.ensure_future(_status_updater())
    asyncio.ensure_future(_report_new_headers())

    asyncio.get_event_loop().run_forever()
