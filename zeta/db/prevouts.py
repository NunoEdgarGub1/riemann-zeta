import sqlite3
from zeta.db import connection
from zeta.zeta_types import Prevout

from typing import cast, List


def prevout_from_row(row: sqlite3.Row) -> Prevout:
    return cast(Prevout, dict((k, row[k]) for k in row.keys()))


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
                :address
            )
            ''',
            (prevout))
        connection.commit()
        return True
    except Exception:
        raise
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


def find_by_txid(tx_id: str) -> List[Prevout]:
    '''
    Finds prevouts by associated txid.
    Args:
        tx_id (str):
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
            WHERE tx_id = :tx_id
            ''',
            {'tx_id': tx_id})]
    except Exception:
        raise
    finally:
        c.close()


def find_by_outpoint(outpoint: str) -> List[Prevout]:
    '''
    Finds prevouts by associated outpoint.
    Args:
        outpoint (str):
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
            WHERE outpoint = :outpoint
            ''',
            {'outpoint': outpoint})]
    except Exception:
        raise
    finally:
        c.close()


def find_unspents(txid: str) -> List[Prevout]:
    ...
