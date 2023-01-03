from enum import Enum


class Reg(int):
    ...


class Reg8(Reg, Enum):
    AX = 0
    BX = 1
    CX = 2
    DX = 3
    SP = 7

    def __repr__(self): return f"{type(self).__name__}.{self.name}"


class Reg16(Reg, Enum):
    EAX = 0
    EBX = 1
    ECX = 2
    EDX = 3
    ESP = 7

    def __repr__(self): return f"{type(self).__name__}.{self.name}"
