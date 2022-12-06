import sys
from argparse import ArgumentParser
from pathlib import PurePosixPath
from typing import List

from machine_file import MachineFile
from parser import parse, Pointer


def compile_code(text: str) -> bytes:
    result = parse(text)
    data = MachineFile()
    for i in result:
        if isinstance(i, Pointer):
            data.symbols[i.name] = data.current_pos
            continue
        i.process().serialize(data)
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
        output = PurePosixPath(names.file).stem + ".mc"

    with open(output, "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main(sys.argv)
