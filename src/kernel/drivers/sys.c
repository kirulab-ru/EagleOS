int str_cmp(const char *a, const char *b)
{
    while (*a && (*a == *b)) {
        a++;
        b++;
    }

    return (unsigned char)*a - (unsigned char)*b;
}

void sleep(unsigned int sec) {
    unsigned int i;

    for (i = 0; i < sec; i++) {
        __asm {
            mov ah, 86h
            mov cx, 000Fh
            mov dx, 4240h
            int 15h
        }
    }
}
