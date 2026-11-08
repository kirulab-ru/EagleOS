use16
org 0x7C00

include 'build/kernel_size.inc'

KERNEL_SEGMENT    = 0x0800
KERNEL_OFFSET     = 0x0100
SECTORS_PER_TRACK = 18

start:

    cli             ; Disable hardware interrupts (We setup segment and stack)
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax 
    mov sp, 0x7C00
    sti             ; Enable hardware interrupts after setup
    cld 

    mov [boot_drive], dl
    mov word [sectors_left], KERNEL_SECTORS
    mov word [kernel_offset], KERNEL_OFFSET
    mov byte [current_cylinder], 0
    mov byte [current_head], 0
    mov byte [current_sector], 2

read_kernel:
    cmp word [sectors_left], 0
    je launch_kernel

    push ds
    push es
    push bx 
    push cx 
    push dx 
    
    mov ax, KERNEL_SEGMENT
    mov es, ax
    mov bx, [kernel_offset]

    mov ax, 0x0201
    mov ch, [current_cylinder]
    mov cl, [current_sector]
    mov dh, [current_head]
    mov dl, [boot_drive]
    int 0x13
    jc disk_err

    pop dx
    pop cx
    pop bx
    pop es
    pop ds
    
    add word [kernel_offset], 512
    dec word [sectors_left]

    inc byte [current_sector]
    cmp byte [current_sector], SECTORS_PER_TRACK + 1
    jb read_kernel

    mov byte [current_sector], 1
    cmp byte [current_head], 0
    jne next_cylinder
    mov byte [current_head], 1
    jmp read_kernel

next_cylinder:
    mov byte [current_head], 0
    inc byte [current_cylinder]
    jmp read_kernel

disk_err:
    pop dx
    pop cx 
    pop bx 
    pop es 
    pop ds
    mov si, disk_err_msg
.print_err:
    lodsb
    test al, al 
    jz .halt
    mov ah, 0x0E
    xor bh, bh
    mov bl, 0x07
    int 0x10
    jmp .print_err

.halt:
    cli
    hlt
    jmp .halt
launch_kernel:
    cli 
    mov ax, KERNEL_SEGMENT
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0xFFFE
    cld
    sti 

    push word KERNEL_SEGMENT
    push word KERNEL_OFFSET
    retf

boot_drive   db 0
current_cylinder db 0
current_head db 0
current_sector db 0
sectors_left dw 0
kernel_offset dw 0 
disk_err_msg db 'Disk read error', 0

times 510-($-$$) db 0
dw 0AA55h
