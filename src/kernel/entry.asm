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

    ; Disable cursor before kernel loaded
    mov dx, 03D4h
    mov al, 0Ah
    out dx, al

    inc dx
    in al, dx

    or al, 20h
    out dx, al

    call kmain_

khalt:
    cli
    hlt
    jmp khalt

end _cs_
