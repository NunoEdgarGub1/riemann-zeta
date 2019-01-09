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

AddressEntry = TypedDict(
    'AddressEntry',
    {
        'address': str,
        'script': bytes,  # the redeem script for p2sh/p2wsh
        'script_pubkeys': List[str]  # parsed pubkeys in the redeem script
    }
)

Outpoint = TypedDict(
    'Outpoint',
    {
        'tx_id': str,  # block explorer format
        'index': int
    }
)

Prevout = TypedDict(
    'Prevout',
    {
        'outpoint': Outpoint,
        'value': int,  # in satoshi
        'spent_at': int,  # block height
        'spent_by': str,  # txid
        'address': str
    }
)

PrevoutEntry = TypedDict(  # the DB formatted prevout
    'PrevoutEntry',
    {
        'outpoint': str,  # tx serialization format
        'tx_id': str,  # block explorers
        'idx': int,
        'value': int,  # in sat
        'spent_at': int,  # block height
        'spent_by': str,  # txid
        'address': str
    }
)

KeyEntry = TypedDict(
    'KeyEntry',
    {
        'address': str,
        'privkey': bytes,  # encrypted when in the DB
        'pubkey': str,
        'derivation': str,
        'chain': str  # deprecated
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
