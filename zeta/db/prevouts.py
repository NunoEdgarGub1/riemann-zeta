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
            outpoint (str)
            tx_id (str)
            idx (int)
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
        address (str): address
    Returns:
        dict:
            outpoint    (str): tx_id and index
            tx_id       (str): tx id
            idx         (int): tx index
            value       (int): tx value in satoshis
            address     (str): address
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
        tx_id (str): tx id
    Returns:
        dict:
            outpoint    (str): tx_id and index
            tx_id       (str): tx id
            idx         (int): tx index
            value       (int): tx value in satoshis
            address     (str): address
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
        outpoint (str): tx_id and index
    Returns:
        dict:
            outpoint    (str): tx_id and index
            tx_id       (str): tx id
            idx         (int): tx index
            value       (int): tx value in satoshis
            address     (str): address
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


def find_unspents(tx_id: str) -> List[Prevout]:
    '''
    Find unspents by tx id.
    Args:
        tx_id (str): tx id
    Returns:
        dict:
            outpoint    (str): outpoint
            tx_id       (str): tx id
            idx         (int): tx index
            value       (int): tx value in satoshis
            address     (str): address
            spent_at    (int): block height tx was spent
            spent_by    (str): txid of spend tx
    '''
    c = connection.get_cursor()

    try:
        prevouts_by_tx_id = [prevout_from_row(r) for r in c.execute(
            '''
            SELECT * FROM prevouts
            WHERE tx_id  = :tx_id
            ''',
            {'tx_id': tx_id})]
        res = []
        for prevout in prevouts_by_tx_id:
            if prevout['spent_by'] is '':
                res.append(prevout)
        return res
    except Exception:
        raise
    finally:
        c.close()
