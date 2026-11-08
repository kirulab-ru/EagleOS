#include "commands.h"
#include "../drivers/video.h"

const Command commands[] = {
    {"help",        cmd_help,       "all of Eagle OS commands"},
    {"echo",        cmd_echo,       "write text on screen"},
    {"clear",       cmd_clear,      "clears the screen"},
    {"shutdown",    cmd_shutdown,   "shutdown the system"},
    {"reboot",      cmd_reboot,     "reboot the system"}
};

const unsigned int command_count = sizeof(commands) / sizeof(commands[0]);
