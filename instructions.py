from enum import Enum
from typing import Union, Type, List

from typeguard import typechecked

import opcodes
from modrm import AddressDisp, Address, DispRM, RegRM, AtRegRM, AtRegDispRM
from not_int import NotInt
from regs import Reg


class BaseInstruction:
    @typechecked
    def __init__(self, *, line: int):
        self.line: int = line

    def __repr__(self):
        return f"{self.line}: {type(self).__name__}"

    def process(self) -> opcodes.BaseOpcode:
        pass


class InstData(BaseInstruction):
    @typechecked
    def __init__(self, args: List[Union[str, NotInt]], *, line: int):
        self.args = args
        super().__init__(line=line)

    def process(self) -> opcodes.BaseOpcode:
        line: List[NotInt] = []
        for i in self.args:
            if isinstance(i, str):
                for j in bytes(i, "utf-8"):
                    line.append(NotInt(j))
                continue
            line.append(i)
        return opcodes.OpDATA(self.line, line)


class BaseInstReversible(BaseInstruction):
    normal_opcode: Type[opcodes.ModRMOpcode]
    reverse_opcode: Type[opcodes.ModRMOpcode]

    @typechecked
    def __init__(self, left: Union[Reg, NotInt, Address, AddressDisp], right: Reg, is_reversed: bool, *, line: int):
        self.left = left
        self.right = right
        self.is_reversed = is_reversed
        super().__init__(line=line)

    def process(self) -> opcodes.ModRMOpcode:
        if isinstance(self.left, Reg):
            mod_rm = RegRM(self.left, self.right)
        elif isinstance(self.left, NotInt):
            mod_rm = DispRM(self.left, self.right)
        elif isinstance(self.left, Address):
            mod_rm = AtRegRM(self.left, self.right)
        elif isinstance(self.left, AddressDisp):
            mod_rm = AtRegDispRM(self.left, self.right)
        else:
            raise Exception
        if self.is_reversed:
            return self.reverse_opcode(self.line, mod_rm)
        return self.normal_opcode(self.line, mod_rm)


class BaseInstIMM(BaseInstruction):
    imm_opcode: Type[opcodes.IMMOpcode]

    @typechecked
    def __init__(self, num: NotInt, *, line: int):
        self.num = num
        super().__init__(line=line)

    def process(self) -> opcodes.IMMOpcode:
        return self.imm_opcode(self.line, self.num)


class BaseInstLeft(BaseInstruction):
    left_opcode: Type[opcodes.ModRMOpcode]

    @typechecked
    def __init__(self, arg: Union[Reg, NotInt, Address, AddressDisp], *, line: int):
        self.arg = arg
        super().__init__(line=line)

    def process(self) -> opcodes.ModRMOpcode:
        if isinstance(self.arg, Reg):
            mod_rm = RegRM(self.arg, Reg.AX)
        elif isinstance(self.arg, NotInt):
            mod_rm = DispRM(self.arg, Reg.AX)
        elif isinstance(self.arg, Address):
            mod_rm = AtRegRM(self.arg, Reg.AX)
        elif isinstance(self.arg, AddressDisp):
            mod_rm = AtRegDispRM(self.arg, Reg.AX)
        else:
            raise Exception
        return self.left_opcode(self.line, mod_rm)


class BaseInstClear(BaseInstruction):
    clear_opcode: Type[opcodes.BaseOpcode]

    def process(self) -> opcodes.BaseOpcode:
        return self.clear_opcode(self.line)


class EnumInstLeft(Enum):
    @staticmethod
    def new(left_opcode_: Type[opcodes.ModRMOpcode]) -> Type[BaseInstLeft]:
        class NewInst(BaseInstLeft):
            left_opcode = left_opcode_

        return NewInst

    PUSH = new(opcodes.OpPUSH)
    POP = new(opcodes.OpPOP)
    NOT = new(opcodes.OpNOT)


class EnumInstReversible(Enum):
    @staticmethod
    def new(normal_: Type[opcodes.ModRMOpcode], reverse_: Type[opcodes.ModRMOpcode]) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal_opcode: Type[opcodes.ModRMOpcode] = normal_
            reverse_opcode: Type[opcodes.ModRMOpcode] = reverse_

        return NewInst

    ADD = new(opcodes.OpADD, opcodes.OpADDR)
    SUB = new(opcodes.OpSUB, opcodes.OpSUBR)
    MOV = new(opcodes.OpMOV, opcodes.OpMOVR)
    CMP = new(opcodes.OpCMP, opcodes.OpCMPR)
    SHL = new(opcodes.OpSHL, opcodes.OpSHLR)
    SHR = new(opcodes.OpSHR, opcodes.OpSHRR)
    AND = new(opcodes.OpAND, opcodes.OpANDR)
    OR = new(opcodes.OpOR, opcodes.OpORR)
    XOR = new(opcodes.OpXOR, opcodes.OpXORR)


class EnumInstImm(Enum):
    @staticmethod
    def new(imm_opcode_: Type[opcodes.IMMOpcode]) -> Type[BaseInstIMM]:
        class NewInst(BaseInstIMM):
            imm_opcode: Type[opcodes.IMMOpcode] = imm_opcode_

        return NewInst

    JMP = new(opcodes.OpJMP)
    JE = new(opcodes.OpJE)
    JNE = new(opcodes.OpJNE)
    JL = new(opcodes.OpJL)
    JLE = new(opcodes.OpJLE)
    JG = new(opcodes.OpJG)
    JGE = new(opcodes.OpJGE)
    CALL = new(opcodes.OpCALL)


class EnumInstClear(Enum):
    @staticmethod
    def new(clear_opcode_: Type[opcodes.BaseOpcode]) -> Type[BaseInstClear]:
        class NewInst(BaseInstClear):
            clear_opcode = clear_opcode_

        return NewInst

    RET = new(opcodes.OpRET)
