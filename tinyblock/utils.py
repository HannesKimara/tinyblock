from typing import BinaryIO
import hashlib


BASE58_CHARSET: str = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58_encode(s: bytearray) -> str:
    """
    Encodes a bytearray into base58
    """
    count = 0
    for char in s:
        if char == 0:
            count += 1
        else:
            break

    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    res = ''

    while num > 0:
        num, mod = divmod(num, 58)
        res = BASE58_CHARSET[mod] + res
    return prefix + res

def hash160(s: bytearray):
    """
    Returns the ripemd160 digest of the sha256 digest
    """
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

def hash256(s: bytearray):
    """
    Returns the two-time sha256 hash of a bytearray
    """
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def checksum_base58(s):
    """
    Returns the base58 encoding of a byte array appended with its checksum
    """
    return base58_encode(s + hash256(s)[:4])


def read_varint(stream: BinaryIO) -> bytes:
    """
    Reads a variable size integer from a stream
    """
    
    i = stream.read(1)[0]
    if i == 0xfd:
        return int.from_bytes(stream.read(2), 'little')
    elif i == 0xfe:
        return int.from_bytes(stream.read(4), 'little')
    elif i == 0xff:
        return int.from_bytes(stream.read(8), 'little')
    else:
        return i

def encode_varint(i: int) -> bytes:
    """
    Encodes an integer as a varint
    """
    if i < 0xfd :
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + i.to_bytes(2, 'little')
    elif i < 0x100000000:
        return b'\xfe' + i.to_bytes(4, 'little')
    elif i < 0x10000000000000000:
        return b'\xff' + i.to_bytes(8, 'little')
    else:
        raise ValueError(f'integer {i} is above 2 ** 64')
 

def int_to_little_endian(i: int, lenb: int) -> bytes:
    return int.to_bytes(i, lenb, 'little')

def little_endian_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'little')