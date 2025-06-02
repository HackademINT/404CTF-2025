# Pix2Num

## Énoncé

Les astronautes souhaitent vous transmettre un message ! Pour ce faire, ils ont décidé de l'envoyer via une image blanche. Cependant, vous ne recevez qu'un nombre. Que s'est-il passé ?

## Fichiers fournis

- `encrypt.py`
- `number.txt`

## Principe du challenge

Une image est convertie en un nombre binaire, puis en un nombre décimal. Ce dernier est ensuite XORé avec un nombre aléatoire de 64 bits.

## Solution

Flag : 404CTF{4n_A11eN_hA9_b33n_70UnD}

Pour retrouver la clé du XOR, il suffit de lire l'énoncé et de remarquer que la majeure partie de l'image est blanche (par exemple, en affichant le nombre en hexadécimal). On peut donc déduire la clé en effectuant un XOR entre les 64 premiers bits du nombre et `0xFFFFFFFFFFFFFFFF`.

Ensuite, le processus pour restaurer l'image initiale est entièrement réversible.

Le fichier `solve.py` démontre de la solution et le `flag.png` est le fichier qui a été utilisé pour la transformation.
