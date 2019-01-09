import asyncio

from typing import Any, Callable, Optional


def reverse_hex(h: str):
    return bytes.fromhex(h)[::-1].hex()


async def queue_printer(
        q: asyncio.Queue,
        transform: Optional[Callable[[Any], Any]] = None) -> None:  # pragma: nocover  # noqa: E501
    '''
    Prints a queue as entries come in
    Useful for debugging

    Args:
        q (asyncio.Queue): the queue to print
    '''
    print('registering printer')

    def do_nothing(k: Any) -> Any:
        return k
    t = transform if transform is not None else do_nothing
    while True:
        print(t(await q.get()))


async def queue_forwarder(
        inq: asyncio.Queue,
        outq: asyncio.Queue,
        transform: Optional[Callable[[Any], Any]] = None) -> None:  # pragma: nocover  # noqa: E501
    '''
    Forwards everything from a queue to another queue
    Useful for combining queues

    Args:
        inq  (asyncio.Queue): input queue
        outq (asyncio.Queue): output queue
        transform (function): A function to transform the q items with

    '''
    def do_nothing(k: Any) -> Any:
        return k
    t = transform if transform is not None else do_nothing
    while True:
        msg = await inq.get()
        await outq.put(t(msg))
