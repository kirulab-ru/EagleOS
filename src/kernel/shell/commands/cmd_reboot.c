#include "../commands.h"
#include "../shell.h"
#include "../../drivers/sys.h"
#include "../../drivers/video.h"

void reboot(){
    __asm {
        int 19h
    }
}

void cmd_reboot(const char *args)
{
    if (str_cmp(args, "now") == 0) {
        reboot();
    } else {
        clear_screen();
        print("System will be reboot in 15 seconds");
        sleep(15);
        reboot();
    }
}
