# TinyBlock

A from scratch implementation of a bitcoin node in python. It currently supports creating addresses, transactions and their serialization schemas.

## Implemented Features

- [x] Finite Fields (FieldElement, Point, Curve)
- [x] Ellitic curve (Secp25kl, Keys, Signatures ...)
- [x] Serialization ((Un)compressed SEC, DER, base58)
- [x] Transactions (Inputs, Outputs, Script, Creation/serialization)
- [ ] Script (Parse, Serialization, Eval)
- [ ] Networking, Transaction Creation, Broadcast and Validation
- [ ] Block Creation, Sync and Validation 
- [ ] Simple Payment Verification (Merkle Trees)
- [ ] Light Clients and Privacy (Bloom Filters) 
- [ ] Segwit (p2wpkh ...)
- [ ] Next (SHA256, Payment Channels, Lightning ...)

## Getting started
Code sample for generating a Private Key and address from a word secret. The sample prints the secp256kl curve points and an address

```python
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

```

## References
[[1]](https://www.oreilly.com/library/view/programming-bitcoin/9781492031482/)
Jimmy Song (2019),
Programming Bitcoin