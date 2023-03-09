
include "uasm8.asm"




    mov sp, stack
    jmp start

print_num:
    push ax
    push bx

    mov bx, ax
    shl bx, 4
    shr bx, 4
    mov bx, [bx:table]
    mov [cx:num+1], bx

    shr ax, 4
    mov bx, [ax:table]
    mov [cx:num], bx

    mov ax, num
    mov [cx:255], ax

    pop bx
    pop ax
    ret
  num:
    db "00", 0
  table:
    db "0123456789ABCDEF"

print_fizz:
    push ax
    mov ax, fizz
    mov [cx:255],ax
    pop ax
    ret
  fizz:
    db "FIZZ", 0


print_buzz:
    push ax
    mov ax, buzz
    mov [cx:255],ax
    pop ax
    ret
  buzz:
    db "BUZZ", 0


print_fizzbuzz:
    push ax
    mov ax, fizzbuzz
    mov [cx:255],ax
    pop ax
    ret
  fizzbuzz:
    db "FIZZBUZZ", 0

start:
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

stack:
