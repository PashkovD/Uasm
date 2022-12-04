from modrm import AddressDisp, Address, DispRM, RegRM, AtRegRM, AtRegDispRM
from opcodes import *
from regs import Reg


class BaseInstruction:
    def __init__(self, line: int):
        self.line: int = line

    def __repr__(self):
        return f"{self.line}: {type(self).__name__}"

    def process(self) -> BaseOpcode:
        pass


class InstData(BaseInstruction):
    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        if len(self.args) < 1:
            raise Exception(f"{self.line}: less one Data args")
        if any((isinstance(i, Reg) and i in Reg) for i in self.args):
            raise Exception(f"{self.line}: Reg in Data args")
        if (Address in self.args) or (AddressDisp in self.args):
            raise Exception(f"{self.line}: Address in Data args")
        line: bytes = bytes()
        for i in self.args:
            if isinstance(i, str):
                line += bytes(i, "utf-8")
                continue
            line += bytes((i,))
        return OpDATA(self.line, line)


class InstTIMES(BaseInstruction):
    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        if len(self.args) < 2:
            raise Exception(f"{self.line}: Too few TIMES args: {len(self.args)}")
        if any((isinstance(i, Reg) and i in Reg) for i in self.args):
            raise Exception(f"{self.line}: Reg in TIMES args")
        if (Address in self.args) or (AddressDisp in self.args):
            raise Exception(f"{self.line}: Address in TIMES args")
        if self.args[0] < 1:
            raise Exception(f"{self.line}: Num less zero in TIMES args {self.args[0]}")
        line: bytes = bytes()
        for i in self.args[1:]:
            if isinstance(i, str):
                line += bytes(i, "utf-8")
                continue
            line += bytes((i,))
        return OpDATA(self.line, line * self.args[0])


class InstINC(BaseInstruction):
    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        if len(self.args) < 1:
            raise Exception(f"{self.line}: Too few INC args: {len(self.args)}")
        if not isinstance(self.args[0], Reg):
            raise Exception(f"{self.line}: incorrect type arg: {type(self.args[0])}")
        return OpADDR(self.line, DispRM(1, self.args[0]))


class InstDEC(BaseInstruction):
    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        if len(self.args) < 1:
            raise Exception(f"{self.line}: Too few DEC args: {len(self.args)}")
        if not isinstance(self.args[0], Reg):
            raise Exception(f"{self.line}: incorrect type arg: {type(self.args[0])}")
        return OpSUBR(self.line, DispRM(1, self.args[0]))


class BaseInstReversible(BaseInstruction):
    normal: Type[ModRMOpcode]
    reverse: Type[ModRMOpcode]

    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> ModRMOpcode:
        if len(self.args) != 2:
            raise Exception(f"{self.line}: Incorrect number of args: {len(self.args)}")
        if not any((isinstance(i, Reg) and i in Reg) for i in self.args):
            raise Exception(
                f"{self.line}: Incorrect combination of args: {type(self.args[0]).__name__}, {type(self.args[1]).__name__}")
        reverse = not isinstance(self.args[1], Reg)
        temp = None
        if reverse:
            temp = self.args
            self.args = self.args.copy()
            self.args[0], self.args[1] = self.args[1], self.args[0]
        if isinstance(self.args[0], Reg):
            mod_rm = RegRM(self.args[0], self.args[1])
        elif isinstance(self.args[0], int):
            mod_rm = DispRM(self.args[0], self.args[1])
        elif isinstance(self.args[0], Address):
            mod_rm = AtRegRM(self.args[0], self.args[1])
        elif isinstance(self.args[0], AddressDisp):
            mod_rm = AtRegDispRM(self.args[0], self.args[1])
        else:
            raise Exception
        if reverse:
            self.args = temp
            return self.reverse(self.line, mod_rm)
        return self.normal(self.line, mod_rm)


class BaseInstIMM(BaseInstruction):
    imm_opcode: Type[IMMOpcode]

    def __init__(self, num: int, line: int):
        self.num: int = num
        super().__init__(line)

    def process(self) -> IMMOpcode:
        return self.imm_opcode(self.line, self.num)


class BaseInstLeft(BaseInstruction):
    left_opcode: Type[ModRMOpcode]

    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> ModRMOpcode:
        if len(self.args) != 1:
            raise Exception(f"{self.line}: Incorrect number of args: {len(self.args)}")
        if isinstance(self.args[0], Reg):
            mod_rm = RegRM(self.args[0], Reg.AX)
        elif isinstance(self.args[0], int):
            mod_rm = DispRM(self.args[0], Reg.AX)
        elif isinstance(self.args[0], Address):
            mod_rm = AtRegRM(self.args[0], Reg.AX)
        elif isinstance(self.args[0], AddressDisp):
            mod_rm = AtRegDispRM(self.args[0], Reg.AX)
        else:
            raise Exception
        return self.left_opcode(self.line, mod_rm)


class BaseInstClear(BaseInstruction):
    clear_opcode: Type[BaseOpcode]

    def __init__(self, args: list, line: int):
        self.args = args
        super().__init__(line)

    def process(self) -> BaseOpcode:
        if len(self.args) != 0:
            raise Exception(f"{self.line}: Incorrect number of args: {len(self.args)}")
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
            normal: Type[ModRMOpcode] = normal_
            reverse: Type[ModRMOpcode] = reverse_

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
