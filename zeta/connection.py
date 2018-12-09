import os
import sys
import sqlite3


def ensure_directory() -> None:
    '''
    Creates the summa/bidder data directory if it does not already exist
    '''
    if not os.path.exists(PATH):
        os.makedirs(PATH)


if sys.platform.startswith('win'):
    PATH_ROOT = os.path.expandvars(r'%LOCALAPPDATA%')
else:
    PATH_ROOT = os.path.expanduser('~')

PATH = os.path.join(PATH_ROOT, '.summa', 'zeta')

ensure_directory()

DB_PBKDF_SALT = b'summa-riemann-zeta'
PBKDF_ITERATIONS = 100000

DB_NAME = 'zeta.db'
DB_PATH = os.path.join(PATH, DB_NAME)

CONN = sqlite3.connect(DB_PATH)
CONN.row_factory = sqlite3.Row


def commit():
    return CONN.commit()


def get_cursor() -> sqlite3.Cursor:
    return CONN.cursor()


def ensure_tables() -> bool:
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
