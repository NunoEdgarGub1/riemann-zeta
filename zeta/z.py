import asyncio

from zeta import checkpoint, electrum, connection, headers

from typing import cast


async def track_chain_tip() -> None:
    q = asyncio.Queue()
    await electrum.subscribe_to_headers(q)
    asyncio.ensure_future(header_queue_handler(q))


async def catch_up(from_height: int) -> None:
    electrum_response = await electrum.get_headers(from_height, 2016)
    if electrum_response['count'] == 2016:
        asyncio.ensure_future(catch_up(from_height + 2014))
    process_header_batch(electrum_response['hex'])


async def maintain_db() -> None:
    while True:
        await asyncio.sleep(60)
        floating = headers.find_by_height(0)
        # NB: this will attempt to find their parent and fill in height/accdiff
        for header in floating:
            headers.store_header(floating)


async def status_updater() -> None:
    best = None
    while True:
        heaviest = headers.find_heaviest()
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
        await asyncio.sleep(10)


def process_header_batch(electrum_hex) -> None:
    blob = bytes.fromhex(electrum_hex)
    header_list = [blob[i:i+80].hex() for i in range(0, len(blob), 80)]
    headers.batch_store_header(header_list)


async def header_queue_handler(q: asyncio.Queue) -> None:
    while True:
        header = await q.get()
        print('got header in queue')

        # NB: the initial result and subsequent notifications are inconsistent
        try:
            hex_header = header[0]['hex']
        except Exception:
            hex_header = header['hex']
        print(hex_header)
        headers.store_header(hex_header)


def initial_setup() -> int:
    '''
    Ensures the database directory exists, and tables exist
    '''
    connection.ensure_directory()
    connection.ensure_tables()

    latest_checkpoint = max(checkpoint.CHECKPOINTS, key=lambda k: k['height'])

    headers.store_header(latest_checkpoint)
    return cast(int, headers.find_highest()[0]['height'])


async def zeta() -> None:
    last_known_height = initial_setup()
    # NB: assume there hasn't been a 10 block reorg
    asyncio.ensure_future(track_chain_tip())
    asyncio.ensure_future(catch_up(last_known_height))
    asyncio.ensure_future(maintain_db())
    asyncio.ensure_future(status_updater())


if __name__ == '__main__':
    asyncio.ensure_future(zeta())
    asyncio.get_event_loop().run_forever()
