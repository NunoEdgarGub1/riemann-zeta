import os
import sys
import sqlite3


# TODO: Clean all this up and make better

def ensure_directory(p) -> None:
    '''
    Creates the PATH data directory if it does not already exist
    '''
    if not os.path.exists(p):
        os.makedirs(p)


if sys.platform.startswith('win'):
    PATH_ROOT = os.path.expandvars(r'%LOCALAPPDATA%')
else:
    PATH_ROOT = os.path.expanduser('~')

DEFAULT_PATH = os.path.join(PATH_ROOT, '.summa', 'zeta')

# Prefer the env variables
PATH = os.environ.get('ZETA_DB_PATH', DEFAULT_PATH)
DB_NAME = os.environ.get('ZETA_DB_NAME', 'zeta.db')

# Set the path and make sure it exists
DB_PATH = os.path.join(PATH, DB_NAME)
ensure_directory(PATH)

CONN = sqlite3.connect(DB_PATH)
CONN.row_factory = sqlite3.Row


def commit():
    return CONN.commit()


def get_cursor() -> sqlite3.Cursor:
    return CONN.cursor()


def ensure_tables() -> bool:
    '''

    Returns:
        (bool): true if table exists/was created, false if there's an exception
    '''
    c = get_cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS headers(
                hash TEXT PRIMARY KEY,
                version INTEGER,
                prev_block TEXT,
                merkle_root TEXT,
                timestamp INTEGER,
                nbits TEXT,
                nonce TEXT,
                difficulty INTEGER,
                hex TEXT,
                height INTEGER,
                accumulated_work INTEGER)
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS addresses(
                address TEXT PRIMARY KEY,
                script BLOB NOT NULL DEFAULT (x''))
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pubkey_to_script(
                pubkey TEXT,
                script BLOB,
                FOREIGN KEY(script) REFERENCES addresses(script))
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS keys(
                pubkey TEXT PRIMARY KEY,
                privkey BLOB,
                derivation TEXT NOT NULL DEFAULT '',
                chain TEXT NOT NULL DEFAULT 'btc',
                address TEXT,
                FOREIGN KEY(address) REFERENCES addresses(address))
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prevouts(
                outpoint TEXT PRIMARY KEY,
                tx_id TEXT,
                idx INTEGER,
                value INTEGER,
                spent_at INTEGER NOT NULL DEFAULT -2,
                spent_by TEXT NOT NULL DEFAULT '',
                address TEXT,
                FOREIGN KEY(address) REFERENCES addresses(address))
            ''')  # default -2 for not yet spent. electrum uses -1 for mempool

        commit()
        return True
    except Exception as e:
        print(e, str(e))
        return False
    finally:
        c.close()


def print_tables() -> None:
    c = get_cursor()
    res = c.execute('''
       SELECT name FROM sqlite_master WHERE type="table"
       ''')
    print([a for row in res for a in row])
