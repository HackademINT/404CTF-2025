# Pix2Num

## Principe du challenge

Une image est convertie en un nombre binaire, puis en un nombre décimal. Ce dernier est ensuite XORé avec un nombre aléatoire de 64 bits.

## Solution

Pour retrouver la clé du XOR, il suffit de lire l'énoncé et de remarquer que la majeure partie de l'image est blanche (par exemple, en affichant le nombre en hexadécimal). On peut donc déduire la clé en effectuant un XOR entre les 64 premiers bits du nombre et `0xFFFFFFFFFFFFFFFF`.

Ensuite, le processus pour restaurer l'image initiale est entièrement réversible.

Le fichier `solve.py` démontre de la solution.

Flag : 404CTF{4n_A11eN_hA9_b33n_70UnD}