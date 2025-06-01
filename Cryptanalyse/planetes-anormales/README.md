<img src='images/logoStaff.png' style='zoom: 80%;' align=left /><h1><ins>Planètes anormales</ins></h1>

​	10 mai - 26 mai 2025

​	**Par**: `Layzix` et `SayWess`

​	**Catégorie**: Cryptographie, Elliptic Curve

​	**Difficulty**: <font color='green'>Easy</font>

# Synopsis

En tant que grand Jedi maintenant l'ordre, il est de votre devoir de partir en mission afin de résoudre toutes sortes de conflits toujours plus farfelus les uns que les autres.
Prouvez votre valeur et votre ingéniosité lors de cette étrange mission.

# Write-up

## 1 - Analyse
Tout d'abord au niveau des imports, rien de bien farfelu si ce n'est ast, mais pour l'instant, on ne possède pas plus d'infos dessus.

Ensuite, on arrive à la partie `class Curve`, mais encore ici rien de flagrant tout est bien défini comme ce doit l'être. 
On peut même observer juste à la suite une liste de courbes définies qui à priori ont l'aire sécurisée (voir [Neuromancer](https://neuromancer.sk/std/secg)). 

Vient notre première fonction `translate(curveName)` qui traduit un nom de courbe en la courbe elle-même en se basant sur la liste de courbes sécurisée juste avant.
Néanmoins, en cas d'erreur, une autre courbe est renvoyée.
```python
return Curve(0xbb0480e1f010abb2e69e7d72df5d75a23a15bc73710df25b6da04121f904e4f5,
             0xfa2bddcca24c1d80baf26cb1e1f04cf78e995c675543c9692e959f83b470a03,
             0xf7fda1b2f0c9ea506e8a125766fd9e5046fd5716630c84f526fea8ce10497829,
             (0x735d07d96821ec8bff37eb23c31081ea526ddc10abe22375518c44e043a39db0,
             0x97e570cf7c177584ddd036d9181a3f5f83307f60c92b539a2d4f479d9c9ad4bd))
```
Ce choix est assez étrange, gardons le en tête.

`createToken(name,destination)` est tout aussi intéressante. Premièrement, notre intuition sur la sécurité des courbes définies plus haut se renforce en voyant `secureCurves`.
Ensuite, notre token est créé, mais aucun traitement n'est effectuée sur les données fournies ! Gardons ce detail aussi.

`generateKey(token)` récupère ce dont elle a besoin afin de renvoyer le couple point de clef publique et clef privé.

`encryptData(flag,d,name)` quant à elle nous renverra le flag chiffré avec la clef privée et notre name en guise de nonce en utilisant AES SIV.
Peut-être qu'il y a quelque chose à faire aussi avec le nonce ?

Viens enfin la partie `chall()` où l'on doit choisir un nom avant d'embarquer pour une destination et pouvoir récupérer la clef publique ainsi que notre ciphertext.
Cependant, le seul formatage de données est effectué avec `ast.literal_eval(token)` ce qui est assez étrange.

## 2 - Idées / exploit

Deux idées s'offrent à nous pour l'instant :
1. Trouver un moyen d'exploiter la courbe custom
2. Trouver un moyen d'exploiter le nonce de l'AES

### 1 - La courbe
Il nous faut un moyen de changer la courbe sélectionnée et pour ça il va falloir se pencher sur les injections JSON.  
Le but serait de remplacer la valeur de curve. Pour cela rien de plus simple, on envoie `attacker', 'curve':'custom` en guise de nom !
Suite à ça on peut envoyer n'importe quel destination puisque l'on va l'overwrite étant donné que le nom est placé APRÈS la curve.
On peut donc récupérer le point public ainsi que le ciphertext sur cette courbe.

Ça s'annonce prometteur, continuons sur cette idée.
Mais que dire de cette courbe... Commençons à regarder les attaques connues sur les courbes elliptiques.
Après quelques vérifications, il s'avère que la courbe est anomalous (comme le laissait entendre le nom du challenge) !

En effet, #$E(F_p) = p$ signifie que la courbe est anomalous.
L'attaque repose sur deux principes :
- Les nombres p-adic, c'est-à-dire les nombres se représentant comme $\sum_{k=-n}^\infty a_kp^k$
- La réduction de courbes élliptiques modulo p

Pour plus de détail, je conseille [cet article](https://wstein.org/edu/2010/414/projects/novotney.pdf).

Un coup de SMART attack sur le point public, et plus qu'à déchiffrer le ciphertext afin de récupérer notre flag


> 404CTF{CuRv3S_0N_Th4t_Pl4N3TeS_4rE_aN0mAl0uS}