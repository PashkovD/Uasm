from modrm import AddressDisp, Address, DispRM, RegRM, AtRegRM, AtRegDispRM
from opcodes import *
from regs import Reg


class BaseInstruction:
    def __init__(self, args: list, line: int):
        self.args = args
        self.line: int = line

    def __repr__(self):
        return f"{type(self).__name__}{repr(tuple(self.args))}: {self.line}"

    def process(self) -> BaseOpcode:
        pass


class InstData(BaseInstruction):
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
    def process(self) -> BaseOpcode:
        if len(self.args) < 1:
            raise Exception(f"{self.line}: Too few INC args: {len(self.args)}")
        if not isinstance(self.args[0], Reg):
            raise Exception(f"{self.line}: incorrect type arg: {type(self.args[0])}")
        return OpADDR(self.line, DispRM(1, self.args[0]))


class InstDEC(BaseInstruction):
    def process(self) -> BaseOpcode:
        if len(self.args) < 1:
            raise Exception(f"{self.line}: Too few DEC args: {len(self.args)}")
        if not isinstance(self.args[0], Reg):
            raise Exception(f"{self.line}: incorrect type arg: {type(self.args[0])}")
        return OpSUBR(self.line, DispRM(1, self.args[0]))


class BaseInstReversible(BaseInstruction):
    normal: Type[ModRMOpcode]
    reverse: Type[ModRMOpcode]

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

    def process(self) -> IMMOpcode:
        if len(self.args) != 1:
            raise Exception(f"{self.line}: Incorrect number of args: {len(self.args)}")
        if type(self.args[0]) != int:
            raise Exception(f"{self.line}: Incorrect argument: {type(self.args[0]).__name__}")
        return self.imm_opcode(self.line, self.args[0])


class BaseInstReg(BaseInstruction):
    reg_opcode: Type[ModRMOpcode]

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
        return self.reg_opcode(self.line, mod_rm)


class InstPUSH(BaseInstReg):
    reg_opcode = OpPUSH


class InstPOP(BaseInstReg):
    reg_opcode = OpPOP


class InstRET(BaseInstruction):
    def process(self) -> OpRET:
        if len(self.args) != 0:
            raise Exception(f"{self.line}: Incorrect number of args: {len(self.args)}")
        return OpRET(self.line)


class InstNOT(BaseInstReg):
    reg_opcode = OpNOT


class EnumInstruction(Enum):
    @staticmethod
    def new_reversible(normal_: Type[ModRMOpcode], reverse_: Type[ModRMOpcode]) -> Type[BaseInstReversible]:
        class NewInst(BaseInstReversible):
            normal: Type[ModRMOpcode] = normal_
            reverse: Type[ModRMOpcode] = reverse_

        return NewInst

    @staticmethod
    def new_imm(imm_opcode_: Type[IMMOpcode]) -> Type[BaseInstIMM]:
        class NewInst(BaseInstIMM):
            imm_opcode: Type[IMMOpcode] = imm_opcode_

        return NewInst

    INC = InstINC
    DEC = InstDEC
    TIMES = InstTIMES
    DATA = InstData
    ADD = new_reversible(OpADD, OpADDR)
    SUB = new_reversible(OpSUB, OpSUBR)
    MOV = new_reversible(OpMOV, OpMOVR)
    CMP = new_reversible(OpCMP, OpCMPR)
    JMP = new_imm(OpJMP)
    JE = new_imm(OpJE)
    JNE = new_imm(OpJNE)
    JL = new_imm(OpJL)
    JLE = new_imm(OpJLE)
    JG = new_imm(OpJG)
    JGE = new_imm(OpJGE)
    PUSH = InstPUSH
    POP = InstPOP
    CALL = new_imm(OpCALL)
    RET = InstRET
    SHL = new_reversible(OpSHL, OpSHLR)
    SHR = new_reversible(OpSHR, OpSHRR)
    AND = new_reversible(OpAND, OpANDR)
    OR = new_reversible(OpOR, OpORR)
    XOR = new_reversible(OpXOR, OpXORR)
    NOT = InstNOT
