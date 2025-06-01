# Named Resolve

**Catégorie** : Active Directory/Réaliste  
**Difficulté** : Intro  
**Author**: HF47

## Description du challenge

Dans la station, chaque nom a sa place — mais certains ne devraient jamais être résolus.
Un secteur du réseau reste ignoré par la majorité des opérateurs. Pourtant, ceux qui savent où chercher y trouvent souvent bien plus qu’ils ne l’imaginaient.

## Solution

### 1. Reconnaissance initiale

Tout d'abord, vérifions que nous avons accès à un contrôleur de domaine avec le service DNS actif :

```bash
hf47@kali> nmap -p 53,135,389,445,5985 192.168.56.4
Starting Nmap 7.94 ( https://nmap.org ) at 2023-05-15 10:00 CEST
Nmap scan report for 192.168.56.4
Host is up (0.00056s latency).

PORT     STATE SERVICE
53/tcp   open  domain
135/tcp  open  msrpc
389/tcp  open  ldap
445/tcp  open  microsoft-ds
5985/tcp open  wsman

Nmap done: 1 IP address (1 host up) scanned in 0.42 seconds
```

Nous avons identifié un serveur avec le port 53 (DNS) ouvert. Le port 5985 (WinRM) est également ouvert, ce qui nous permettra d'utiliser Evil-WinRM pour nous connecter.

### 2. Tentative de transfert de zone classique (qui échoue)

Essayons d'abord un transfert de zone classique avec `dig` :

```bash
hf47@kali> dig @192.168.56.4 challenge.ctfcorp.local AXFR

; <<>> DiG 9.18.12 <<>> @192.168.56.4 challenge.ctfcorp.local AXFR
; (1 server found)
;; global options: +cmd
; Transfer failed.
```

Le transfert de zone échoue, ce qui était attendu car l'administrateur a désactivé cette fonctionnalité.

### 3. Connexion via Evil-WinRM

Nous allons maintenant utiliser Evil-WinRM pour nous connecter au serveur :

```bash
hf47@kali> evil-winrm -i 192.168.56.4 -u Player1 -p test

Evil-WinRM shell v3.4
Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Player1\Documents>
```

### 4. Étape par étape : découverte des zones DNS avec dnscmd

#### 4.1 Utilisation de dnscmd pour lister les zones

Les membres du groupe CTF_Player (qui est ajouté au groupe DnsAdmins) peuvent utiliser `dnscmd` pour énumérer les zones DNS :

```powershell
*Evil-WinRM* PS C:\Users\Player1\Documents> dnscmd localhost /enumzones

Enumerated zone list:
    Zone count = 5
    challenge.ctfcorp.local
    ctfcorp.local
    dev.ctfcorp.local
    internal.ctfcorp.local
    test.ctfcorp.local

Command completed successfully.
```

#### 4.2 Énumération des enregistrements dans la zone challenge.ctfcorp.local

Maintenant que nous connaissons les zones disponibles, énumérons les enregistrements de la zone `challenge.ctfcorp.local` :

```powershell
*Evil-WinRM* PS C:\Users\Player1\Documents> dnscmd localhost /enumrecords challenge.ctfcorp.local .

Enumerated zone: challenge.ctfcorp.local
    . [Aging:3600] 3600 A 192.168.56.4
    . [Aging:3600] 3600 NS dc1.ctfcorp.local.
    admin [Aging:3600] 3600 A 192.168.56.4
    api [Aging:3600] 3600 A 192.168.56.4
    flag [Aging:3600] 3600 TXT "404CTF{DNS_Z0n3_W4lk1ng_Byp4ss3s_Tr4nsf3r_R3str1ct10ns!}"
    info [Aging:3600] 3600 TXT "Ceci est un serveur de challenge pour le 404CTF 2025"
    service [Aging:3600] 3600 A 192.168.56.4
    www [Aging:3600] 3600 A 192.168.56.4

Command completed successfully.
```

#### 4.3 Recherche ciblée d'enregistrements TXT

Pour filtrer uniquement les enregistrements TXT, nous pouvons utiliser PowerShell pour traiter la sortie de `dnscmd` :

```powershell
*Evil-WinRM* PS C:\Users\Player1\Documents> dnscmd localhost /enumrecords challenge.ctfcorp.local . | Select-String -Pattern "TXT"

    flag [Aging:3600] 3600 TXT "404CTF{DNS_Z0n3_W4lk1ng_Byp4ss3s_Tr4nsf3r_R3str1ct10ns!}"
    info [Aging:3600] 3600 TXT "Ceci est un serveur de challenge pour le 404CTF 2025"
```

### 7. Flag

Le flag est donc : `404CTF{DNS_Z0n3_W4lk1ng_Byp4ss3s_Tr4nsf3r_R3str1ct10ns!}`
