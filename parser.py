from typing import List, Union

from ply import yacc

from instructions import BaseInstruction
from lexer import Lexer
from modrm import Address, AddressDisp
from not_int import NotInt


class Pointer:
    def __init__(self, name: str, line: int):
        self.name: str = name
        self.line: int = line

    def __repr__(self):
        return f"Pointer({self.name}): {self.line}"


class Parser(Lexer):
    precedence = (
        ('left', '.'),
        ('left', '-', '+'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, input_: str, **kwargs):
        return self.parser.parse(input_, **kwargs)

    @staticmethod
    def p_code_start(p):
        """code : """
        p[0] = []

    @staticmethod
    def p_code_newline(p):
        """code : code NEWLINE"""
        p[0] = p[1]

    @staticmethod
    def p_code(p):
        """code : code instruction
                | code pointer"""
        p[0] = p[1]
        p[0].append(p[2])

    @staticmethod
    def p_pointer(p):
        """pointer : '.' ID NEWLINE"""
        p[0] = Pointer(p[2], p.slice[1].lineno)

    @staticmethod
    def p_expression_id(p):
        """expression : ID"""
        p[0] = NotInt(0, {p[1]: 1})

    @staticmethod
    def p_expression_int(p):
        """expression : INTEGER"""
        p[0] = NotInt(p[1])

    @staticmethod
    def p_expression_unary(p):
        """expression : '-' expression"""
        if p[1] == "-":
            p[0] = -p[2]
        else:
            raise Exception

    @staticmethod
    def p_expression_bin(p):
        """expression : expression '+' expression
                      | expression '-' expression"""
        if p[2] == "+":
            p[0] = p[1] + p[3]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        else:
            raise Exception

    @staticmethod
    def p_instruction_data(p):
        """instruction : OpData data_operands NEWLINE"""
        p[0] = p[1](p[2], line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_times(p):
        """instruction : OpTimes expression ',' data_operands NEWLINE"""
        if len(p[2].symbols) != 0:
            raise Exception(f"{p.slice[1].lineno}: pointers in TIMES num not suported")
        p[0] = p[1](p[4] * p[2].num, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_inc_dec(p):
        """instruction : OpIncDec REG NEWLINE"""
        p[0] = p[1].value(NotInt(1), p[2], is_reversed=True, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_imm(p):
        """instruction : InstImm expression NEWLINE"""
        p[0] = p[1].value(p[2], line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_rev(p):
        """instruction : InstReversible REG ',' REG NEWLINE
                       | InstReversible addr ',' REG NEWLINE
                       | InstReversible addr_disp ',' REG NEWLINE
                       | InstReversible expression ',' REG NEWLINE"""
        p[0] = p[1].value(p[2], p[4], is_reversed=False, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_rev_reversed(p):
        """instruction : InstReversible REG ',' addr NEWLINE
                       | InstReversible REG ',' addr_disp NEWLINE
                       | InstReversible REG ',' expression NEWLINE"""
        p[0] = p[1].value(p[4], p[2], is_reversed=True, line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_left(p):
        """instruction : InstLeft expression NEWLINE
                       | InstLeft REG NEWLINE
                       | InstLeft addr NEWLINE
                       | InstLeft addr_disp NEWLINE"""
        p[0] = p[1].value(p[2], line=p.slice[1].lineno)

    @staticmethod
    def p_instruction_clear(p):
        """instruction : InstClear NEWLINE"""
        p[0] = p[1].value(line=p.slice[1].lineno)

    @staticmethod
    def p_addr(p):
        """addr : '[' REG ']'"""
        p[0] = Address(p[2])

    @staticmethod
    def p_addr_disp(p):
        """addr_disp : '[' REG ':' expression ']'"""
        p[0] = AddressDisp(p[2], p[4])

    @staticmethod
    def p_addr_disp_reversed(p):
        """addr_disp : '[' expression ':' REG ']'"""
        p[0] = AddressDisp(p[4], p[2])

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
        """data_operands   : data_operands ',' data_operand"""
        p[0] = p[1]
        p[0].append(p[3])


def parse(data: str) -> List[Union[Pointer, BaseInstruction]]:
    return Parser().parse(data)
