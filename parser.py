from typing import List, Union, Dict

from ply import *

from instructions import BaseInstruction
from lexer import Lexer
from modrm import Address, AddressDisp
from regs import Reg


class NedoDict(dict):
    def __getitem__(self, item: str) -> int:
        return 255


class Pointer:
    def __init__(self, name: str, line: int):
        self.name: str = name
        self.line: int = line

    def __repr__(self):
        return f"Pointer({self.name}): {self.line}"


id_dict: Dict[str, int] = NedoDict()


class Parser:
    tokens = Lexer.tokens

    precedence = (
        ('left', 'DOT'),
        ('left', 'MINUS', 'PLUS'),
    )

    def __init__(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, input_: str, **kwargs):
        return self.parser.parse(input_, **kwargs)

    @staticmethod
    def p_code(p: yacc.YaccProduction):
        """code : code instruction
                | code pointer
                | code NEWLINE
                | pointer
                | instruction
                | NEWLINE"""
        if len(p) == 3:
            if not isinstance(p[1], list):
                p[1] = []
            p[0] = p[1]
            if p.slice[2].type != "NEWLINE":
                p[0].append(p[2])
        elif len(p) == 2 and p.slice[1].type == "NEWLINE":
            pass
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            raise Exception

    @staticmethod
    def p_pointer(p):
        """pointer : DOT ID NEWLINE"""
        p[0] = Pointer(p[2], p.slice[1].lineno)

    @staticmethod
    def p_expression_id(p):
        """expression : ID"""
        p[0] = id_dict[p[1]]

    @staticmethod
    def p_expression_int(p):
        """expression : INTEGER"""
        p[0] = p[1]

    @staticmethod
    def p_expression_unary(p):
        """expression : MINUS INTEGER"""
        if p[1] == "-":
            p[0] = -p[2]
        else:
            raise Exception

    @staticmethod
    def p_expression_bin(p):
        """expression : expression PLUS expression
                      | expression MINUS expression"""
        if p[2] == "+":
            p[0] = p[1] + p[3]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        else:
            raise Exception

    @staticmethod
    def p_instruction_data(p):
        """instruction : OpData data_operands NEWLINE"""
        p[0] = p[1](p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_times(p):
        """instruction : OpTimes expression COMMA data_operands NEWLINE"""
        p[0] = p[1](p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_inc(p):
        """instruction : OpDec REG NEWLINE"""
        p[0] = p[1](p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_dec(p):
        """instruction : OpInc REG NEWLINE"""
        p[0] = p[1](p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_imm(p):
        """instruction : InstImm expression NEWLINE"""
        p[0] = p[1].value(p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_rev(p):
        """instruction : InstReversible REG COMMA REG NEWLINE
                       | InstReversible addr COMMA REG NEWLINE
                       | InstReversible addr_disp COMMA REG NEWLINE
                       | InstReversible expression COMMA REG NEWLINE"""
        p[0] = p[1].value(p[2], p[4], is_reversed=False, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_rev_reversed(p):
        """instruction : InstReversible REG COMMA addr NEWLINE
                       | InstReversible REG COMMA addr_disp NEWLINE
                       | InstReversible REG COMMA expression NEWLINE"""
        p[0] = p[1].value(p[4], p[2], is_reversed=True, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_left(p):
        """instruction : InstLeft expression NEWLINE
                       | InstLeft REG NEWLINE
                       | InstLeft addr NEWLINE
                       | InstLeft addr_disp NEWLINE"""
        p[0] = p[1].value(p[2], p.slice[1].lineno)

    @staticmethod
    def p_instruction_clear(p):
        """instruction : InstClear NEWLINE"""
        p[0] = p[1].value([], p.slice[1].lineno)

    @staticmethod
    def p_addr(p):
        """addr : LBREACKET REG RBREACKET"""
        p[0] = Address(p[2])

    @staticmethod
    def p_addr_disp(p):
        """addr_disp : LBREACKET REG DOTS expression RBREACKET"""
        p[0] = AddressDisp(p[2], p[4])

    @staticmethod
    def p_addr_disp_reversed(p):
        """addr_disp : LBREACKET expression DOTS REG RBREACKET"""
        p[0] = AddressDisp(p[4], p[2])

    @staticmethod
    def p_operand(p):
        """operand : REG
                   | STRING
                   | expression
                   | LBREACKET REG RBREACKET
                   | LBREACKET REG DOTS expression RBREACKET
                   | LBREACKET expression DOTS REG """
        if len(p) == 4:
            p[0] = Address(p[2])
        elif len(p) == 6:
            reg: Reg
            disp: int
            if isinstance(p[2], Reg):
                reg, disp = p[2], p[4]
            else:
                reg, disp = p[4], p[2]
            if isinstance(disp, str):
                disp = id_dict[disp]
            p[0] = AddressDisp(reg, disp)

        elif len(p) == 2:
            if p.slice[1].type == "ID":
                p[1] = id_dict[p[1]]
            p[0] = p[1]
        else:
            raise Exception

    @staticmethod
    def p_data_operand(p):
        """data_operand   : expression
                          | STRING"""
        p[0] = p[1]

    @staticmethod
    def p_data_operands_start(p):
        """data_operands   : data_operand"""
        p[0] = [p[1]]

    @staticmethod
    def p_data_operands(p):
        """data_operands   : data_operands COMMA data_operand"""
        p[0] = p[1]
        p[0].append(p[3])


def parse(data: str) -> List[Union[Pointer, BaseInstruction]]:
    return Parser().parse(data, lexer=Lexer().lexer)
