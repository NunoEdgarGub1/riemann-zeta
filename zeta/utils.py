import asyncio

from mypy_extensions import TypedDict
from typing import Any, Callable, Optional


# Header = Dict[str, Union[str, int]]

Header = TypedDict(
    'Header',
    {
        'hash': str,
        'version': int,
        'prev_block': str,
        'merkle_root': str,
        'timestamp': int,
        'nbits': str,
        'nonce': str,
        'difficulty': int,
        'hex': str,
        'height': int,
        'accumulated_work': int
    }
)


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
