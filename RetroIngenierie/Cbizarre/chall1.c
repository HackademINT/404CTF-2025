#include <stdio.h>
#include <curl/curl.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/evp.h>

size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    size_t total_size = size * nmemb;
    fwrite(ptr, size, nmemb, stdout);
    fwrite("\n", 1, 1, stdout);
    return total_size;
}

int main(int argc, char const *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <password>\n", argv[0]);
        return 1;
    }

    const char *hex_encrypted = "b457cbb3a588fda49339744bdeff34ca0885bb3b630dbdb57fcbab5595d64a49a5338b5efe8e7cfdccb75fd137b172fa5dcc5e47748d2ed55f7ccad26829670b9eeb98ded4429c4d66f01dd5ddbd2c2668ba4b666e29d206dbcdec0e11ebb5d53a0de62612ed923beda79aea3dae06a05efe67f4c3dec8f92ecbaa3a1c16e8693ef93aa28b962e39e2bf1308b0d46f61";
    unsigned char encrypted[128];
    size_t hex_len = strlen(hex_encrypted);
    for (size_t i = 0; i < hex_len / 2; i++) {
        sscanf(&hex_encrypted[i * 2], "%2hhx", &encrypted[i]);
    }
    int ciphertext_len = hex_len / 2;
    unsigned char decrypted[128];
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int len;

    EVP_DecryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, argv[1], NULL);
    EVP_DecryptUpdate(ctx, decrypted, &len, encrypted, ciphertext_len);
    int plaintext_len = len;
    EVP_DecryptFinal_ex(ctx, decrypted + len, &len);
    plaintext_len += len;
    decrypted[plaintext_len] = '\0'; // pour l'affichage

    EVP_CIPHER_CTX_free(ctx);

    const char *expected_message = "AV5Ukqn7VMi@z08w71WCzJd6$G*EF#fhsF2taRxYxccVXwk!Uc7@QsBUgZzFVXz1p7vBlmpUILL$T7#8@#WNE#68JW$AamQYJlsrQj#NZkb%n&5DqA*pQ67X&OVp68BN";
    if (strcmp((char *)decrypted, expected_message) != 0) {
        fprintf(stderr, "Decrypted message does not match expected message\n");
        return 1;
    }
    
    CURL *curl = curl_easy_init();
    if (!curl) {
        fprintf(stderr, "Failed to initialize CURL\n");
        return 1;
    }

    curl_easy_setopt(curl, CURLOPT_URL, "https://pastebin.com/raw/n8CXuwE0");
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);

    CURLcode res = curl_easy_perform(curl);
    
    curl_easy_cleanup(curl);
    
    return 0;
}