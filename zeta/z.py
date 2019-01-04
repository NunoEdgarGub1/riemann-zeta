import asyncio

from zeta.sync import chain


async def zeta(header_q: asyncio.Queue) -> None:
    '''
    Main function. Starts the various tasks
    TODO: keep references to the tasks, and monitor them
          gracefully shut down conections and the DB
    '''
    asyncio.ensure_future(chain.sync(header_q))


if __name__ == '__main__':
    # do the thing
    asyncio.ensure_future(zeta(asyncio.Queue()))
    asyncio.get_event_loop().run_forever()
