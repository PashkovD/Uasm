from typing import Union, List

from typeguard import typechecked

from modrm import AddressDisp, Address, DispRM, RegRM, AtRegRM, AtRegDispRM
from opcodes import *
from regs import Reg


class BaseInstruction:
    @typechecked
    def __init__(self, line: int):
        self.line: int = line

    def __repr__(self):
        return f"{self.line}: {type(self).__name__}"

    def process(self) -> BaseOpcode:
        pass


class InstData(BaseInstruction):
    @typechecked
    def __init__(self, args: List[Union[str, int]], line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        line: bytes = bytes()
        for i in self.args:
            if isinstance(i, str):
                line += bytes(i, "utf-8")
                continue
            line += bytes((i,))
        return OpDATA(self.line, line)


class InstINC(BaseInstruction):
    @typechecked
    def __init__(self, reg: Reg, line: int):
        self.reg: Reg = reg
        super().__init__(line)

    def process(self) -> BaseOpcode:
        return OpADDR(self.line, DispRM(1, self.reg))


class InstDEC(BaseInstruction):
    @typechecked
    def __init__(self, reg: Reg, line: int):
        self.reg: Reg = reg
        super().__init__(line)

    def process(self) -> BaseOpcode:
        return OpSUBR(self.line, DispRM(1, self.reg))


class BaseInstReversible(BaseInstruction):
    normal_opcode: Type[ModRMOpcode]
    reverse_opcode: Type[ModRMOpcode]

    @typechecked
    def __init__(self, left: Union[Reg, int, Address, AddressDisp], right: Reg, is_reversed: bool, line: int):
        self.left = left
        self.right = right
        self.is_reversed = is_reversed
        super().__init__(line)

    def process(self) -> ModRMOpcode:
        if isinstance(self.left, Reg):
            mod_rm = RegRM(self.left, self.right)
        elif isinstance(self.left, int):
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
    imm_opcode: Type[IMMOpcode]

    @typechecked
    def __init__(self, num: int, line: int):
        self.num: int = num
        super().__init__(line)

    def process(self) -> IMMOpcode:
        return self.imm_opcode(self.line, self.num)


class BaseInstLeft(BaseInstruction):
    left_opcode: Type[ModRMOpcode]

    @typechecked
    def __init__(self, arg: Union[Reg, int, Address, AddressDisp], line: int):
        self.arg = arg
        super().__init__(line)

    def process(self) -> ModRMOpcode:
        if isinstance(self.arg, Reg):
            mod_rm = RegRM(self.arg, Reg.AX)
        elif isinstance(self.arg, int):
            mod_rm = DispRM(self.arg, Reg.AX)
        elif isinstance(self.arg, Address):
            mod_rm = AtRegRM(self.arg, Reg.AX)
        elif isinstance(self.arg, AddressDisp):
            mod_rm = AtRegDispRM(self.arg, Reg.AX)
        else:
            raise Exception
        return self.left_opcode(self.line, mod_rm)


class BaseInstClear(BaseInstruction):
    clear_opcode: Type[BaseOpcode]

    def process(self) -> BaseOpcode:
        return self.clear_opcode(self.line)


class EnumInstLeft(Enum):
    @staticmethod
    def new(left_opcode_: Type[ModRMOpcode]) -> Type[BaseInstLeft]:
        class NewInst(BaseInstLeft):
            left_opcode = left_opcode_

        return NewInst

    PUSH = new(OpPUSH)
    POP = new(OpPOP)
    NOT = new(OpNOT)


class EnumInstReversible(Enum):
    @staticmethod
    def new(normal_: Type[ModRMOpcode], reverse_: Type[ModRMOpcode]) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal_opcode: Type[ModRMOpcode] = normal_
            reverse_opcode: Type[ModRMOpcode] = reverse_

        return NewInst

    ADD = new(OpADD, OpADDR)
    SUB = new(OpSUB, OpSUBR)
    MOV = new(OpMOV, OpMOVR)
    CMP = new(OpCMP, OpCMPR)
    SHL = new(OpSHL, OpSHLR)
    SHR = new(OpSHR, OpSHRR)
    AND = new(OpAND, OpANDR)
    OR = new(OpOR, OpORR)
    XOR = new(OpXOR, OpXORR)


class EnumInstImm(Enum):
    @staticmethod
    def new(imm_opcode_: Type[IMMOpcode]) -> Type[BaseInstIMM]:
        class NewInst(BaseInstIMM):
            imm_opcode: Type[IMMOpcode] = imm_opcode_

        return NewInst

    JMP = new(OpJMP)
    JE = new(OpJE)
    JNE = new(OpJNE)
    JL = new(OpJL)
    JLE = new(OpJLE)
    JG = new(OpJG)
    JGE = new(OpJGE)
    CALL = new(OpCALL)


class EnumInstClear(Enum):
    @staticmethod
    def new(clear_opcode_: Type[BaseOpcode]) -> Type[BaseInstClear]:
        class NewInst(BaseInstClear):
            clear_opcode = clear_opcode_

        return NewInst

    RET = new(OpRET)
