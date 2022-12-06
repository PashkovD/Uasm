from enum import Enum

from typeguard import typechecked

from machine_file import MachineFile
from modrm import BaseModRM


class Opcode(int, Enum):
    DATA = -1
    ADD = 0
    ADDR = 1
    SUB = 2
    SUBR = 3
    MOV = 4
    MOVR = 5
    CMP = 6
    CMPR = 7
    JMP = 8
    JE = 9
    JNE = 10
    JL = 11
    JLE = 12
    JG = 13
    JGE = 14
    PUSH = 15
    POP = 16
    CALL = 17
    RET = 18
    SHL = 19
    SHLR = 20
    SHR = 21
    SHRR = 22
    AND = 23
    ANDR = 24
    XOR = 25
    XORR = 26
    OR = 27
    ORR = 28
    NOT = 29


class BaseOpcode:
    opcode: Opcode

    def __init__(self, line: int):
        self.line: int = line

    @property
    def size(self) -> int:
        return 1

    def __str__(self):
        return f"{self.opcode.name}"

    def __repr__(self):
        return f"{type(self).__name__}()"

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode.value,)))


class OpDATA(BaseOpcode):
    opcode = Opcode.DATA

    def __init__(self, line: int, data: bytes):
        super().__init__(line)
        self.data: bytes = data
        self.line: int = line

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(self.data)

    @property
    def size(self) -> int:
        return len(self.data)


class ModRMOpcode(BaseOpcode):
    def __init__(self, line: int, modrm: BaseModRM):
        super().__init__(line)
        self.modrm: BaseModRM = modrm

    @property
    def size(self) -> int:
        return 2

    def __str__(self):
        return f"{self.opcode.name} {str(self.modrm)}"

    def __repr__(self):
        return f"{type(self).__name__}({str(self.modrm)})"

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode.value,)) + self.modrm.serialize())


class IMMOpcode(BaseOpcode):
    def __init__(self, line: int, imm: int):
        super().__init__(line)
        assert imm in range(256)
        self.imm: int = imm

    @property
    def size(self) -> int:
        return 2

    def __str__(self):
        return f"{self.opcode.name} {str(self.imm)}"

    def __repr__(self):
        return f"{type(self).__name__}({str(self.imm)})"

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode.value, self.imm)))


class OpADD(ModRMOpcode):
    opcode = Opcode.ADD


class OpSUB(ModRMOpcode):
    opcode = Opcode.SUB


class OpMOV(ModRMOpcode):
    opcode = Opcode.MOV


class OpCMP(ModRMOpcode):
    opcode = Opcode.CMP


class OpADDR(ModRMOpcode):
    opcode = Opcode.ADDR


class OpSUBR(ModRMOpcode):
    opcode = Opcode.SUBR


class OpMOVR(ModRMOpcode):
    opcode = Opcode.MOVR


class OpCMPR(ModRMOpcode):
    opcode = Opcode.CMPR


class OpJMP(IMMOpcode):
    opcode = Opcode.JMP


class OpJE(IMMOpcode):
    opcode = Opcode.JE


class OpJNE(IMMOpcode):
    opcode = Opcode.JNE


class OpJL(IMMOpcode):
    opcode = Opcode.JL


class OpJLE(IMMOpcode):
    opcode = Opcode.JLE


class OpJG(IMMOpcode):
    opcode = Opcode.JG


class OpJGE(IMMOpcode):
    opcode = Opcode.JGE


class OpPUSH(ModRMOpcode):
    opcode = Opcode.PUSH


class OpPOP(ModRMOpcode):
    opcode = Opcode.POP


class OpCALL(IMMOpcode):
    opcode = Opcode.CALL


class OpRET(BaseOpcode):
    opcode = Opcode.RET


class OpSHL(ModRMOpcode):
    opcode = Opcode.SHL


class OpSHLR(ModRMOpcode):
    opcode = Opcode.SHLR


class OpSHR(ModRMOpcode):
    opcode = Opcode.SHR


class OpSHRR(ModRMOpcode):
    opcode = Opcode.SHRR


class OpAND(ModRMOpcode):
    opcode = Opcode.AND


class OpANDR(ModRMOpcode):
    opcode = Opcode.ANDR


class OpOR(ModRMOpcode):
    opcode = Opcode.OR


class OpORR(ModRMOpcode):
    opcode = Opcode.ORR


class OpXOR(ModRMOpcode):
    opcode = Opcode.XOR


class OpXORR(ModRMOpcode):
    opcode = Opcode.XORR


class OpNOT(ModRMOpcode):
     opcode = Opcode.NOT


# op_cls: Dict[Opcode, Type[BaseOpcode]] = {
#     OpDATA.opcode: OpDATA,
#     OpADD.opcode: OpADD,
#     OpSUB.opcode: OpSUB,
#     OpMOV.opcode: OpMOV,
#     OpCMP.opcode: OpCMP,
#     OpADDR.opcode: OpADDR,
#     OpSUBR.opcode: OpSUBR,
#     OpMOVR.opcode: OpMOVR,
#     OpCMPR.opcode: OpCMPR,
#     OpJMP.opcode: OpJMP,
#     OpJE.opcode: OpJE,
#     OpJNE.opcode: OpJNE,
#     OpJL.opcode: OpJL,
#     OpJLE.opcode: OpJLE,
#     OpJG.opcode: OpJG,
#     OpJGE.opcode: OpJGE,
#     OpPUSH.opcode: OpPUSH,
#     OpPOP.opcode: OpPOP,
#     OpCALL.opcode: OpCALL,
#     OpRET.opcode: OpRET,
#     OpSHL.opcode: OpSHL,
#     OpSHLR.opcode: OpSHLR,
#     OpSHR.opcode: OpSHR,
#     OpSHRR.opcode: OpSHRR,
# }
