from instructions import InstData, EnumInstReversible8, EnumInstIMM8, EnumInstLeft8, EnumInstClear8
from modrm import Address, AddressDisp
from not_int import NotInt
from parser import BaseParser


class Parser8(BaseParser):

    @staticmethod
    def p_instruction_data(p):
        """instruction : OpData data_operands"""
        p[0] = InstData(p[2], line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_times(p):
        """instruction : OpTimes expression ',' data_operands"""
        if len(p[2].symbols) != 0:
            raise Exception(f"{p.slice[1].lineno}: pointers in TIMES num not suported")
        p[0] = InstData(p[4] * p[2].num, line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_inc_dec(p):
        """instruction : OpIncDec REG8"""
        p[0] = EnumInstReversible8[p[1]].value(NotInt(1), p[2], is_reversed=True, line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_imm(p):
        """instruction : InstIMM expression"""
        p[0] = EnumInstIMM8[p[1]].value(p[2], line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_rev(p):
        """instruction : InstReversible REG8 ',' REG8
                       | InstReversible addr8 ',' REG8
                       | InstReversible addr_disp8 ',' REG8
                       | InstReversible expression ',' REG8"""
        p[0] = EnumInstReversible8[p[1]].value(p[2], p[4], is_reversed=False, line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_rev_reversed(p):
        """instruction : InstReversible REG8 ',' addr8
                       | InstReversible REG8 ',' addr_disp8
                       | InstReversible REG8 ',' expression"""
        p[0] = EnumInstReversible8[p[1]].value(p[4], p[2], is_reversed=True, line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_left(p):
        """instruction : InstLeft expression
                       | InstLeft REG8
                       | InstLeft addr8
                       | InstLeft addr_disp8"""
        p[0] = EnumInstLeft8[p[1]].value(p[2], line=p.slice[1].lineno).process()

    @staticmethod
    def p_instruction_clear(p):
        """instruction : InstClear"""
        p[0] = EnumInstClear8[p[1]].value(line=p.slice[1].lineno).process()

    @staticmethod
    def p_addr(p):
        """addr8 : '[' REG8 ']'"""
        p[0] = Address(p[2])

    @staticmethod
    def p_addr_disp(p):
        """addr_disp8 : '[' REG8 ':' expression ']'"""
        p[0] = AddressDisp(p[2], p[4])

    @staticmethod
    def p_addr_disp_reversed(p):
        """addr_disp8 : '[' expression ':' REG8 ']'"""
        p[0] = AddressDisp(p[4], p[2])
