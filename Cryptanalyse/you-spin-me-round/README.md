<img src='images/logoStaff.png' style='zoom: 80%;' align=left /><h1><ins>You spin me round</ins></h1>

​	10 mai - 26 mai 2025

​	**Par**: `Layzix` et `SayWess`

​	**Catégorie**: Cryptographie, AES

​	**Difficulty**: <font color='orange'>Medium</font>

# Synopsis

Un duel au sommet qui en ferait tourner plus d'un. Attention droit devant !

# Write-up

## Analyse
Il s'agit d'une implémentation d'AES classique, fait main, à 1 petit détail près. En effet, on remarque l'ajout d'un paramètre `security` qui influence sur les fonctions `sub_bytes()` et `inv_sub_bytes()`, ces fonctions jouent sur l'ajout de non-linéarité dans AES à l'aide de la SBOX, et le paramètre applique `security fois` ces fonctions (cela revient à appliquer une permutation n fois).

Intéressons-nous au but du challenge maintenant. On peut choisir la `security` utilisée dans le chiffrement, puis on nous offre 2 choix : chiffrer un message ou recevoir un message chiffré, le but du challenge étant visiblement de renvoyer ce dernier message déchiffré.

On va essayer de s'interesser à ce que l'ajout de `security` apporte, et s'il n'y aurait pas une faille liée à ce paramètre justement.
On peut représenter la sbox par une matrice de permutation, ce qui peut être intéressant à regarder c'est son ordre, pour voir si $M^s = I_n$ pour un certain $s$.
```python
from sage.all import *

M = Matrix(GF(256), [ [0 if i != s_box[j] else 1 for i in range(256)] for j in range(256) ])
print(M.multiplicative_order())
# ou
p = Permutation([e + 1 for e in list(s_box)])
print(p.order())
```
On voit que $M^{277182} = I_n$, ça veut dire que si on met le paramètre `security` à 277182, l'opération `sub_bytes()` renverra juste le même élément ! On obtient donc un AES totalement linéaire !

$E(x) = A*x + b$ où $x,b \in F^{128}_2, A \in M_{128}$ et $E$ représente le chiffrement AES, $x$ les bits du message à chiffrer, la matrice $A$ est la partie linéaire d'AES (ShiftRows, MixColumns et la partie linéaire de SubBytes) et $b$ est la partie affine de AES (AddRoundKey et la partie affine de SubBytes). $A$ n'est pas dépendante de la clé, on peut donc la calculer en utilisant n'importe quelle clé, seul $b$ dépend de la clé choisie.

## Exploit

Commençons par déterminer $A$

On peut initier une instance de `BC_Starhunter` avec une clé random. Pour déterminer A, il va falloir d'abord déterminer la constance $b$ associée à cette clé.

On voit que $E(0) = A*0 + b = b$ donc il suffit de chiffrer le message (en hex) `00000000000000000000000000000000` *(1)* pour obtenir $b$.

Chaque colonne de $A$, que l'on va noter $A_j$ peut être déterminée de la façon suivante

$A_j = E(V_j) + b$ où $V_j$ est le vecteur nul sauf à la position $j$ où il vaut 1

Maintenant qu'on a $A$, il suffit de récupérer le $b$ associé au cipher du challenge !

Pour ça on demande au serveur de chiffrer le message contenant que des 0 *(1)*, on a maintenant l'AES utilisé par le serveur !

Il suffit d'utiliser cette relation pour déchiffrer le message $A^{-1}*(E(x) + b) = x$

> 404CTF{3vErY0n3_c4n7_TuRn_1nFiN1t3Ly}