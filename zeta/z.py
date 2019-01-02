import asyncio

from zeta.sync import headers


async def zeta() -> None:
    '''
    Main function. Starts the various tasks
    TODO: keep references to the tasks, and monitor them
          gracefully shut down conections and the DB
    '''
    asyncio.ensure_future(headers.sync())


if __name__ == '__main__':
    # do the thing
    asyncio.ensure_future(zeta())
    asyncio.get_event_loop().run_forever()
