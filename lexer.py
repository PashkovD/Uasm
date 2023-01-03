from typing import Any, Dict

from ply import *
from ply.lex import Token
from typeguard import typechecked

from instructions import EnumInstIMM, EnumInstReversible, EnumInstLeft, EnumInstClear
from regs import Reg8, Reg16


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
        'INTEGER', 'STRING', 'REG8', 'REG16',
        'InstIMM', 'InstReversible', 'InstLeft', 'InstClear',
        'OpData', 'OpTimes', 'OpIncDec',
        'ID', 'NEWLINE'
    )

    t_ignore = ' \t'
    t_ID = '[A-Za-z_][A-Za-z0-9_]*'
    literals = ':+-[].,'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    for i in Reg8:
        _new_keyword(f"t_REG8_{i.name}", i.name, i, "REG8", locals())
    for i in Reg16:
        _new_keyword(f"t_REG16_{i.name}", i.name, i, "REG16", locals())
    for i in EnumInstIMM:
        _new_keyword(f"t_InstIMM_{i.name}", i.name, i.name, "InstIMM", locals())
    for i in EnumInstReversible:
        _new_keyword(f"t_InstReversible_{i.name}", i.name, i.name, "InstReversible", locals())
    for i in EnumInstLeft:
        _new_keyword(f"t_InstLeft_{i.name}", i.name, i.name, "InstLeft", locals())
    for i in EnumInstClear:
        _new_keyword(f"t_InstClear_{i.name}", i.name, i.name, "InstClear", locals())

    del i

    _new_keyword("t_DATA", "data", "DATA", "OpData", locals())
    _new_keyword("t_TIMES", "times", "TIMES", "OpTimes", locals())

    _new_keyword("t_INC", "inc", EnumInstReversible.ADD.name, "OpIncDec", locals())
    _new_keyword("t_DEC", "dec", EnumInstReversible.SUB.name, "OpIncDec", locals())

    @staticmethod
    def t_STRING(t):
        r'\".*?\"'
        t.value = t.value[1:-1]
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
