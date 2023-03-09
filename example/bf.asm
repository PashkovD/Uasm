
include "uasm8.asm"

start:
    mov ax, code
  read_loop:
    db 253, 8
    mov [ax], bx
    inc ax
    cmp bx, 0
    jne read_loop

    mov bx, code
  main_loop:
    mov cx, [bx]
    inc bx
    cmp cx, '+'
    je plus
    cmp cx, '-'
    je minus
    cmp cx, '.'
    je i_out
    cmp cx, ','
    je i_in
    cmp cx, '['
    je lbr
    cmp cx, ']'
    je rbr
    cmp cx, '>'
    je rightt
    cmp cx, '<'
    je leftt

    db 255

  plus:
    mov dx, [ax]
    inc dx
    mov [ax], dx
    jmp main_loop
  minus:
    mov dx, [ax]
    dec dx
    mov [ax], dx
    jmp main_loop

  rightt:
    inc ax
    jmp main_loop
  leftt:
    dec ax
    jmp main_loop

  i_out:
    db 254, 64
    jmp main_loop

  i_in:
    db 253, 64
    jmp main_loop

  lbr:
    mov cx, [ax]
    cmp cx, 0
    jne main_loop
    mov dx, 0
      lloop:
        mov cx, [bx]
        inc bx
        cmp cx, '['
        je linc
        cmp cx, ']'
        je ldec
        jmp lloop

        linc:
          inc dx
          jmp lloop

        ldec:
          cmp dx, 0
          je main_loop
          dec dx
          jmp lloop

  rbr:
    mov dx, 0
    dec bx
    rloop:
        mov cx, [bx:-1]
        dec bx
        cmp cx, ']'
        je rinc
        cmp cx, '['
        je rdec
        jmp rloop

        rinc:
          inc dx
          jmp rloop

        rdec:
          cmp dx, 0
          je main_loop
          dec dx
          jmp rloop


code:
