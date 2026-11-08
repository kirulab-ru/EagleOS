#ifndef SHELL_H
#define SHELL_H

void shell_init(void);
void shell_update(void);
void print(const char *text);
void exec_cmd(const char *name, const char *args);

#endif
