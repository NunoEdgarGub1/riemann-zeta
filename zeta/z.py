import asyncio

from zeta.sync import chain

from typing import Optional


async def zeta(header_q: Optional[asyncio.Queue] = None) -> None:
    '''
    Main function. Starts the various tasks
    TODO: keep references to the tasks, and monitor them
          gracefully shut down conections and the DB
    '''
    asyncio.ensure_future(chain.sync(header_q))


if __name__ == '__main__':
    # do the thing
    asyncio.ensure_future(zeta())
    asyncio.get_event_loop().run_forever()
