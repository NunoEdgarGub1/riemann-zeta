import sqlite3

from zeta import crypto
from zeta.db import connection

from riemann.encoding import addresses as addr

from typing import cast, Optional, List
from zeta.zeta_types import KeyEntry


def key_from_row(row: sqlite3.Row, secret_phrase: str) -> KeyEntry:
    '''
    Does what it says on the tin
    '''

    privkey = crypto.decode_aes(row['privkey'], secret_phrase)

    res = cast(KeyEntry, dict((k, row[k]) for k in row.keys()))
    res['privkey'] = privkey
    return res


def validate_key(k: KeyEntry) -> bool:
    '''
    Checks internal consistency of a key entry
    '''
    # missing expected keys, prevents runtime errors later in this method
    if set(['pubkey', 'privkey', 'address']) - set(k.keys()) != set():
        return False

    # pubkey is malformatted
    if not crypto.is_pubkey(k['pubkey']):
        return False

    # pubkey matches privkey
    if k['pubkey'] != crypto.to_pubkey(crypto.coerce_key(k['privkey'])).hex():
        return False

    # address matches pubkey
    if k['address'] != addr.make_p2wpkh_address(bytes.fromhex(k['pubkey'])):
        return False

    return True


def store_key(key_entry: KeyEntry, secret_phrase: str) -> bool:
    if not validate_key(key_entry):
        return False

    k = key_entry.copy()  # type: ignore

    c = connection.get_cursor()
    try:
        k['privkey'] = crypto.encode_aes(k['privkey'], secret_phrase)
        c.execute(
            '''
            INSERT OR IGNORE INTO addresses VALUES (
                :address,
                :script)
            ''',
            {'address': k['address'], 'script': b''})
        c.execute(
            '''
            INSERT OR REPLACE INTO keys VALUES (
                :pubkey,
                :privkey,
                :derivation,
                :chain,
                :address)
            ''',
            k)
        connection.commit()
        return True
    except Exception:
        return False
    finally:
        c.close()


def find_by_address(address: str, secret_phrase: str) -> Optional[KeyEntry]:
    '''
    finds a key by its primary address
    its primary address is the bech32 p2wpkh of its compressed pubkey
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT * FROM keys
            WHERE address = :address
            ''',
            {'address': address})
        for a in res:
            # little hacky. returns first entry
            # we know there can only be one
            return key_from_row(a, secret_phrase)
        return None
    finally:
        c.close()


def find_by_pubkey(pubkey: str, secret_phrase: str) -> List[KeyEntry]:
    '''
    finds a key by its pubkey
    '''
    c = connection.get_cursor()
    try:
        res = [key_from_row(r, secret_phrase) for r in c.execute(
            '''
            SELECT * FROM keys
            WHERE pubkey = :pubkey
            ''',
            {'pubkey': pubkey})]
        return res
    finally:
        c.close()


def find_by_script(script: bytes, secret_phrase: str) -> List[KeyEntry]:
    '''
    Finds all KeyEntries whose pubkey appears in a certain script
    '''
    c = connection.get_cursor()
    try:
        res = [key_from_row(r, secret_phrase) for r in c.execute(
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
