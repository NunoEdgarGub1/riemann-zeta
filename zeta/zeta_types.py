from mypy_extensions import TypedDict

from typing import List

Header = TypedDict(
    'Header',
    {
        'hash': str,
        'version': int,
        'prev_block': str,
        'merkle_root': str,
        'timestamp': int,
        'nbits': str,
        'nonce': str,
        'difficulty': int,
        'hex': str,
        'height': int,
        'accumulated_work': int
    }
)

Address = TypedDict(
    'Address',
    {
        'address': str,
        'script': bytes,
        'script_pubkeys': List[str]
    }
)

Outpoint = TypedDict(
    'Outpoint',
    {
        'tx_id': str,
        'index': int
    }
)

Prevout = TypedDict(
    'Prevout',
    {
        'outpoint': Outpoint,
        'tx_id': str,
        'idx': int,
        'value': int,
        'spent_at': int,
        'spent_by': str,
        'address': str
    }
)

KeyEntry = TypedDict(
    'KeyEntry',
    {
        'address': str,
        'privkey': bytes,
        'pubkey': bytes,
        'derivation': str,
        'chain': str
    }
)
