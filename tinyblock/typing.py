from typing import Dict, Optional, Sequence, Union, Tuple, Callable, NamedTuple


from tinyblock.vm.opcodes import OpcodeValue

class OpcodeValue(NamedTuple):
    fn: Callable
    added: int
    popped: int


# Opcodes
OpcodeMap = Dict[int, OpcodeValue]
