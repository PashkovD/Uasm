from enum import Enum


class Reg8(Enum):
    AX = 0
    BX = 1
    CX = 2
    DX = 3
    SP = 7

    def __repr__(self): return f"{type(self).__name__}.{self.name}"
