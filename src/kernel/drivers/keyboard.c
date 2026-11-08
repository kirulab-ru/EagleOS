#include "keyboard.h"

int keyboard_getchar(void)
{
    int key;

    __asm {
        mov ah, 00h
        int 16h
        xor ah, ah
        mov key, ax
    }

    return key;
}
