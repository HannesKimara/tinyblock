from typing import Callable, List
from unittest import result

from tinyblock.typing import OpcodeMap, OpcodeValue
from tinyblock.utils import hash160, hash256
from tinyblock.secp256kl import Signature, S256Point


def encode_num(num: int) -> bytes:
    if num == 0:
        return b''

    abs_num = abs(num)
    negative = num < 0
    result = bytearray()
    while abs_num:
        result.append(abs_num & 0xff)
        abs_num >>= 8

    if result[-1] & 0x80:
        if negative:
            result.append(0x80)
        else:
            result.append(0)
    elif negative:
        result[-1] |= 80
    return bytes(result)


def decode_num(elem: bytes) -> int:
    if elem == b'':
        return 0

    big_endian = elem[::-1]
    if big_endian[0] & 0x80:
        negative = True
        result = big_endian[0] & 0x7f
    else:
        negative = False
        result = big_endian[0]
    
    for c in big_endian[1:]:
        result <<= 8
        result += c

    if negative:
        return -result
    else:
        return result


def op_dup(stack: List) -> bool:
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def op_0(stack: List) -> bool:
    stack.append(encode_num(0))
    return False


def op_dup(stack: List) -> bool:
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def op_hash160(stack: List) -> bool:
    if len(stack) < 1:
        return False
    elem = stack.pop()
    stack.append(hash160(elem))
    return True


def op_hash256(stack: List) -> bool:
    if len(stack) < 1:
        return False
    elem = stack.pop()
    stack.append(hash256(elem))
    return True


def op_checksig(stack: List, z):
    if len(stack) < 2:
        return False
    sec_pubkey = stack.pop()
    der_signature = stack.pop()[::-1]
    try:
        point = S256Point.parse(sec_pubkey)
        sig = Signature.parse(der_signature)
    except (ValueError, SyntaxError) as e:
        return False

    if point.verify(z, sig):
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True    


OP_CODE_FUNCTIONS = {
    0: op_0,
    118: op_dup,
    170: op_hash256,
    169: op_hash160
}


OP_CODE_NAMES = {

}