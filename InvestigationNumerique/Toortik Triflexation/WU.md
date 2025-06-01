## Toortik Triflexation [1/2] - Analyse forensique
Ayant un dump mémoire, on peut utiliser l'outil volatility3. La première chose à faire est de trouver l'OS et le kernel utilisé par l'utilisateur grâce au plugin `banners` :
`Linux version 6.11.0-17-generic (buildd@lcy02-amd64-038) (x86_64-linux-gnu-gcc-13 (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0, GNU ld (GNU Binutils for Ubuntu) 2.42) #17~24.04.2-Ubuntu SMP PREEMPT_DYNAMIC  (Ubuntu 6.11.0-17.17~24.04.2-generic 6.11.11)`

On doit alors trouver ou créer l'ISF (Intermediate Symbols File). Pour ce chall, vous pouviez les chercher en ligne sur ce github : https://github.com/Abyss-W4tcher/volatility3-symbols/tree/master/Ubuntu/amd64/6.11.0/17/generic. 
Si vous vouliez créer vous même votre ISF, vous pouvez par exemple suivre ce tuto : https://cpuu.hashnode.dev/how-to-perform-memory-forensic-analysis-in-linux-using-volatility-3.


A présent on peut lancer l'analyse !


Déjà, pour le nom du module kernel, on pouvait utiliser le plugin `linux.hidden_modules.Hidden_modules`. On l'a directement : `chall`.

Ensuite on nous parle de période executée, ce qui peut clairement nous faire penser à un cron ! On va donc chercher dans le fichier qui répertorie les cron de l'utilisateur root, à savoir `/var/spool/cron/crontabs/root`. En dumpant le fichier on a l'information suivante :
`/10 * * * * /snap/firefox/.config/config-firefox`

On a donc à la fois la période (`00:10:00`) et le nom du binaire : `/snap/firefox/.config/config-firefox`.

Pour le type de spyware, on pouvait ou bien le deviner dans le fichier `/snap/firefox/.config/logs` avec les `_MAJ_` ou on pouvait reverse ou à la limite strings le fichier `/snap/firefox/.config/firefox_utilities`.

On a alors le flag : `404CTF{/snap/firefox/.config/config-firefox:00:10:00:chall:keylogger}`



## Toortik Triflexation [2/2] - Analyse forensique
Ayant le nom du malware, on peut alors le chercher pour comprendre mieux ce qu'il s'est passé.

Pour récupérer l'executable, on peut utiliser le plugin volatility3 linux.pagecache.RecoverFs qui va récupérer tous les fichiers présents dans le dump mémoire. \
En décompressant l'output et en tapant la commande `find . -type f -name "config-firefox"`, on trouve l'executable. On peut alors ouvrir un décompilateur pour reverse ce dernier. On découvre alors que le fichier original a été chiffré avec AES CBC en utilisant la clé et le iv :   
```
unsigned char key[AES_KEY_SIZE] = {
        0x6a, 0x3f, 0x9b, 0x1e, 0x4c, 0x7a, 0x2d, 0x8e,
        0x5f, 0x0c, 0x3a, 0x7b, 0x1d, 0x4e, 0x8a, 0x6c,
        0x2b, 0x9e, 0x4f, 0x3d, 0x7c, 0x1a, 0x5e, 0x8f,
        0x0b, 0x6d, 0x2c, 0x9a, 0x4e, 0x3f, 0x7b, 0x1e
    };
unsigned char iv[AES_BLOCK_SIZE] = {
        0x1a, 0x2b, 0x3c, 0x4d,
        0x5e, 0x6f, 0x7a, 0x8b,
        0x9c, 0xad, 0xbe, 0xcf,
        0xda, 0xeb, 0xfc, 0x0f
    };
```
  
Puis le fichier a été envoyé via https au serveur distant `10.0.2.4`.\
On remarque également, que le sslkeylogfile a été trigger pendant l'execution ce qui nous permettra de déchiffrer les paquets TLS.

A présent, on ouvre le fichier de capture de réseau et on détecte les trames TLS qui nous sont utiles. On va donc retrouver "manuellement" le sslkeylogfile. En utilisant les commandes strings et grep on reconstruit ce dernier : \
`strings rootkit_exfiltration.elf | grep SERVER_HANDSHAKE_TRAFFIC_SECRET`
`strings rootkit_exfiltration.elf | grep EXPORTER_SECRET`
`strings rootkit_exfiltration.elf | grep SERVER_TRAFFIC_SECRET_0`
`strings rootkit_exfiltration.elf | grep CLIENT_HANDSHAKE_TRAFFIC_SECRET`
`strings rootkit_exfiltration.elf | grep CLIENT_TRAFFIC_SECRET_0`

