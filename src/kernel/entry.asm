.8086
.model tiny
.code
org 100h

extern kmain_: near ptr
public _cs_, _sm_code_

_sm_code_ label near

_cs_:
    cli
    mov ax, cs
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0FFFEh
    cld
    sti

    call kmain_

khalt:
    cli
    hlt
    jmp khalt

end _cs_
