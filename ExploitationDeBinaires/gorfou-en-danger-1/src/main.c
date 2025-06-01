#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

void menu() {
    puts("      __                                                                     ");
    puts("     /\\ \\                                                                  ");
    puts("    /  \\ \\      .--------------------------------------------------------. ");
    puts("   / /\\ \\ \\     |░█▀▄░█▀▀░█▀▀░█▀▀░░░█▀▀░█▀█░█▀█░█▀▀░█▀█░█░░░█▀▀░░░█░█░▀█░|");
    puts("  / / /\\ \\ \\    |░█░█░█░█░▀▀█░█░█░░░█░░░█░█░█░█░▀▀█░█░█░█░░░█▀▀░░░▀▄▀░░█░|");
    puts(" / / /__\\_\\ \\   |░▀▀░░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░░░▀░░▀▀▀|");
    puts("/ / /________\\  '--------------------------------------------------------'  ");
    puts("\\/___________/                                                              ");
}

void debug_access(void) {
    puts("Accès à l'interface de debogage...");

    __asm__(
        ".intel_syntax noprefix;"
        "push 0x0;"
        ".att_syntax;"
    );
    
    system("/bin/sh");
    return;
}

void take_command() {
    char command[0x100];
    
    printf("> ");
    read(0, command, 0x130);
    printf("Commande inconnue\n");
}

int main(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    menu();

    printf("Terminal de contrôle à distance de la base martienne Fermat\n");

    while (1) {
        take_command();
    }

    return 0;
}
