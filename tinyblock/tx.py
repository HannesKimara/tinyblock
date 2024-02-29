from __future__ import annotations # For PEP 563 – Postponed Evaluation of Annotations
from dataclasses import dataclass, field
from typing import List, Union, BinaryIO
from io import BytesIO
import os

import requests

from .utils import hash256, encode_varint, read_varint
from .script import Script

__all__ = ['TxIn', 'TxOut', 'Tx', 'TxFetcher']


@dataclass
class TxIn:
    prev_tx: Union[bytes, str]
    tx_ix: int
    script_sig: Script = field(default_factory=Script, compare=False, repr=False)
    sequence: int = field(default=0xffffffff, repr=False)

    def __post_init__(self):
        if isinstance(self.prev_tx, bytes):
            pass
        elif isinstance(self.prev_tx, str):
            self.prev_tx = bytes.fromhex(self.prev_tx)
        else:
            raise ValueError("Unsupported previous transaction type")

    def serialize(self) -> bytes:
        """
        Returns a concise binary representation of the Tx Input
        """
        ser = b''
        ser += self.prev_tx[::-1]
        ser += self.tx_ix.to_bytes(4, 'little')
        ser += self.script_sig.serialize()
        ser += self.sequence.to_bytes(4, 'little')
        return ser

    @classmethod
    def parse(cls, s: BinaryIO):
        ser_tx_hash = s.read(32)[::-1]
        tx_hash = ser_tx_hash.hex()

        tx_ix = int.from_bytes(s.read(4), 'little')
        script_sig = Script.parse(s)
        sequence = int.from_bytes(s.read(4), 'little')

        return cls(tx_hash, tx_ix, script_sig, sequence)

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        tx = self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.tx_ix].amount

    def __repr__(self):
        return f'{self.__class__.__name__}(prev_tx={self.prev_tx.hex()}, tx_ix={self.tx_ix})'


@dataclass
class TxOut:
    amount: int
    script_pubkey: Script

    def serialize(self) -> bytes:
        """
        Returns a concise binary representation of the Tx Output
        """
        ser = b''
        ser += self.amount.to_bytes(8, 'little')
        ser += self.script_pubkey.serialize()
        return ser

    @classmethod
    def parse(cls, s: BinaryIO):
        amount = int.from_bytes(s.read(8), 'little')
        script_pubkey = Script.parse(s)

        return cls(amount, script_pubkey)


class TxFetcher:
    @staticmethod
    def fetch(tx_id: str, testnet=False):
        CACHE_DIR = 'tx_cache'
        assert isinstance(tx_id, str)
        tx_cache_file = os.path.join(CACHE_DIR, tx_id)
        if os.path.exists(tx_cache_file):
            with open(tx_cache_file, 'rb') as f:
                raw = f.read()

        else:
            if testnet:
                base = 'https://blockstream.info/testnet/api/tx/'
            else:
                base =  'https://blockstream.info/api/tx/'
            res = requests.get(f'{base}/{tx_id}/hex')
            assert res.status_code == 200
            raw = bytes.fromhex(res.text.strip())

            if not os.path.isdir(CACHE_DIR):
                os.makedirs(CACHE_DIR, exist_ok=True)

            with open(tx_cache_file, 'wb') as f:
                f.write(raw)

        tx = Tx.parse(BytesIO(raw))

        return tx

@dataclass(repr=False)
class Tx:
    version: int
    tx_ins: List[TxIn]
    tx_outs: List[TxOut]
    locktime: int = 0
    testnet: bool = False

    def serialize(self) -> bytes:
        """
        Returns a concise binary representation of the transaction
        """
        ser = b''
        ser += self.version.to_bytes(4, 'little')

        ser += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            ser += tx_in.serialize()
        
        ser += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            ser += tx_out.serialize()

        ser += self.locktime.to_bytes(4, 'little')

        return ser

    def id(self) -> str:
        """
        Returns a hex encoded hash of the serialized transaction
        """
        return self.hash().hex()

    def hash(self) -> bytes:
        """
        Returns a binary hash of the serialized transaction
        """
        return hash256(self.serialize())

    @classmethod
    def parse(cls, stream: BinaryIO, testnet=False) -> Tx:
        version = int.from_bytes(stream.read(4), 'little')
        num_inputs = read_varint(stream)

        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(stream))
        
        num_outputs = read_varint(stream)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(stream))
        
        locktime = int.from_bytes(stream.read(4), 'little')

        return cls(version, inputs, outputs, locktime)


    def __str__(self):
        rpr = '\n'
        rpr += f'Version: {self.version}\n'
        rpr += f'Inputs({len(self.tx_ins)}):\n'
        
        for tx_in in self.tx_ins:
            rpr += f'\t{tx_in}\n'

        rpr += f'Outputs({len(self.tx_outs)}):\n'
        for tx_out in self.tx_outs:
            rpr += f'\t{tx_out}\n'
        
        rpr += f'Locktime: {self.locktime}'

        return rpr

    def fee(self, testnet=False):
        total_input = 0

        for tx_in in self.tx_ins:
            total_input += tx_in.value(testnet=testnet)
        
        total_output = 0

        for tx_out in self.tx_outs:
            total_output += tx_out.amount

        return total_input - total_output
