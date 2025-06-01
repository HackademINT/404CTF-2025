# Reversconstrictor

Difficulté : Facile

## Solution

Flag : 404CTF{D0_y0U_L0v3_Pyth02?1_l0v3_pYt60n!}
Les fichiers originaux sont dans /solve

Le but du challenge est de savoir utiliser les outils pour décompiler du python.
On peut remarquer en lisant le fichier avec un string et en faisant un grep avec "py" qui c'est compilé avec pyinstaller

Il existe alors un moyen de le décompiler : [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor)

`python3 pyinstctractor.py chall`

On se retouve avec beaucoup de fichiers mais seulement deux nous intéressent :

- chall.pyc
- /modules/encrypt_key.cpython-39.pyc

Pour les décompiler, il suffit d'utiliser [pycdc](https://github.com/zrax/pycdc)

`./pycdc chall.pyc > chall.py`
`./pycdc modules/encrypt_key.cpython-39.pyc > encrypt_key.cpython-39.pyc`

On obtient alors des fichiers très proches des originaux !

On remarque alors que le mot de passe est juste XOR avec une clé encrypté avec le module encrypt_key.
Le encrypt_key n'est pas réversible parce qu'il y a du décalage de bits...
Mais on s'en préocupe pas trop puisqu'on peut retrouver la clé à XORé juste en lançant le programme avec la clé trouvé dans le fichier chall.pyc décompilé
Idem pour encode_password qui est réversible bytes par bytes donc on peut juste stocker dans un petit dico tous les bytes et le reverse se fait alors très simplement

Le fichier qui permet de retrouver le mot de passe s'appelle `solve2.py` (Attention, il faut lancer le fichier en python 3.9)


Si on veut s'embêter à faire de la crypto, c'est un peu plus compliqué.
Mais on se retrouve avec 3 points d'une fonction du second degré donc on peut retrouver les racines, et à partir des racines, on peut retrouver le byte original à chaque fois (c'est d'ailleurs le principe du challenge R1R2 en crypto).
Bref, vous pouvez retrouver une solution avec cette méthode dans le fichier `solve.py` (mais l'autre est beaucoup plus simple).

## Création du challenges

 Compilé en python3.9

 `python3 -m compileall encrypt_key.py`

 `pyinstaller --onefile --noconsole --clean --add-data "__pycache__/encrypt_key.cpython-39.pyc:modules" chall.py`
