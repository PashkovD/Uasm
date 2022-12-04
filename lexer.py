from ply import *

from instructions import EnumInstruction, EnumInstImm, EnumInstReversible, EnumInstLeft, EnumInstClear
from regs import Reg


class Lexer:
    tokens = (
        'PLUS', 'MINUS', 'RBREACKET', 'LBREACKET',
        'COMMA', 'DOT', 'DOTS', 'INTEGER', 'STRING', 'REG', 'OPCODE',
        'InstImm', 'InstReversible', 'InstLeft', 'InstClear',
        'ID', 'NEWLINE'
    )

    t_ignore = ' \t'
    t_DOTS = r':'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_LBREACKET = r'\['
    t_RBREACKET = r'\]'
    t_DOT = r'\.'
    t_COMMA = r'\,'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    @staticmethod
    def t_STRING(t):
        r'\".*?\"'
        t.value = t.value[1:-1]
        if len(t.value) == 1:
            t.value = ord(t.value)
            t.type = 'INTEGER'
        return t

    @staticmethod
    def t_ID(t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        try:
            t.value = Reg[t.value.upper()]
            t.type = 'REG'
            return t
        except KeyError:
            ...
        try:
            t.value = EnumInstruction[t.value.upper()]
            t.type = 'OPCODE'
            return t
        except KeyError:
            ...

        try:
            t.value = EnumInstImm[t.value.upper()]
            t.type = 'InstImm'
            return t
        except KeyError:
            ...
        try:
            t.value = EnumInstReversible[t.value.upper()]
            t.type = 'InstReversible'
            return t
        except KeyError:
            ...
        try:
            t.value = EnumInstLeft[t.value.upper()]
            t.type = 'InstLeft'
            return t
        except KeyError:
            ...
        try:
            t.value = EnumInstClear[t.value.upper()]
            t.type = 'InstClear'
            return t
        except KeyError:
            ...
        return t

    @staticmethod
    def t_INTEGER(t):
        r'\d+'
        t.value = int(t.value)
        return t

    @staticmethod
    def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return t

    @staticmethod
    def t_error(t):
        raise Exception("Illegal character %s" % t.value[0])
