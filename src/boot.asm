use16
org 7C00h

start:

    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax 
    mov sp, 7C00h

    ; Clear screen
    mov ah, 06h
    mov al, 00h
    mov bh, 07h
    mov cx, 0000h
    mov dx, 184Fh
    int 10h 

    ; Reset cursor position
    mov ah, 02h
    mov bh, 00h
    mov dh, 00h
    mov dl, 00h
    int 10h

    ; Read sector 2 from floppy drive
    mov ah, 02h
    mov al, 01h
    mov ch, 00h
    mov cl, 02h
    mov dh, 00h
    mov dl, 00h 
    mov bx, 1000h
    int 13h
    jc kernel_error

    ; Moving to the Kernel
    jmp 1000h

kernel_error:
    mov si, error_msg
    call print

print:
    mov ah, 0Eh

.next:
    lodsb
    or al, al
    jz .done
    int 10h
    jmp .next
.done:
    ret

error_msg db 'Kernel error', 0

times 510-($-$$) db 0
dw 0AA55h
