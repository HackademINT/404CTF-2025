# Extraction de preuves dans les logs Windows

**Catégorie** : Forensique / Analyse de logs  
**Difficulté** : Intro  
**Auteur**: HF47

## Description du challenge

Bienvenue sur la station. Une activité suspecte a été signalée… mais aucune alerte n’a été déclenchée. Tout ce que vous avez, c’est un fichier .evtx et une intuition : quelque chose s’est glissé là où personne ne regarde. Aidez nos ingénieurs à comprendre ce qui est arrivé !
## Solution

### 1. Présentation de l'outil Chainsaw

Pour ce challenge, nous allons utiliser [Chainsaw](https://github.com/WithSecureLabs/chainsaw), un outil puissant pour analyser les journaux d'événements Windows (fichiers .evtx).

Chainsaw permet de rechercher rapidement des événements spécifiques, d'extraire des informations pertinentes, et d'identifier des indicateurs de compromission.

### 2. Installation de Chainsaw

Si vous n'avez pas encore installé Chainsaw, vous pouvez le faire avec les commandes suivantes :

```bash
git clone https://github.com/WithSecureLabs/chainsaw.git
cd chainsaw
cargo build --release
```

Ou télécharger directement la dernière release depuis GitHub.

### 3. Analyse du fichier EVTX

Commençons par examiner le fichier de logs fourni :

```bash
./chainsaw info forensic-et-mat/chall-1/Security.evtx
```

Cette commande nous donne un aperçu général du fichier, notamment le nombre d'événements et la période couverte.

### 4. Recherche d'événements suspects

Utilisons le module `search` de Chainsaw pour rechercher des événements suspects ou des mots-clés qui pourraient nous indiquer la présence du flag :

```bash
./chainsaw search -i forensic-et-mat/chall-1/Security.evtx -s "404CTF"
```

Cette commande recherche le motif "404CTF" dans le fichier des logs de sécurité.

### 5. Analyse des résultats

Dans les résultats, nous trouvons un événement particulier contenant notre flag :

```
[+] Found matching event:
Event ID: 4688
Date: 2024-07-15 15:22:18.123 UTC
Message: Un nouveau processus a été créé.
    Processus: cmd.exe
    PID: 4567
    Utilisateur: SYSTEM
    Arguments: /c echo "Tâche de maintenance exécutée. Message secret: 404CTF{Ch41ns4w_3st_1d34l_p0ur_l3s_l0gs_W1nd0ws}"
```

### 6. Flag

Le flag est : `404CTF{Sch3dul3d_T4sk_3v3nts_4r3_N0t_S4f3!}`

## Explications supplémentaires

Chainsaw est particulièrement utile pour l'analyse forensique car il permet :
- De traiter rapidement de gros volumes de logs
- D'utiliser des règles de détection (comme les règles Sigma)
- D'effectuer des recherches complexes avec des expressions régulières
- De générer des chronologies d'événements

Dans ce challenge, nous avons utilisé l'approche la plus simple : la recherche directe d'un motif. Dans des scénarios plus complexes, vous pourriez avoir besoin d'analyser des corrélations entre plusieurs événements ou d'utiliser des règles Sigma pour détecter des comportements malveillants spécifiques.

