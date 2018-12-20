from mypy_extensions import TypedDict


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
        'value': int,
        'address': str,
        'spent_at': int,
        'spent_by': str
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
