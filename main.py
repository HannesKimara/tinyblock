import hashlib, io

from tinyblock.secp256kl import PrivateKey


def hash256(s: str):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

    
if __name__ == '__main__':
    e = int.from_bytes(hash256(b'my very secret secret'), 'big')
    z = int.from_bytes(hash256(b'my message'), 'big')

    prv = PrivateKey(e)
    print(f'Point: {prv.point}')
    addr = prv.point.address()

    print(f'Address: {addr}')
