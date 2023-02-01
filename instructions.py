from enum import Enum
from typing import Union, Type, List

from typeguard import typechecked

from modrm import AddressDisp, Address, Disp8RM, RegRM, AtRegRM, AtRegDisp8RM
from not_int import NotInt
from opcodes import Opcode, ClearOpcode, OpDATA, ModRMOpcode, JMPOpcode, Opcode8, Opcode16
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


class BaseInstIMM(BaseInstruction):
    imm_opcode: Opcode

    @typechecked
    def __init__(self, num: NotInt, *, line: int):
        self.num = num
        super().__init__(line=line)

    def process(self) -> JMPOpcode:
        return JMPOpcode(self.imm_opcode, self.num)


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


class EnumInstLeft8(Enum):
    @staticmethod
    def new(left_opcode_: Opcode) -> Type[BaseInstLeft]:
        class NewInst(BaseInstLeft):
            left_opcode = left_opcode_

        return NewInst

    PUSH = new(Opcode8.PUSH)
    POP = new(Opcode8.POP)
    NOT = new(Opcode8.NOT)


class EnumInstReversible8(Enum):
    @staticmethod
    def new(normal_: Opcode, reverse_: Opcode) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal_opcode: Opcode = normal_
            reverse_opcode: Opcode = reverse_

        return NewInst

    ADD = new(Opcode8.ADD, Opcode8.ADDR)
    SUB = new(Opcode8.SUB, Opcode8.SUBR)
    MOV = new(Opcode8.MOV, Opcode8.MOVR)
    CMP = new(Opcode8.CMP, Opcode8.CMPR)
    SHL = new(Opcode8.SHL, Opcode8.SHLR)
    SHR = new(Opcode8.SHR, Opcode8.SHRR)
    AND = new(Opcode8.AND, Opcode8.ANDR)
    OR = new(Opcode8.OR, Opcode8.ORR)
    XOR = new(Opcode8.XOR, Opcode8.XORR)


class EnumInstIMM8(Enum):
    @staticmethod
    def new(imm_opcode_: Opcode) -> Type[BaseInstIMM]:
        class NewInst(BaseInstIMM):
            imm_opcode: Opcode = imm_opcode_

        return NewInst

    JMP = new(Opcode8.JMP)
    JE = new(Opcode8.JE)
    JNE = new(Opcode8.JNE)
    JL = new(Opcode8.JL)
    JLE = new(Opcode8.JLE)
    JG = new(Opcode8.JG)
    JGE = new(Opcode8.JGE)
    CALL = new(Opcode8.CALL)


class EnumInstClear8(Enum):
    @staticmethod
    def new(clear_opcode_: Opcode) -> Type[BaseInstClear]:
        class NewInst(BaseInstClear):
            clear_opcode = clear_opcode_

        return NewInst

    RET = new(Opcode8.RET)


class EnumInstLeft16(Enum):
    @staticmethod
    def new(left_opcode_: Opcode) -> Type[BaseInstLeft]:
        class NewInst(BaseInstLeft):
            left_opcode = left_opcode_

        return NewInst

    PUSH = new(Opcode16.PUSH)
    POP = new(Opcode16.POP)
    NOT = new(Opcode16.NOT)


class EnumInstReversible16(Enum):
    @staticmethod
    def new(normal_: Opcode, reverse_: Opcode) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal_opcode: Opcode = normal_
            reverse_opcode: Opcode = reverse_

        return NewInst

    ADD = new(Opcode16.ADD, Opcode16.ADDR)
    SUB = new(Opcode16.SUB, Opcode16.SUBR)
    MOV = new(Opcode16.MOV, Opcode16.MOVR)
    CMP = new(Opcode16.CMP, Opcode16.CMPR)
    SHL = new(Opcode16.SHL, Opcode16.SHLR)
    SHR = new(Opcode16.SHR, Opcode16.SHRR)
    AND = new(Opcode16.AND, Opcode16.ANDR)
    OR = new(Opcode16.OR, Opcode16.ORR)
    XOR = new(Opcode16.XOR, Opcode16.XORR)


class EnumInstIMM16(Enum):
    @staticmethod
    def new(imm_opcode_: Opcode) -> Type[BaseInstIMM]:
        class NewInst(BaseInstIMM):
            imm_opcode: Opcode = imm_opcode_

        return NewInst

    JMP = new(Opcode16.JMP)
    JE = new(Opcode16.JE)
    JNE = new(Opcode16.JNE)
    JL = new(Opcode16.JL)
    JLE = new(Opcode16.JLE)
    JG = new(Opcode16.JG)
    JGE = new(Opcode16.JGE)
    CALL = new(Opcode16.CALL)


class EnumInstClear16(Enum):
    @staticmethod
    def new(clear_opcode_: Opcode) -> Type[BaseInstClear]:
        class NewInst(BaseInstClear):
            clear_opcode = clear_opcode_

        return NewInst

    RET = new(Opcode16.RET)
