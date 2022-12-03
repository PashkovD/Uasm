from typing import Iterable


from parser import parse, Pointer
import parser

text2: str = """
    mov sp, stack
    jmp start


.print_num
    push ax
    push bx

    mov bx, ax
    shl bx, 4
    shr bx, 4
    mov bx, [table:bx]
    mov [cx:num+1], bx 
    
    shr ax, 4
    mov bx, [table:ax]
    mov [cx:num], bx 
    
    mov ax, num
    mov [cx:255], ax

    pop bx
    pop ax
    ret
  .num
    data "00", 0
  .table
    data "0123456789ABCDEF"


.print_fizz
    push ax
    mov ax, fizz
    mov [cx:255],ax
    pop ax
    ret
  .fizz
    data "FIZZ", 0


.print_buzz
    push ax
    mov ax, buzz
    mov [cx:255],ax
    pop ax
    ret
  .buzz
    data "BUZZ", 0


.print_fizzbuzz
    push ax
    mov ax, fizzbuzz
    mov [cx:255],ax
    pop ax
    ret
  .fizzbuzz
    data "FIZZBUZZ", 0

.start
    inc ax
    call print_num
    inc ax
    call print_num
    inc ax
    call print_fizz
    inc ax
    call print_num
    inc ax
    call print_buzz
    inc ax
    call print_fizz
    inc ax
    call print_num
    inc ax
    call print_num
    inc ax
    call print_fizz
    inc ax
    call print_buzz
    inc ax
    call print_num
    inc ax
    call print_fizz
    inc ax
    call print_num
    inc ax
    call print_num
    inc ax
    call print_fizzbuzz
    jmp start

.stack
"""

def decorate(data: Iterable[int]) -> str:
    data2 = ""
    codes = "0123456789ABCDEF"
    for i in data:
        data2 += fr"\x{codes[i // 16]}{codes[i % 16]}"
    return data2


def main():
    result = parse(text2)
    if result is None:
        raise Exception
    data = bytearray()
    data2 = {}
    for i in result:
        if isinstance(i, Pointer):
            data2[i.name] = len(data)
            continue
        data.extend(i.process().serialize())
    parser.id_dict = data2
    result = parse(text2)
    data = bytearray()
    for i in result:
        if isinstance(i, Pointer):
            continue
        data.extend(i.process().serialize())
    print(data2)
    print(" ".join(hex(i)[2:] for i in data))
    print(", ".join(map(str, data)))
    print(decorate(data))
    print(len(data))


if __name__ == "__main__":
    main()
