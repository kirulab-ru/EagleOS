#include "../commands.h"
#include "../shell.h"
#include "../../drivers/sys.h"
#include "../../drivers/video.h"

void shutdown(){
    __asm {
        mov ax, 5307h
        mov bx, 0001h
        mov cx, 0003h
        int 15h
    }
}

void cmd_shutdown(const char *args)
{
    if (str_cmp(args, "now") == 0) {
        shutdown();
    } else {
        clear_screen();
        print("System will be shutdown in 15 seconds");
        sleep(15);
        shutdown();
    }
}
