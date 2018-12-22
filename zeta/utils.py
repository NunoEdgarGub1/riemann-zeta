import asyncio

from typing import Any, Callable, Optional


async def queue_forwarder(
        inq: asyncio.Queue,
        outq: asyncio.Queue,
        transform: Optional[Callable[[Any], Any]] = None) -> None:
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


def is_pubkey(p: str) -> bool:
    '''
    determines if a string can be interpreted as btc hex formatted pubkey
    '''
    prefix = p[0:2]
    try:
        bytes.fromhex(p)
    except ValueError:
        return False
    if len(p) == 66:   # compressed
        return prefix in ['02', '03']
    if len(p) == 130:  # uncompressed
        return prefix == '04'
    return False
