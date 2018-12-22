import sqlite3

from riemann import utils as rutils
from riemann.encoding import addresses as addr
from riemann.script import serialization as script_ser

from zeta import utils
from zeta.db import connection

from zeta.zeta_types import AddressEntry
from typing import List, Union, Optional


def address_from_row(row: sqlite3.Row) -> AddressEntry:
    a: AddressEntry = {
        'address': row['address'],
        'script': row['script'],
        'script_pubkeys': pubkeys_from_script(row['script'])
    }
    return a


def validate_address(address: AddressEntry) -> bool:
    '''
    Validates the address data structure
    '''
    try:
        h = addr.parse_hash(address['address'])
        if address['script'] == '':
            return True

        if address['script_pubkeys'] != pubkeys_from_script(address['script']):
            return False

        if h in [rutils.sha256(address['script']),
                 rutils.hash160(address['script'])]:
            return True
    except ValueError:
        pass

    return False


def pubkeys_from_script(script: bytes) -> List[str]:
    '''
    guess-parses pubkeys from a serialized bitcoin script
    '''
    res: List[str] = []
    s = script_ser.deserialize(script)
    for token in s.split():
        if utils.is_pubkey(token):
            res.append(token)
    return res


def store_address(address: Union[str, AddressEntry]) -> bool:
    '''
    stores an address in the db
    accepts a string address
    '''
    a: AddressEntry

    if type(address) is str:
        a = {
            'address': address,
            'script': None,
            'script_pubkeys': []
        }
    else:
        a = address

    if not validate_address(a):
        return False

    c = connection.get_cursor()
    try:
        c.execute(
            '''
            INSERT OR REPLACE INTO addresses VALUE (
                :address
                :script)
            ''',
            a)

        # NB: we track what pubkeys show up in what scripts so we can search
        for pubkey in a['script_pubkeys']:
            c.execute(
                '''
                    INSERT OR REPLACE INTO pubkey_to_script VALUE (
                        :pubkey,
                        :script
                    )
                ''',
                {'pubkey': pubkey, 'script': a['script']})
        connection.commit()
        return True
    except Exception:
        return False
    finally:
        c.close()


def find_associated_pubkeys(script: bytes) -> List[str]:
    '''
    looks up pubkeys associated with a script
    somewhat redundant with pubkeys_from_script
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT pubkey from pubkey_to_script
            WHERE script = :script
            ''',
            {'script': script})
        return [r['pubkey'] for r in res]
    finally:
        c.close()


def find_by_address(address: str) -> Optional[AddressEntry]:
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT pubkey from addresses
            WHERE address = :address
            ''',
            {'script': address})
        if len(res) != 0:
            return address_from_row(res[0])
        return None
    finally:
        c.close()


def find_by_script(script: bytes) -> List[AddressEntry]:
    c = connection.get_cursor()
    try:
        res = [address_from_row(r) for r in c.execute(
            '''
            SELECT * FROM addresses
            WHERE script = :script
            ''',
            {'script': script})]
        return res
    finally:
        c.close()


def find_by_pubkey(pubkey: str) -> List[AddressEntry]:
    c = connection.get_cursor()
    try:
        res = [address_from_row(r) for r in c.execute(
            '''
            SELECT * FROM addresses
            WHERE pubkey = :pubkey
            ''',
            {'pubkey': pubkey})]
        return res
    finally:
        c.close()
