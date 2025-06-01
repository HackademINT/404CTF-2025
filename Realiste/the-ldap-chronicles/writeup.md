# The LDAP Chronicles

**Catégorie** : Active Directory/Réaliste  
**Difficulté** : Intro  
**Author**: HF47

## Description du challenge

Un administrateur a laissé une porte ouverte dans le système de gestion des identités. Explorez les profondeurs du répertoire pour découvrir des informations cachées. Le secret se trouve dans un des attributs des comptes utilisateurs. Saurez-vous le dénicher ?

## Solution

### 1. NMAP

Dans un premier temps on regarde si on à bien un service LDAP sur le réseau. 

```bash
hf47@kali> nmap 192.168.56.0/24                                                                                                         

Nmap scan report for 192.168.56.4
Host is up (0.00056s latency).
Not shown: 986 closed tcp ports (reset)
PORT     STATE SERVICE
53/tcp   open  domain
80/tcp   open  http
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
389/tcp  open  ldap
445/tcp  open  microsoft-ds
464/tcp  open  kpasswd5
593/tcp  open  http-rpc-epmap
636/tcp  open  ldapssl
3268/tcp open  globalcatLDAP
3269/tcp open  globalcatLDAPssl
3389/tcp open  ms-wbt-server
5985/tcp open  wsman
MAC Address: 08:00:27:6A:C3:6D (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap scan report for 192.168.56.1
Host is up (0.0000030s latency).
All 1000 scanned ports on 192.168.56.1 are in ignored states.
Not shown: 1000 closed tcp ports (reset)

Nmap done: 256 IP addresses (3 hosts up) scanned in 3.84 seconds

```

### 1. Vérification de l'accès anonyme LDAP

Nous trouvons une IP avec un service `LDAP 389/TCP`, nous savons donc que nous sommes en présence de notre AD. Vérifions l'accès anonyme LDAP :

```bash
hf47@kali> ldapsearch -x -H ldap://<LDAP_IP> -b "DC=ctfcorp,DC=local"
```

L'option `-x` utilise l'authentification simple (anonyme dans ce cas) et nous pouvons voir que la requête fonctionne, confirmant que l'accès anonyme est activé.

```bash
hf47@kali> ldapsearch -x -H ldap://192.168.56.4 -b "DC=ctfcorp,DC=local"                                                                
# extended LDIF
#
# LDAPv3
# base <DC=ctfcorp,DC=local> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# ctfcorp.local
dn: DC=ctfcorp,DC=local
objectClass: top
objectClass: domain
objectClass: domainDNS
distinguishedName: DC=ctfcorp,DC=local
[...]
```

### 2. Énumération des utilisateurs

Pour lister tous les utilisateurs avec leurs attributs :

```bash
hf47@kali> ldapsearch -x -H ldap://192.168.56.4 -b "DC=ctfcorp,DC=local" "(objectClass=user)" description department info
```

Cette commande :
- `-x` : utilise l'authentification simple
- `-H ldap://192.168.56.4` : spécifie le serveur LDAP
- `-b "DC=ctfcorp,DC=local"` : définit la base de recherche
- `"(objectClass=user)"` : filtre pour ne retourner que les utilisateurs
- `description department info` : demande ces attributs spécifiques     
### 3. Analyse des résultats

Dans les résultats, nous trouvons plusieurs utilisateurs avec différents attributs. En particulier, l'utilisateur `sarah_smith` a un attribut description intéressant :

```ldif
# sarah_smith, Users, ctfcorp.local
dn: CN=sarah_smith,CN=Users,DC=ctfcorp,DC=local
objectClass: user
description: 404CTF{Ld4P_4n0nym0us_1s_4_B4d_Pr4ct1c3!}
department: Human Resources
info: Contact for recruitment
```

### 4. Flag

Le flag est : `404CTF{Ld4P_4n0nym0us_1s_4_B4d_Pr4ct1c3!}`
