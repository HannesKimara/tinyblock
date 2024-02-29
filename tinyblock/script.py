from __future__ import annotations # For PEP 563 – Postponed Evaluation of Annotations
from typing import BinaryIO, List, Union
from dataclasses import dataclass

from tinyblock.utils import read_varint, hash256, encode_varint, hash160
from tinyblock.opcodes import OP_CODE_FUNCTIONS, OP_CODE_NAMES


__all__ = ['Script']


@dataclass
class Script:
    cmds: List[Union[int, bytes]]

    @classmethod
    def parse(cls, s: BinaryIO) -> Script:
        len_script = read_varint(s)

        cmds = []
        count = 0
        while count < len_script:
            current = s.read()
            count += 1
            curr_byte = current[0]
            if curr_byte >= 1 and curr_byte <= 75:
                n = curr_byte
                cmds.append(s.read(n))
                count += n
            elif curr_byte == 76:
                data_len = int.from_bytes(s.read(1), 'little')
                cmds.append(s.read(data_len))
                count += data_len + 1
            elif curr_byte == 77:
                data_len = int.from_bytes(s.read(2), 'little')
                cmds.append(s.read(data_len))
                count += data_len + 2
            else:
                op_code = curr_byte
                cmds.append(op_code)
        if count != len_script:
            raise SyntaxError('parsing script failed')
        return cls(cmds)

    def serialize(self) -> bytes:
        ser = b''

        for cmd in self.cmds:
            if isinstance(cmd, int):
                ser += int.to_bytes(cmd, 1, 'little')
            else:
                length = len(cmd)
                if length < 75:
                    ser += int.to_bytes(length, 1, 'little')
                elif length > 75 and length < 256:
                    ser += int.to_bytes(76, 1, 'little')
                    ser += int.to_bytes(length, 1, 'little')
                elif length > 256 and length < 520:
                    ser += int.to_bytes(77, 1)
                    ser += int.to_bytes(length, 2, 'little')
                else:
                    raise ValueError('too long')

        return encode_varint(len(ser)) + ser                

    def eval(self, z):
        cmds = self.cmds[:]
        stack = []
        altstack = []
        while len(cmds) > 0:
            cmd = cmds.pop(0)
            if type(cmd) == int:
                op = OP_CODE_FUNCTIONS[cmd]
                if cmd in (99, 100): # OP_IF and OP_NOTIF
                    if not op(stack, cmds):
                        print(f'Bad op: {OP_CODE_NAMES[cmd]}')
                        return False
                elif cmd in (107, 108): # OP_TOALTSTACK and OP_FROMALTSTACK
                    if not op(stack, altstack):
                        print(f'Bad op: {OP_CODE_NAMES[cmd]}')
                        return False
                elif cmd in (172, 173, 14, 175):
                    if not op(stack, z): # OP_CHECKSIG, OP_CHECKSIGVERIFY, OP_CHECKMULTISIG and OP_CHECKMULTISIGVERIFY
                        print(f'Bad op: {OP_CODE_NAMES[cmd]}')
                        return False
                else:
                    if not op(stack):
                        print(f'Bad op: {OP_CODE_NAMES[cmd]}')
                        return False
            else:
                stack.append(cmd)
            
        if len(stack) == 0:
            return False

        if stack.pop() == b'':
            return False
        return True

    def __add__(self, other: Script) -> Script:
        return self.__class__(self.cmds + other.cmds)
