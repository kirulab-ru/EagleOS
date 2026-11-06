typedef unsigned char u8;
typedef unsigned short u16;

#define VGA_T ((volatile u16 far *)0xB8000000UL)   // VGA_TEXT
#define VGA_W 80                                    // VGA_WEIGHT
#define VGA_H 25                                    // VGA_HEIGHT
#define VGA_A 0x0F                                  // VGA_ATTRIBUTE  

static void clear_screen(void)
{
    volatile u16 far *video = VGA_T;
    u16 i;

    for (i = 0; i < VGA_W * VGA_H; ++i) {
        video[i] = (u16)((VGA_A << 8) | ' ');
    }
    
}

static void write_at(u16 x, u16 y, const char *text, u8 attr) 
{
    volatile u16 far *video = VGA_T;
    u16 offset = (u16)(y * VGA_W + x);
    u16 i = 0;

    while (text[i] != '\0' && x + i < VGA_W) {
        video[offset + i] = (u16)(((u16)attr << 8) | (u8)text[i]);
        ++i;
    }
}

void kmain(void)
{
    clear_screen();
    write_at(0, 0, "Welcome to Eagle OS", 0xB);

    for (;;) {
        __asm {
            hlt
        }
    }
}