minimal chain tip tracking for simple light clients

## What is Zeta

Zeta is an ultra-minimal Bitcoin light client.


## What does Zeta do?

Zeta connects to Electrum servers, retrieves Bitcoin header information and stores it in a local DB. It maintains a connection to several electrum servers, and processes headers as they come in.

Zeta starts from a checkpoint, which is hardcoded. It ranks blocks by accumulated work from that checkpoint.


## Installation

```
pip install riemann-zeta
```

## Configuration

Yes, surprisingly.

```
export ZETA_DB_PATH="/absolute/path/to/db/directory"
export ZETA_DB_NAME="yourdb.name"
```


## Usage

### Command line (non-interactive, just syncs the db)
```
pipenv run python zeta/z.py
```

### Programmatically:
```python
import asyncio

from zeta import z, headers

asyncio.ensure_future(z.zeta())

# NB: Chain sync may take some time, depending on your checkpoint
#     You have to wait.

# returns a List of header dicts, heights are NOT (!!) unique
headers.find_by_height(595959)  
headers.find_highest()

# returns a List of header dicts. total difficulty is NOT (!!) unique
headers.find_heaviest()

# returns a header dict. hashes are unique
# at least, if they aren't, we have bigger problems than Zeta breaking
h = headers.find_by_hash("00000000000000000020ba2cdb900193eb8af323487a84621d45f2222e01f8c6")

print(h['height'])
print(h['merkle_root'])
print(h['hex'])
```


## Header Format

``` python
# https://blockstream.info/block/00000000000000000020ba2cdb900193eb8af323487a84621d45f2222e01f8c6
{  # It's a dict, not an object
    'hash': '00000000000000000020ba2cdb900193eb8af323487a84621d45f2222e01f8c6',
    'version': 536870912,
    'prev_block': '0000000000000000001cd1aec2e9e7e576a157c5d74f3e09af7f536924ca9891',
    'merkle_root': '4cdee1106ad3b739d66f29913efc71e4d087f7e7dbc4cf2b852532e078b43b1d',
    'timestamp': 1544487446,
    'nbits': '7cd93117',
    'nonce': 'af1c036e',
    'difficulty': 5646403851534,
    'hex': '000000209198ca2469537faf093e4fd7c557a176e5e7e9c2aed11c0000000000000000004cdee1106ad3b739d66f29913efc71e4d087f7e7dbc4cf2b852532e078b43b1d16020f5c7cd93117af1c036e',
    'height': 553333,  # will be 0 if the parent's height is unknown
    'accumulated_work': 303123758060231297  #  will be 0 if the parent's accumulated_work is unknown
}
```

## Development

```
pipenv install -d
```

### Running tests

This will run the linter, the type checker, and then the unit tests.

Provided anyone ever writes unit tests.

```
tox
```

## Infrequently asked questions

#### How is Zeta?

Very young and resource inefficient.

#### Why is Zeta?

Zeta is pure python, and has only 1 dependency (which is also pure python).

#### Why are the hardcoded servers and checkpoints in .py files?

Pyinstaller does not support pkg_resources. Putting them in .py files ensure they can be packaged in executables

#### What else?

Future plans:
1. Add some logic to check if the chain tip gets stuck (e.g. because of electrum errors)
1. Track prevouts in history and mempool
1. Implemnt merkle proof validation
1. Validate electrum scripthash messages against headers
