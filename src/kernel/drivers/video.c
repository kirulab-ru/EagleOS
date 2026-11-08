
#include "video.h"

typedef unsigned char u8;
typedef unsigned short u16;

#define VGA_T ((volatile u16 far *)0xB8000000UL)    // VGA_TEXT
#define VGA_W 80                                    // VGA_WEIGHT
#define VGA_H 25                                    // VGA_HEIGHT
#define VGA_A 0x0F                                  // VGA_ATTRIBUTE  

static unsigned char color = 0x07;
static unsigned short cursor_x = 0;
static unsigned short cursor_y = 0;

void reset_pos(void)
{
    cursor_x = 0;
    cursor_y = 0;
}

void set_color(unsigned char new_color)
{
    color = new_color;
}

void terminal_putc(char c)
{
    volatile unsigned short far *video = VGA_T;

    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    }
    else if (c == '\b') {
        if (cursor_x > 0)
            cursor_x--;
        video[cursor_y * VGA_W + cursor_x] =
            ((unsigned short)color << 8) | ' ';
    }
    else {
        video[cursor_y * VGA_W + cursor_x] =
            ((unsigned short)color << 8) | (unsigned char)c;

        cursor_x++;
    }

    if (cursor_x >= VGA_W) {
        cursor_x = 0;
        cursor_y++;
    }

    if (cursor_y >= VGA_H) {
        clear_screen();
    }
}

void clear_screen(void)
{
    volatile u16 far *video = VGA_T;
    u16 i;

    for (i = 0; i < VGA_W * VGA_H; ++i) {
        video[i] = (u16)((VGA_A << 8) | ' ');
    }
    
    __asm {
        mov dx, 03D4h
        mov al, 0Fh
        out dx, al

        inc dx
        xor al, al
        out dx, al

        dec dx
        mov al, 0Eh
        out dx, al

        inc dx
        xor al, al
        out dx, al
    }
    reset_pos();
}
