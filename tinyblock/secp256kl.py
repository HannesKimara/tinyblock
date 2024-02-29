from typing import Union
from random import randint
from dataclasses import dataclass, field

from .ecc import FieldElement, Point, Curve
from .utils import hash160, checksum_base58


__all__ = ['Signature', 'S256Point', 'S256Field', 'G', 'PrivateKey']

# Order of the curve 
P = 2**256 - 2**32 - 977

# Coefficients of the curve 
A, B = 0, 7

# Order of the group {G, 2G, 3G, ..., NG}
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

@dataclass(repr=False)
class Signature:
    r: int
    s: int

    def to_der(self) -> bytes:
        rb = self.r.to_bytes(32, 'big')
        rb = rb.lstrip(b'\x00')

        if rb[0] >= 0x80:
            rb = b'\x00' + rb
        res = bytes([2, len(rb)]) + rb

        sb = self.s.to_bytes(32, 'big')
        sb = sb.lstrip(b'\x00')

        if sb[0] >= 0x80:
            sb = b'\x00' + sb

        res += bytes([2, len(sb)]) + sb
        return bytes([30, len(res)]) + res


    @classmethod
    def parse(cls, signature_bin):
        s = BytesIO(signature_bin)
        compound = s.read(1)[0]
        if compound != 0x30:
            raise SyntaxError("Bad Signature")
        length = s.read(1)[0]
        if length + 2 != len(signature_bin):
            raise SyntaxError("Bad Signature Length")
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        rlength = s.read(1)[0]
        r = int.from_bytes(s.read(rlength), 'big')
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        slength = s.read(1)[0]
        s = int.from_bytes(s.read(slength), 'big')
        if len(signature_bin) != 6 + rlength + slength:
            raise SyntaxError("Signature too long")
        return cls(r, s)

    def __repr__(self):
        return f'Signature({hex(self.r)}, {hex(self.s)})'


class S256Field(FieldElement):
    def __init__(self, num: int, order: int = None):
        super().__init__(num=num, order=P)

    def sqrt(self):
        return self**((P + 1) // 4)

    def __repr__(self):
        return f'S256Field({self.num:064})'


class S256Point(Point):
    def __init__(self, x:Union[int, S256Field], y:Union[int, S256Field], curve: Curve = None):
        curve = Curve(S256Field(A), S256Field(B), 1)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), curve=curve)
        else:
            super().__init__(x=x, y=y, curve=curve)

    def is_valid(self, z, sig:Signature):
        s_inv = pow(sig.s, N-2, N)
        u = z * s_inv % N
        v = sig.r *s_inv % N
        return (u * G + v * self).x.num == sig.r

    def hash160(self, compressed: bool=True):
        return hash160(self.to_sec(compressed))

    def address(self, compressed: bool=True, testnet: bool=True):
        h = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'

        return checksum_base58(prefix + h)

    def to_sec(self, compressed: bool=True):
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
        else:
            return b'\x04' + self.x.num.to_bytes(32, 'big') + self.y.num.to_bytes(32, 'big')

    @classmethod
    def from_sec(cls, sec_byte: bytearray):
        if sec_byte[0] == 4:
            x = int.from_bytes(sec_byte[1:33], 'big')
            y = int.from_bytes(sec_byte[33:65], 'big')
            return S256Point(x, y)

        x = int.from_bytes(sec_byte[1:], 'big')
        y2 = cls.curve(x)
        y = y2.sqrt()

        if y.num % 2 == 0:
            even_y = y
            odd_y = S256Field(P - y.num)
        else:
            odd_y = y
            even_y = S256Field(P - y.num)

        if sec_byte[0] == 2:
            return cls(x, even_y)
        else:
            return cls(x, odd_y)

    @classmethod
    def parse(cls, sec_byte: bytearray):
        return cls.from_sec(sec_byte)

    def __rmul__(self, coef: int):
        coef = coef % N
        return super().__rmul__(coef)

    def __repr__(self):
        return  f'S256Point({hex(self.x.num)}, {hex(self.y.num)})'


G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)


@dataclass
class PrivateKey:
    secret: int
    point: S256Point = field(init=False, repr=False)

    def __post_init__(self):
        self.point = self.secret * G

    def sign(self, z: int):
        k = randint(0, N) # TODO: use deterministic k
        r = (k * G).x.num
        k_inv = pow(k, N-2, N)
        s = (z + r * self.secret) * k_inv % N
        if s > N/2:
            s = N - s

        return Signature(r, s)
