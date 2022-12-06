from enum import Enum

from typeguard import typechecked

from machine_file import MachineFile
from not_int import NotInt
from regs import Reg


class Address:
    @typechecked
    def __init__(self, reg: Reg):
        self.reg: Reg = reg

    def __repr__(self):
        return f"Address[{self.reg}]"


class AddressDisp:
    @typechecked
    def __init__(self, reg: Reg, disp: NotInt):
        self.disp = disp
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

    @typechecked
    def __init__(self, r_reg: Reg):
        assert r_reg in Reg
        self.r_reg: Reg = r_reg

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        raise Exception

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)})"


class RegRM(BaseModRM):
    size = 1
    mod = ModRMMod.reg

    @typechecked
    def __init__(self, l_reg: Reg, r_reg: Reg):
        super().__init__(r_reg)
        assert l_reg in Reg
        self.l_reg: Reg = l_reg

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes(((self.mod << 6) + (self.l_reg.value << 3) + self.r_reg.value,)))

    def __str__(self) -> str:
        return f"{self.l_reg.value}, {self.r_reg.name}"


class AtRegRM(BaseModRM):
    size = 1
    mod = ModRMMod.at_reg

    @typechecked
    def __init__(self, address: Address, r_reg: Reg):
        super().__init__(r_reg)
        self.address = address

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes(((self.mod.value << 6) + (self.address.reg.value << 3) + self.r_reg.value,)))

    def __str__(self) -> str:
        return f"[{self.address.reg}], {self.r_reg.name}"


class AtRegDispRM(BaseModRM):
    size = 2
    mod = ModRMMod.at_reg_disp

    @typechecked
    def __init__(self, address: AddressDisp, r_reg: Reg):
        super().__init__(r_reg)
        self.left = address

    def __str__(self) -> str:
        return f"[{self.left.reg.name} + {self.left.disp}], {self.r_reg.name}"

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes(((self.mod << 6) + (self.left.reg.value << 3) + self.r_reg.value,)))
        file.write_int(self.left.disp)


class DispRM(BaseModRM):
    size = 2
    mod = ModRMMod.disp

    @typechecked
    def __init__(self, disp: NotInt, r_reg: Reg):
        super().__init__(r_reg)
        self.disp = disp

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes(((self.mod << 6) + self.r_reg.value,)))
        file.write_int(self.disp)

    def __str__(self) -> str:
        return f"{self.disp}, {self.r_reg.name}"
