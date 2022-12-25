from enum import Enum
from typing import List

from typeguard import typechecked

from machine_file import MachineFile
from modrm import BaseModRM
from not_int import NotInt


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


class ClearOpcode:
    @typechecked
    def __init__(self, opcode: Opcode):
        self.opcode: Opcode = opcode

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))


class OpDATA(ClearOpcode):
    opcode = None

    @typechecked
    def __init__(self, data: List[NotInt]):
        super().__init__(Opcode.DATA)
        self.data: List[NotInt] = data

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        for i in self.data:
            file.write_int(i)


class ModRMOpcode(ClearOpcode):
    @typechecked
    def __init__(self, opcode: Opcode, modrm: BaseModRM):
        super().__init__(opcode)
        self.modrm: BaseModRM = modrm

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))
        self.modrm.serialize(file)


class IMMOpcode(ClearOpcode):
    @typechecked
    def __init__(self, opcode: Opcode, imm: NotInt):
        super().__init__(opcode)
        self.imm: NotInt = imm

    @typechecked
    def serialize(self, file: MachineFile) -> None:
        file.write(bytes((self.opcode,)))
        file.write_int(self.imm)
