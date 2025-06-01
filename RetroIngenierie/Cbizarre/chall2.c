#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* xor(const char *input, const char* key, size_t key_length) {
    char* output = malloc(strlen(input) + 1);
    for (size_t i = 0; i < key_length; i++) {
        output[i] = input[i] ^ key[i];
    }
    return output;
}


int main(int argc, char const *argv[]) {

    if (argc != 2) {
        fprintf(stderr, "Usage: %s <password>\n", argv[0]);
        return 1;
    }

    if (strlen(argv[1]) != 0x14) {
        fprintf(stderr, "Error: Incorrect password.\n");
        return 1;
    }

    if (argv[1][5] != 'Z') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][12] != 'o') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][0] != 'f') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][18] != '1') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][7] != '%') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][3] != 'M') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][9] != 'y') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][16] != 'v') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][14] != 'n') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][1] != 'a') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][19] != 'x') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][6] != 'a') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][15] != 'M') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][8] != '3') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][4] != 'P') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][11] != 'K') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][10] != 'N') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][17] != '%') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][2] != 'V') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }
    if (argv[1][13] != '@') { fprintf(stderr, "Error: Incorrect password.\n"); exit(1); }


    const char input[] = {0x52, 0x51, 0x62, 0x0e, 0x04, 0x1c, 0x1a, 0x66, 0x54, 0x49, 0x7e, 0x2f, 0x49, 0x33, 0x02, 0x20, 0x06, 0x69, 0x02, 0x05, '\0'};

    char* result = xor(input, argv[1], 0x14);

    printf("Bravo ! Vous avez le flag ! %s\n", result);
    
    return 0;
}