#ifndef COMMANDS_H
#define COMMANDS_H

typedef void (*CommandFunc)(const char *args);

typedef struct {
    const char *name;
    CommandFunc function;
    const char *desc;
} Command;

extern const Command commands[];
extern const unsigned int command_count;

void cmd_help(const char *args);
void cmd_echo(const char *args);
void cmd_clear(const char *args);
void cmd_shutdown(const char *args);
void cmd_reboot(const char *args);

#endif
