from unittest import TestCase
from io import BytesIO

from tinyblock.tx import Tx, TxIn, TxOut, TxFetcher
from tinyblock.script import Script


class TestTx(TestCase):
    def setUp(self):
        self.raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        tx_ins = [
            TxIn(bytes.fromhex('d1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'), 0)
        ]
        tx_outs = [
            TxOut(32454049, Script()),
            TxOut(10011545, Script())
        ]
        self.tx = Tx(1, tx_ins, tx_outs, 410393)

    def test_parse_version(self):
        s = BytesIO(self.raw_tx)
        tx = Tx.parse(s)

        self.assertEqual(tx.version, self.tx.version)

    def test_parse_inputs(self):
        s = BytesIO(self.raw_tx)
        tx = Tx.parse(s)

        # Assert number of inputs
        self.assertEqual(len(tx.tx_ins), 1)

        # Assert previous transaction
        self.assertEqual(tx.tx_ins[0].prev_tx, self.tx.tx_ins[0].prev_tx)
        self.assertEqual(tx.tx_ins[0].tx_ix, self.tx.tx_ins[0].tx_ix)

    def test_parse_outputs(self):
        s = BytesIO(self.raw_tx)
        tx = Tx.parse(s)

        # Assert number of inputs
        self.assertEqual(len(tx.tx_outs), 2)

    def test_tx_serialize(self):
        ser = self.tx.serialize()

    def test_fee(self):
        s = BytesIO(self.raw_tx)
        tx = Tx.parse(s)

        print(tx.fee())


class TestTxFetcher(TestCase):
    def test_mainnet_get(self):
        tx_id = 'd1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'
        tx = TxFetcher.fetch(tx_id)
