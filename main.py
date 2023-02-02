import sys
from argparse import ArgumentParser
from pathlib import PurePosixPath
from typing import List, Union

from lexer import Lexer
from machine_file import MachineFile
from opcodes import ClearOpcode
from parser import Pointer
from parser8 import Parser8
from preprocessor import Preprocessor


def parse(data: str) -> List[Union[Pointer, ClearOpcode]]:
    dat1 = Lexer()
    dat1.lexer.input(data)
    dat = Preprocessor(dat1)
    dat2 = []
    while not dat.is_ended():
        dat2 += Parser8().parse(data, lexer=dat)

    return dat2


def compile_code(text: str) -> bytes:
    result = parse(text)
    data = MachineFile()
    for i in result:
        if isinstance(i, Pointer):
            data.symbols[i.name] = data.current_pos
            continue
        i.serialize(data)
    data.apply_relocations()
    return data.data


def main(args: List[str]):
    arg_parser = ArgumentParser(description="Assemble Uasm")
    arg_parser.add_argument('file', type=str, help='Input file')
    arg_parser.add_argument('-o', type=str, default=None, help='output file')
    names = arg_parser.parse_args(args[1:])

    with open(names.file) as f:
        data: bytes = compile_code(f.read())

    output = names.o
    if output is None:
        output = PurePosixPath(names.file).stem + ".bin"

    with open(output, "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main(sys.argv)
