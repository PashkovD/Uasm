namespace uasm
    element register
end namespace

element AX?   : uasm.register + 0h
element BX?   : uasm.register + 1h
element CX?   : uasm.register + 2h
element DX?   : uasm.register + 3h

element SP?  : uasm.register + 7h

namespace uasm
    macro reg name,param
            name = 0Fh
            match param,x
                if param relativeto param element 1 & \
                   param scale 0 = 0 & \
                   param metadata 1 relativeto register
                   name = (param metadata 1 - register)
                end if
            end match
            if name = 0Fh
               err "bad register"
            end if
    end macro
end namespace


irp <mnem,opcode>,RET?,12h
    macro mnem
        db opcode
    end macro
end irp

irp <mnem,opcode>,  JMP?,08h,CALL?,011h,\
                    JE?,09h,JNE?,0Ah,\
                    JL?,0Bh,JNL?,0Ch,\
                    JG?,0Dh,JNG?,0Eh
    macro mnem imm
        db opcode, imm
    end macro
end irp

irp <mnem,opcode>, PUSH?, 0Fh, POP?, 10h, NOT?, 1Dh
    macro mnem argument
        namespace uasm
            db opcode
            match [param : disp], argument
                reg dest, param
                db 080h or dest shl 3, disp
            else match [param], argument
                reg dest, param
                db 040h or dest shl 3
            else if argument metadata 1 relativeto register
                reg dest, argument
                db dest shl 3
            else match param, argument
                db 0C0h, param
            else
                err "bad argument"
            end match
        end namespace
    end macro
end irp

irp <mnem,opcode>,  ADD?, 00h, SUB?, 02h, MOV?, 04h, CMP?, 06h,\
                    SHL?, 013h, SHR?, 015h, AND?, 017h, OR?, 01Bh, XOR?, 019h
    macro mnem argument1, argument2
        namespace uasm
            match [param : disp], argument1
                reg left, param
                reg right, argument2
                db opcode, 080h or left shl 3 or right, disp
            else match [param], argument1
                reg left, param
                reg right, argument2
                db opcode, 040h or left shl 3 or right
            else if argument1 metadata 1 relativeto register
                reg left, argument1
                match [param : disp], argument2
                    db opcode + 1
                    reg right, param
                    db 080h or right shl 3 or left, disp
                else match [param], argument2
                    db opcode + 1
                    reg right, param
                    db 040h or right shl 3 or left
                else if argument2 metadata 1 relativeto register
                    db opcode
                    reg right, argument2
                    db left shl 3 or right
                else match param, argument2
                    db opcode + 1
                    db 0C0h or left, param
                else
                    err "bad argument"
                end match
            else match param, argument1
                reg right, argument2
                db opcode, 0C0h or right, param
            else
                err "bad argument"
            end match
        end namespace
    end macro
end irp

irp <mnem,opcode>,  INC?,01h,DEC?,03h
    macro mnem argument
        namespace uasm
            reg dest, argument
            db opcode, 0C0h or dest, 1
        end namespace
    end macro
end irp
