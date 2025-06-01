# Cbizarre

Catégorie : Intro

## Premier challenge Cbizarre [1/1]

### Solution

Flag : 404CTF{PAst3_mY_FL2g}

Y'a un mot de passe difficilement retrouvable par AES, mais c'est pas grave parce que on peut juste bypass ce mot de passe pour voir un lien pastebin qui contient le flag.
La solution la plus simple est donc de faire un `strings chall1` et de remarquer le lien pastebin écrit en clair dans le programme.


## Deuxième challenge Cbizarre [2/2]

### Solution

Flag : 404CTF{Cg00d&slmpL3}

Ça se décompile normalement bien avec Ghidra ou avec n'importe quel autre décompilateur. On retrouve une suite de conditions pour avoir un mot de passe valide, il suffit alors de résoudre les conditions et on trouve le mot de passe intermédiaire : `faVMPZa%3yNKo@nMv%1x` ! Grâce à ce mot de passe et quand on le lance avec ce mot de passe, nous obtenons le flag !
