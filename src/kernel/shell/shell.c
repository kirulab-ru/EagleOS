#include "shell.h"
#include "commands.h"
#include "../drivers/keyboard.h"
#include "../drivers/video.h"
#include "../drivers/sys.h"

#define SHELL_MAX_INPUT 128
static char input_buffer[SHELL_MAX_INPUT];
static unsigned int input_length = 0;

void print(const char *text)
{
    while (*text) {
        terminal_putc(*text);
        text++;
    }
}

void exec_cmd(const char *name, const char *args)
{
    unsigned int i;

    for (i = 0; i < command_count; i++) {
        if (str_cmp(name, commands[i].name) == 0) {
            commands[i].function(args);
            return;
        }
    }

    print("Unknown command.\n");
}

static void shell_process_input(void)
{
    char *name = input_buffer;
    char *args = input_buffer;

    while (*args && *args != ' ')
        args++;

    if (*args) {
        *args = '\0';
        args++;

        while (*args == ' ')
            args++;
    }

    if (*name)
        exec_cmd(name, args);

    input_length = 0;
    input_buffer[0] = '\0';
}

void shell_welcome(void)
{
    set_color(0x0B);
    print(
        "\n\n\xDA\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xBF\n"

        "\xB3                                         \xB3\n"
        "\xB3           Welcome to Eagle OS           \xB3\n"
        "\xB3                                         \xB3\n"
        "\xB3        Type 'help' for commands.        \xB3\n"
        "\xB3                                         \xB3\n"

        "\xC0\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4"
        "\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xC4\xD9\n\n\n"
    );
    set_color(0x07);
}

void shell_init(void)
{
    input_length = 0;
    input_buffer[0] = '\0';
    shell_welcome();
    print("[live@eagle]:");
    print(" ");
}

void shell_update(void)
{
    int c = keyboard_getchar();

    if (c < 0)
        return;

    if (c == '\r' || c == '\n') {
        terminal_putc('\n');
        shell_process_input();
        print("[live@eagle]:");
        print(" ");
        return;
    }

    if (c == '\b' || c == 127) {
        if (input_length > 0) {
            input_length--;
            input_buffer[input_length] = '\0';
            terminal_putc('\b');
        }
        return;
    }

    if (c == 3) {
        input_length = 0;
        input_buffer[0] = '\0';

        terminal_putc('^');
        terminal_putc('C');
        terminal_putc('\n');

        print("[live@eagle]: ");
        return;
    }

    if (c >= 32 && c <= 126 &&
        input_length < SHELL_MAX_INPUT - 1) {

        input_buffer[input_length++] = (char)c;
        input_buffer[input_length] = '\0';

        terminal_putc((char)c);
    }
}
