use16
org 1000h

input_buff          equ 11D0h
echo_arg            equ input_buff+5

start:

    mov ax, 4F02h
    mov bx, 0117h
    int 10h

    xor ax, ax
    mov ds, ax
    mov es, ax

    mov si, welcome_msg
    call print
    call nl
    call nl 

main:

    mov si, prompt
    call print

    mov di, input_buff
    call read_line

    mov si, input_buff
    cmp byte [si], 0
    je main

    ; [CMD] clear
    mov si, input_buff
    mov di, cmd_clear
    call strcmp 
    jc do_clear

    ; [CMD] echo <text>
    mov si, input_buff
    mov di, cmd_echo
    call match_echo
    jc do_echo

    ; [CMD] shutdown
    mov si, input_buff
    mov di, cmd_shutdown
    call strcmp
    jc do_shutdown

    ; [CMD] reboot
    mov si, input_buff
    mov di, cmd_reboot
    call strcmp
    jc do_reboot

    mov si, cmd_not_found
    call print
    call nl
    jmp main

do_clear:
    
    mov ah, 02h
    mov bh, 00h
    mov dh, 00h
    mov dl, 00h
    
    mov ah, 06h
    mov al, 00h
    mov cx, 0000h
    mov dx, 0AFFFh
    int 10h 
    jmp main

do_echo:
    
    mov si, echo_arg
    call print
    call nl
    jmp main

do_reboot:

    int 19h

do_shutdown:
    
    mov ax, 5307h
    mov bx, 0001h
    mov cx, 0003h
    int 15h

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

read_line:
    xor cx, cx
    mov si, di

.read_key:
    
    mov ah, 00h
    int 16h
    
    cmp al, 03h
    je .ctrl_c
    
    cmp al, 0Dh
    je .enter

    cmp al, 08h
    je .backspace

    cmp al, 0E0h
    je .extended

    cmp cx, 7Fh
    jae .read_key
    stosb
    mov ah, 0Eh
    mov bh, 00h
    int 10h
    inc cx
    jmp .read_key

.ctrl_c:

    mov ah, 0Eh
    mov al, '^'
    int 10h
    mov al, 'C'
    int 10h
    call nl

    jmp main

.backspace:

    cmp cx, 0
    je .read_key
    dec di
    dec cx 
    mov ah, 0Eh
    mov al, 08h 
    int 10h
    mov al, ''
    int 10h
    mov al, 08h 
    int 10h
    jmp .read_key

.extended:

    mov ah, 00h
    int 16h
    cmp ah, 4Bh
    je .cursor_left
    jmp .read_key

.cursor_left:

    cmp di, si 
    je .read_key
    dec di 
    dec cx
    mov ah, 0Eh
    mov al, 08h
    int 10h 
    jmp .read_key

.cursor_right:

    cmp cx, 7Fh
    jae .read_key
    inc di
    inc cx
    mov ah, 0Eh
    mov al, ''
    int 10h
    mov al, 08h
    int 10h
    jmp .read_key

.enter: 

    mov al, 00h
    stosb
    call nl
    ret 

strcmp:

    mov al, [si]
    cmp al, [di]
    jne .not_equal
    or al, al
    je .equal
    inc si
    inc di
    jmp strcmp

.not_equal:
    clc
    ret

.equal:
    stc
    ret 

match_echo:
    mov cx, 4

.compare:
    mov al, [si]
    cmp al, [di]
    jne strcmp.not_equal
    inc si
    inc di
    loop .compare
    cmp byte [si], 20h
    je strcmp.equal
    jmp strcmp.not_equal

nl:
    mov ah, 0Eh
    mov al, 0Dh
    int 10h
    mov al, 0Ah
    int 10h
    ret

welcome_msg         db 'Welcome to Eagle OS', 0
prompt              db '[live@eagle]: ', 0
cmd_not_found       db 'Command not found.', 0
cmd_clear           db 'clear', 0
cmd_echo            db 'echo', 0
cmd_reboot          db 'reboot', 0
cmd_shutdown        db 'shutdown', 0



times 512-($-$$)     db 0

