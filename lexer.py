from typing import Any, Dict

from ply import *
from ply.lex import Token
from typeguard import typechecked

from instructions import EnumInstImm, EnumInstReversible, EnumInstLeft, EnumInstClear, InstData
from regs import Reg


@typechecked
def _new_keyword(name: str, rule: str, value: Any, type_: str, local: Dict[str, Any]):
    @Token(rule.lower())
    def f(t):
        t.value = value
        t.type = type_
        return t

    local[name + "_l"] = staticmethod(f)

    @Token(rule.upper())
    def f(t):
        t.value = value
        t.type = type_
        return t

    local[name + "_u"] = staticmethod(f)


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

    for i in Reg:
        _new_keyword(f"t_REG_{i.name}", i.name, i, "REG", locals())
    del i

    @staticmethod
    def t_STRING(t):
        r'\".*?\"'
        t.value = t.value[1:-1]
        return t

    @staticmethod
    def t_data_l(t):
        r'data'
        t.type = 'OpData'
        t.value = InstData
        return t

    @staticmethod
    def t_data_u(t):
        r'DATA'
        t.type = 'OpData'
        t.value = InstData
        return t

    @staticmethod
    def t_times_l(t):
        r'times'
        t.value = InstData
        t.type = 'OpTimes'
        return t

    @staticmethod
    def t_times_u(t):
        r'TIMES'
        t.value = InstData
        t.type = 'OpTimes'
        return t

    @staticmethod
    def t_ID(t):
        r'[A-Za-z_][A-Za-z0-9_]*'
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
