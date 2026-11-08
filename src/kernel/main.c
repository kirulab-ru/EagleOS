#include "shell/shell.h"
#include "drivers/video.h"
#include "drivers/sys.h"

void kmain(void)
{
    clear_screen();
    shell_init();
    for (;;) {
        shell_update();
    }
}
