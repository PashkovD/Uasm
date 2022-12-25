from ply import *

from instructions import EnumInstImm, EnumInstReversible, EnumInstLeft, EnumInstClear, InstData
from regs import Reg


class Lexer:
    tokens = (
        'INTEGER', 'STRING', 'REG',
        'InstImm', 'InstReversible', 'InstLeft', 'InstClear',
        'OpData', 'OpTimes', 'OpInc', 'OpDec',
        'ID', 'NEWLINE'
    )

    t_ignore = ' \t'
    literals = ':+-[].,'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    @staticmethod
    def t_STRING(t):
        r'\".*?\"'
        t.value = t.value[1:-1]
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

        if t.value.upper() == "DATA":
            t.value = InstData
            t.type = 'OpData'
            return t

        if t.value.upper() == "TIMES":
            t.value = InstData
            t.type = 'OpTimes'
            return t

        if t.value.upper() == "INC":
            t.value = EnumInstReversible.ADD
            t.type = 'OpInc'
            return t

        if t.value.upper() == "DEC":
            t.value = EnumInstReversible.SUB
            t.type = 'OpDec'
            return t

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
    def t_INTEGER_char(t):
        r"'.'"
        t.value = ord(t.value[1])
        t.type = "INTEGER"
        return t

    @staticmethod
    def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return t

    @staticmethod
    def t_error(t):
        raise Exception("Illegal character %s" % t.value[0])
