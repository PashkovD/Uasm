from ply import yacc

from lexer import Lexer
from not_int import NotInt


class Pointer:
    def __init__(self, name: str, line: int):
        self.name: str = name
        self.line: int = line

    def __repr__(self):
        return f"Pointer({self.name}): {self.line}"


class BaseParser(Lexer):
    precedence = (
        ('left', '.'),
        ('left', '-', '+'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, input_: str, **kwargs):
        return self.parser.parse(input_, **kwargs)

    start = "code"

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
        """code : instruction
                | pointer"""
        p[0] = [p[1]]

    @staticmethod
    def p_pointer(p):
        """pointer : '.' ID"""
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
