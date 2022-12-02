from enum import Enum
from typing import Union, Dict

from regs import Reg


class Address:
    def __init__(self, reg: Reg):
        assert reg in Reg
        self.reg: Reg = reg

    def __repr__(self):
        return f"Address[{self.reg}]"


class AddressDisp:
    def __init__(self, reg: Reg, disp: int):
        assert reg in Reg
        self.disp: int = (disp % 256 + 256) % 256
        self.reg: Reg = reg

    def __repr__(self):
        return f"AddressDisp[{self.reg} + {self.disp}]"


class ModRMMod(int, Enum):
    reg = 0
    at_reg = 1
    at_reg_disp = 2
    disp = 3


class BaseModRM:
    size: int
    mod: ModRMMod

    def __init__(self, r_reg: Reg):
        assert r_reg in Reg
        self.r_reg: Reg = r_reg

    def serialize(self) -> bytes:
        raise Exception

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)})"


class RegRM(BaseModRM):
    size = 1
    mod = ModRMMod.reg

    def __init__(self, l_reg: Reg, r_reg: Reg):
        super().__init__(r_reg)
        assert l_reg in Reg
        self.l_reg: Reg = l_reg

    def serialize(self) -> bytes:
        return bytes(((self.mod << 6) + (self.l_reg.value << 3) + self.r_reg.value,))

    def __str__(self) -> str:
        return f"{self.l_reg.value}, {self.r_reg.name}"


class AtRegRM(BaseModRM):
    size = 1
    mod = ModRMMod.at_reg

    def __init__(self, address: Address, r_reg: Reg):
        super().__init__(r_reg)
        assert address.reg in Reg
        self.l_reg: Reg = address.reg

    def serialize(self) -> bytes:
        return bytes(((self.mod.value << 6) + (self.l_reg.value << 3) + self.r_reg.value,))

    def __str__(self) -> str:
        return f"[{self.l_reg.value}], {self.r_reg.name}"


class AtRegDispRM(BaseModRM):
    size = 2
    mod = ModRMMod.at_reg_disp

    def __init__(self, address: AddressDisp, r_reg: Reg):
        super().__init__(r_reg)
        assert address.reg in Reg
        self.disp: int = (address.disp % 256 + 256) % 256
        self.l_reg: Reg = address.reg

    def __str__(self) -> str:
        return f"[{self.l_reg.name} + {self.disp}], {self.r_reg.name}"

    def serialize(self) -> bytes:
        return bytes(((self.mod << 6) + (self.l_reg.value << 3) + self.r_reg.value, self.disp))


class DispRM(BaseModRM):
    size = 2
    mod = ModRMMod.disp

    def __init__(self, disp: int, r_reg: Reg):
        super().__init__(r_reg)
        self.disp: int = (disp % 256 + 256) % 256

    def serialize(self) -> bytes:
        return bytes(((self.mod << 6) + self.r_reg.value, self.disp))

    def __str__(self) -> str:
        return f"{self.disp}, {self.r_reg.name}"
