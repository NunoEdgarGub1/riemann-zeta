import sqlite3

from typing import cast
from zeta.zeta_types import KeyEntry


def key_from_row(row: sqlite3.Row) -> KeyEntry:
    '''
    Does what it says on the tin
    '''
    return cast(KeyEntry, dict(zip(row.keys(), row)))


def store_key(k: KeyEntry) -> bool:
    ...


def validate_key(k: KeyEntry) -> bool:
    ...


def find_by_address(address: str) -> KeyEntry:
    ...
