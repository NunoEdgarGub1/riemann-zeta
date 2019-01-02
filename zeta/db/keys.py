import sqlite3

from zeta.db import connection

from typing import cast, Optional, List
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


def find_by_address(address: str) -> Optional[KeyEntry]:
    '''
    finds a key by its primary address
    its primary address is the bech32 p2wpkh of its compressed pubkey
    '''
    c = connection.get_cursor()
    try:
        res = [key_from_row(r) for r in c.execute(
            '''
            SELECT * FROM keys
            WHERE address = :address
            ''',
            {'address': address})]
        for a in res:
            # little hacky. returns first entry
            # we know there can only be one
            return key_from_row(a)
        return None
    finally:
        c.close()


def find_by_pubkey(pubkey: str) -> List[KeyEntry]:
    '''
    finds a key by its pubkey
    '''
    c = connection.get_cursor()
    try:
        res = [key_from_row(r) for r in c.execute(
            '''
            SELECT * FROM keys
            WHERE pubkey = :pubkey
            ''',
            {'pubkey': pubkey})]
        return res
    finally:
        c.close()


def find_by_script(script: bytes) -> List[KeyEntry]:
    c = connection.get_cursor()
    try:
        res = [key_from_row(r) for r in c.execute(
            '''
            SELECT * FROM keys
            WHERE pubkey IN
                (SELECT pubkey FROM pubkey_to_script
                 WHERE script = :script)
            ''',
            {'script': script})]
        return res
    finally:
        c.close()
