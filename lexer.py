from ply import *

from instructions import EnumInstruction
from regs import Reg

tokens = (
    'PLUS', 'MINUS', 'RBREACKET', 'LBREACKET',
    'COMMA', 'DOT', 'DOTS', 'INTEGER', 'STRING', 'REG', 'OPCODE',
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


def t_STRING(t):
    r'\".*?\"'
    t.value = t.value[1:-1]
    if len(t.value) == 1:
        t.value = ord(t.value)
        t.type = 'INTEGER'
    return t

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
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t


def t_error(t):
    raise Exception("Illegal character %s" % t.value[0])


lexer = lex.lex()
