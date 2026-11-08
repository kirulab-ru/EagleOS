#include "../commands.h"
#include "../shell.h"

void cmd_help()
{
    unsigned int i;
    
    print("\nAvailable commands:\n");
    for (i = 0; i < command_count; i++) {
        print("  ");
        print(commands[i].name);
        print(" - ");
        print(commands[i].desc);
        print("\n");
    }
    print("\n");
}
