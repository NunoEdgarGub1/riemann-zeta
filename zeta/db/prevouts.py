import sqlite3

from riemann.encoding import addresses as addr
from riemann import utils as rutils

from zeta.db import connection
from zeta.zeta_types import Prevout

from typing import cast, List, Optional


def prevout_from_row(row: sqlite3.Row) -> Prevout:
    return cast(Prevout, dict((k, row[k]) for k in row.keys()))


def validate_prevout(prevout: Prevout) -> bool:
    idx_bytes = rutils.i2le_padded(prevout['idx'], 4)

    if prevout['outpoint'] != '{}{}'.format(prevout['tx_id'], idx_bytes.hex()):
        return False

    if prevout['value'] <= 0:
        return False

    try:
        addr.parse_hash(prevout['address'])
    except ValueError:
        return False

    return True


def store_prevout(prevout: Prevout) -> bool:
    '''
    Stores a prevout in the database
    Args:
        prevout (dict):
            Outpoint (dict)
            value (int)
            address (str)
            spent_at (str)
            spent_by (str)
    Return:
        (bool): true if successful, false if error
    '''
    c = connection.get_cursor()

    if not validate_prevout(prevout):
        return False

    try:
        c.execute(
            '''
            INSERT OR REPLACE INTO prevouts VALUES (
                :outpoint,
                :tx_id,
                :idx,
                :value,
                :spent_at,
                :spent_by,
                :address)
            ''',
            prevout)
        connection.commit()
        return True
    except Exception:
        return False
    finally:
        c.close()


def find_by_address(address: str) -> List[Prevout]:
    '''
    Finds prevouts by associated address.
    Args:
        address (str):
    Returns:
        dict:
            outpoint    (dict): Outpoint
            value       (int): tx value in satoshis
            address     (str):
            spent_at    (int): block height tx was spent
            spent_by    (str): txid of spend tx
    '''
    c = connection.get_cursor()

    try:
        return [prevout_from_row(r) for r in c.execute(
            '''
            SELECT * FROM prevouts
            WHERE address = :address
            ''',
            {'address': address})]
    except Exception:
        raise
    finally:
        c.close()


def find_by_tx_id(tx_id: str) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE tx_id = :tx_id
            ''',
            {'tx_id': tx_id}
        )]
        return res
    finally:
        c.close()


def find_by_outpoint(outpoint: str) -> Optional[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE outpoint = :outpoint
            ''',
            {'outpoint': outpoint}
        )]
        for p in res:
            # little hacky. returns first entry
            # we know there can only be one
            return p
        return None
    finally:
        c.close()


def find_all_unspents() -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE spent_at = -2
            '''
        )]
        return res
    finally:
        c.close()


def find_by_child(child_tx_id: str) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE spent_by = :child_tx_id
            ''',
            {'child_tx_id': child_tx_id}
        )]
        return res
    finally:
        c.close()


def find_by_value_range(
        lower_value: int,
        upper_value: int,
        unspents_only: bool = True) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        # I don't like this.
        # figure out how to do this without string format
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE value <= :upper_value
              AND value >= :lower_value
              AND spent_at {operator} -2
            '''.format(operator=('==' if unspents_only else '!=')),
            {'upper_value': upper_value,
             'lower_value': lower_value})]
        return res
    finally:
        c.close()
