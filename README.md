minimal chain tip tracking for simple light clients

## What is Zeta

Zeta is an ultra-minimal Bitcoin light client.


## What does Zeta do?

Zeta connects to Electrum servers, retrieves Bitcoin header information and stores it in a local DB. It maintains a connection to several electrum servers, and processes headers as they come in.

Zeta starts from a checkpoint, which are hardcoded. It ranks blocks by accumulated work from that checkpoint. We will eventually support specifying your own checkpoints.


## Installation

```
$ pip install riemann-zeta
```

## Configuration

Yes, surprisingly. We have two configuration environment variables.
Make sure they're set BEFORE you import zeta.

```
$ export ZETA_DB_PATH="/absolute/path/to/db/directory"
$ export ZETA_DB_NAME="yourdb.name"
```

## Usage

### Command line (non-interactive, just syncs the db)
```
$ pipenv run python zeta/z.py
```

### Programmatically:
```python
import asyncio

from zeta import z
from zeta.db import headers

async def use_zeta():

    # if you pass in a queue, you can get access to the electrum subscription
    header_q = asyncio.Queue()
    asyncio.ensure_future(z.zeta(header_q=header_q))

    # NB: Chain sync may take some time, depending on your checkpoint
    #     You have to wait.

    asyncio.sleep(60)

    # NB : returns a List of header dicts, heights are NOT (!!) unique
    #      we store ALL HEADERS we hear of, including orphans
    headers.find_by_height(595959)  
    headers.find_highest()

    # NB: returns a List of header dicts. total difficulty is NOT (!!) unique
    headers.find_heaviest()

    # NB: returns a header dict. hashes are unique
    #     at least, if they aren't, we have bigger problems than Zeta breaking :)
    h = headers.find_by_hash("00000000000000000020ba2cdb900193eb8af323487a84621d45f2222e01f8c6")

    print(h['height'])
    print(h['merkle_root'])
    print(h['hex'])

if __name__ == '__main__':
    asyncio.ensure_future(use_zeta())
    asyncio.run_forever()
```


## Header Format

See all types in `zeta/zeta_types.py`

## Development

```
$ pipenv install -d
```

### Running tests

This will run the linter, the type checker, and then the unit tests.

We actually wrote a few unit tests

```
$ tox
```

## Infrequently asked questions

#### How is Zeta?

Very young and resource inefficient.

#### Why is Zeta?

Zeta is pure python, and has only 1 dependency (which is also pure python). We intended it to be lightweight and easily packaged. We will be using it in the wild shortly.

#### Does zeta support multiple chains?

Not at the moment. Although it could pretty easily. If we wanted to move that direction, each chain would need to supply its own parsing interface and schema, and I haven't bothered looking at that yet.

#### Why are the hardcoded servers and checkpoints in .py files?

pyinstaller does not support pkg_resources. Putting the servers in .py files ensures they can be packaged in executables

#### What else?

Future plans:
1. Add some logic to check if the chain tip gets stuck (e.g. because of electrum errors)
1. Track prevouts in history and mempool
1. Implemnt merkle proof validation
1. Validate electrum scripthash messages against headers