On obtient ainsi le fichier :   
```
SERVER_HANDSHAKE_TRAFFIC_SECRET 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b a77af2eea2726ffd6fe63fe8662fa2233b12ca182c7ca0f641b86937ea821b1a7c2138eca63e2963c66ea559eb85cffe
EXPORTER_SECRET 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 0dd78f3e40cb00a51c8d33ecde17d52f181054a6274c3e59181ae024815932c89aeb4136c19c14c46c36e2786ee8577e
SERVER_TRAFFIC_SECRET_0 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 0efc9918b3e23872a7cb1458b8f19802d3e3ee3abe4c1a7dd7555a1a8929ec95d84cf67d604725f10b70aa7531e45436
CLIENT_TRAFFIC_SECRET_0 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 8bd3531ac9764f9250a12f85c5220815a8f6a8510c046f8bc2ff022c92fdbdb778972697993e8e60d4bd58a2dfb85125
CLIENT_HANDSHAKE_TRAFFIC_SECRET 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 021e1b83b338a2ff782de1e5c438a9050b70b86c13a0bbedc12a480dcde1e8f80e4347b1323aca0dd553acbc427265
```
On se rend compte que le `CLIENT_HANDSHAKE_TRAFFIC_SECRET` n'est pas de la bonne longueur (manque 2 caractères), on fait donc une attaque bruteforce pour déchiffrer les paquets TLS. Script : 

```
import os
import subprocess

partial_secret = "021e1b83b338a2ff782de1e5c438a9050b70b86c13a0bbedc12a480dcde1e8f80e4347b1323aca0dd553acbc427265"
client_random = "4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b"
label = "CLIENT_HANDSHAKE_TRAFFIC_SECRET"
pcap_file = "rootkit_complet/network.pcapng"

frame_to_check = 7045

base_keylog = """SERVER_HANDSHAKE_TRAFFIC_SECRET 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b a77af2eea2726ffd6fe63fe8662fa2233b12ca182c7ca0f641b86937ea821b1a7c2138eca63e2963c66ea559eb85cffe
EXPORTER_SECRET 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 0dd78f3e40cb00a51c8d33ecde17d52f181054a6274c3e59181ae024815932c89aeb4136c19c14c46c36e2786ee8577e
SERVER_TRAFFIC_SECRET_0 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 0efc9918b3e23872a7cb1458b8f19802d3e3ee3abe4c1a7dd7555a1a8929ec95d84cf67d604725f10b70aa7531e45436
CLIENT_TRAFFIC_SECRET_0 4e9152602145711b9af18fec5cd0e270386509b8e41e1b0e4a54206b6cd2b86b 8bd3531ac9764f9250a12f85c5220815a8f6a8510c046f8bc2ff022c92fdbdb778972697993e8e60d4bd58a2dfb85125
"""

for i in range(256):
    suffix = f"{i:02x}"
    suffix == "f8"
    full_secret = partial_secret + suffix

    with open("temp_sslkeylogfile.txt", "w") as f:
        f.write(base_keylog)
        f.write(f"{label} {client_random} {full_secret}\n")

    cmd = [
        "tshark",
        "-r", pcap_file,
        "-Y", f"frame.number == {frame_to_check}",
        "-o", "tls.keylog_file:temp_sslkeylogfile.txt",
        "-V"
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)

        if b"HTTP" in output:
            print(f"\n✅ Packet {frame_to_check} is decrypted with: {full_secret}")
            break

    except subprocess.CalledProcessError:
        pass
```

Après déchiffrement, on remarque une requête HTTP POST. On télécharge alors le fichier uploadé. Cependant, ce dernier est illisible mais on se rappelle qu'il a été chiffré avec AES.

A présent, on peut faire un petit script python pour déchiffrer notre fichier :
```
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import sys

def decrypt_file(input_filename, key, iv):
    with open(input_filename, 'rb') as infile:
        encrypted_data = infile.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    print(decrypted_data)

if __name__ == "__main__":
    key = bytes([
        0x6a, 0x3f, 0x9b, 0x1e, 0x4c, 0x7a, 0x2d, 0x8e,
        0x5f, 0x0c, 0x3a, 0x7b, 0x1d, 0x4e, 0x8a, 0x6c,
        0x2b, 0x9e, 0x4f, 0x3d, 0x7c, 0x1a, 0x5e, 0x8f,
        0x0b, 0x6d, 0x2c, 0x9a, 0x4e, 0x3f, 0x7b, 0x1e
    ])
    
    iv = bytes([
        0x1a, 0x2b, 0x3c, 0x4d,
        0x5e, 0x6f, 0x7a, 0x8b,
        0x9c, 0xad, 0xbe, 0xcf,
        0xda, 0xeb, 0xfc, 0x0f
    ])

    decrypt_file(sys.argv[1], key, iv)
```

`404CTF{k3rn3lR00tk1t_b3tt3r_th@n_fir3f0x}`