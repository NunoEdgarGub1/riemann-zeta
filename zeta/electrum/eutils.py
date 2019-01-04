from riemann import utils as rutils
from riemann.encoding import addresses as addr


def address_to_electrum_scripthash(address: str) -> str:
    '''Electrum is lame and uses backwards sha hashes of output scripts

    Args:
        address (str): a valid bitcoin address
    Returns:
        (str): the electrum-formatted scripthash in hex
    '''
    scripthash = rutils.sha256(addr.to_output_script(address))
    return scripthash[::-1].hex()
