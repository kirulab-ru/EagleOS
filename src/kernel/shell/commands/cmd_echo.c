#include "../commands.h"
#include "../shell.h"

void cmd_echo(const char *args)
{
    print(args);
    print("\n");
}
