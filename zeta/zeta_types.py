from mypy_extensions import TypedDict

from typing import List, Optional

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

AddressEntry = TypedDict(
    'AddressEntry',
    {
        'address': str,
        'script': Optional[bytes],
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
        'pubkey': str,
        'derivation': str,
        'chain': str
    }
)

ElectrumGetHeadersResponse = TypedDict(
    'ElectrumGetHeadersResponse',
    {
        'count': int,
        'hex': str,
        'max': int
    }
)
