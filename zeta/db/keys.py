import sqlite3

from zeta import utils
from zeta.db import connection

from riemann.encoding import addresses as addr

from typing import cast, Optional, List
from zeta.zeta_types import KeyEntry


def key_from_row(row: sqlite3.Row, secret_phrase: str) -> KeyEntry:
    '''
    Does what it says on the tin
    '''

    privkey = utils.decode_aes(row['privkey'], secret_phrase)

    res = cast(KeyEntry, dict((k, row[k]) for k in row.keys()))
    res['privkey'] = privkey
    return res


def store_key(key_entry: KeyEntry, secret_phrase: str) -> bool:
    if not validate_key(key_entry):
        return False

    k = key_entry.copy()

    k['privkey'] = utils.encode_aes(k['privkey'], 'secret_phrase')

    c = connection.get_cursor()
    try:
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


def validate_key(k: KeyEntry) -> bool:
    '''
    Checks internal consistency of a key entry
    '''
    # pubkey is malformatted
    if not utils.is_pubkey(k['pubkey']):
        return False

    # pubkey matches privkey
    if k['pubkey'] != utils.to_pubkey(utils.coerce_key(k['privkey'])).hex():
        return False

    # address matches pubkey
    if k['address'] != addr.make_p2wpkh_address(bytes.fromhex(k['pubkey'])):
        return False

    return True


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
    '''
    Finds all KeyEntries whose pubkey appears in a certain script
    '''
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
