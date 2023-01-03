from enum import Enum
from typing import List

from typeguard import typechecked

from machine_file import MachineFile
from modrm import BaseModRM
from not_int import NotInt


class Opcode(int):
    ...


class Opcode8(Opcode, Enum):
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


class Opcode16(Opcode, Enum):
    ADD = 0 + 64
    ADDR = 1 + 64
    SUB = 2 + 64
    SUBR = 3 + 64
    MOV = 4 + 64
    MOVR = 5 + 64
    CMP = 6 + 64
    CMPR = 7 + 64
    JMP = 8 + 64
    JE = 9 + 64
    JNE = 10 + 64
    JL = 11 + 64
    JLE = 12 + 64
    JG = 13 + 64
    JGE = 14 + 64
    PUSH = 15 + 64
    POP = 16 + 64
    CALL = 17 + 64
    RET = 18 + 64
    SHL = 19 + 64
    SHLR = 20 + 64
    SHR = 21 + 64
    SHRR = 22 + 64
    AND = 23 + 64
    ANDR = 24 + 64
    XOR = 25 + 64
    XORR = 26 + 64
    OR = 27 + 64
    ORR = 28 + 64
    NOT = 29 + 64


class ClearOpcode:
    @typechecked
    def __init__(self, opcode: Opcode):
        self.opcode: Opcode = opcode

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))


class OpDATA(ClearOpcode):
    @typechecked
    def __init__(self, data: List[NotInt]):
        super().__init__(Opcode(-1))
        self.data: List[NotInt] = data

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        for i in self.data:
            file.write_int8(i)


class ModRMOpcode(ClearOpcode):
    @typechecked
    def __init__(self, opcode: Opcode, modrm: BaseModRM):
        super().__init__(opcode)
        self.modrm: BaseModRM = modrm

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))
        self.modrm.serialize(file)


class JMPOpcode(ClearOpcode):
    @typechecked
    def __init__(self, opcode: Opcode, imm: NotInt):
        super().__init__(opcode)
        self.imm: NotInt = imm

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))
        file.write_int8(self.imm)
