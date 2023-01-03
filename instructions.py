from enum import Enum
from typing import Union, Type, List

from typeguard import typechecked

from modrm import AddressDisp, Address, Disp8RM, RegRM, AtRegRM, AtRegDisp8RM
from not_int import NotInt
from opcodes import Opcode, ClearOpcode, OpDATA, ModRMOpcode, JMPOpcode
from regs import Reg, Reg8


class BaseInstruction:
    @typechecked
    def __init__(self, *, line: int):
        self.line: int = line

    def __repr__(self):
        return f"{self.line}: {type(self).__name__}"

    def process(self) -> ClearOpcode:
        pass


class InstData(BaseInstruction):
    @typechecked
    def __init__(self, args: List[Union[str, NotInt]], *, line: int):
        self.args = args
        super().__init__(line=line)

    def process(self) -> ClearOpcode:
        line: List[NotInt] = []
        for i in self.args:
            if isinstance(i, str):
                for j in bytes(i, "utf-8"):
                    line.append(NotInt(j))
                continue
            line.append(i)
        return OpDATA(line)


class BaseInstReversible(BaseInstruction):
    normal_opcode: Opcode
    reverse_opcode: Opcode

    @typechecked
    def __init__(self, left: Union[Reg, NotInt, Address, AddressDisp], right: Reg, is_reversed: bool, *, line: int):
        self.left = left
        self.right = right
        self.is_reversed = is_reversed
        super().__init__(line=line)

    def process(self) -> ModRMOpcode:
        if isinstance(self.left, Reg):
            mod_rm = RegRM(self.left, self.right)
        elif isinstance(self.left, NotInt):
            mod_rm = Disp8RM(self.left, self.right)
        elif isinstance(self.left, Address):
            mod_rm = AtRegRM(self.left, self.right)
        elif isinstance(self.left, AddressDisp):
            mod_rm = AtRegDisp8RM(self.left, self.right)
        else:
            raise Exception
        if self.is_reversed:
            return ModRMOpcode(self.reverse_opcode, mod_rm)
        return ModRMOpcode(self.normal_opcode, mod_rm)


class BaseInstJMP(BaseInstruction):
    jmp_opcode: Opcode

    @typechecked
    def __init__(self, num: NotInt, *, line: int):
        self.num = num
        super().__init__(line=line)

    def process(self) -> JMPOpcode:
        return JMPOpcode(self.jmp_opcode, self.num)


class BaseInstLeft(BaseInstruction):
    left_opcode: Opcode

    @typechecked
    def __init__(self, arg: Union[Reg, NotInt, Address, AddressDisp], *, line: int):
        self.arg = arg
        super().__init__(line=line)

    def process(self) -> ModRMOpcode:
        if isinstance(self.arg, Reg):
            mod_rm = RegRM(self.arg, Reg8.AX)
        elif isinstance(self.arg, NotInt):
            mod_rm = Disp8RM(self.arg, Reg8.AX)
        elif isinstance(self.arg, Address):
            mod_rm = AtRegRM(self.arg, Reg8.AX)
        elif isinstance(self.arg, AddressDisp):
            mod_rm = AtRegDisp8RM(self.arg, Reg8.AX)
        else:
            raise Exception
        return ModRMOpcode(self.left_opcode, mod_rm)


class BaseInstClear(BaseInstruction):
    clear_opcode: Opcode

    def process(self) -> ClearOpcode:
        return ClearOpcode(self.clear_opcode)


class EnumInstLeft(Enum):
    @staticmethod
    def new(left_opcode_: Opcode) -> Type[BaseInstLeft]:
        class NewInst(BaseInstLeft):
            left_opcode = left_opcode_

        return NewInst

    PUSH = new(Opcode.PUSH)
    POP = new(Opcode.POP)
    NOT = new(Opcode.NOT)


class EnumInstReversible(Enum):
    @staticmethod
    def new(normal_: Opcode, reverse_: Opcode) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal_opcode: Opcode = normal_
            reverse_opcode: Opcode = reverse_

        return NewInst

    ADD = new(Opcode.ADD, Opcode.ADDR)
    SUB = new(Opcode.SUB, Opcode.SUBR)
    MOV = new(Opcode.MOV, Opcode.MOVR)
    CMP = new(Opcode.CMP, Opcode.CMPR)
    SHL = new(Opcode.SHL, Opcode.SHLR)
    SHR = new(Opcode.SHR, Opcode.SHRR)
    AND = new(Opcode.AND, Opcode.ANDR)
    OR = new(Opcode.OR, Opcode.ORR)
    XOR = new(Opcode.XOR, Opcode.XORR)


class EnumInstJmp(Enum):
    @staticmethod
    def new(imm_opcode_: Opcode) -> Type[BaseInstJMP]:
        class NewInst(BaseInstJMP):
            jmp_opcode: Opcode = imm_opcode_

        return NewInst

    JMP = new(Opcode.JMP)
    JE = new(Opcode.JE)
    JNE = new(Opcode.JNE)
    JL = new(Opcode.JL)
    JLE = new(Opcode.JLE)
    JG = new(Opcode.JG)
    JGE = new(Opcode.JGE)
    CALL = new(Opcode.CALL)


class EnumInstClear(Enum):
    @staticmethod
    def new(clear_opcode_: Opcode) -> Type[BaseInstClear]:
        class NewInst(BaseInstClear):
            clear_opcode = clear_opcode_

        return NewInst

    RET = new(Opcode.RET)
