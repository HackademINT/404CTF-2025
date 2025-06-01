# Traque d'un acteur malveillant dans les logs Windows

**Catégorie** : Forensique / Analyse de logs  
**Difficulté** : Facile  
**Auteur**: HF47

## Description du challenge

Dans les profondeurs des journaux de CTFCORP, une ombre numérique persiste. 
Comme un écho dans une forêt de données, des événements ont laissé leur empreinte, 
même après que quelqu'un ait tenté de les effacer.

Votre mission :
- Explorez les recoins oubliés du journal CTFCORP_Security.evtx
- Suivez la trace des événements qui ont survécu à la tentative d'effacement

Conseils des anciens :
- Les avertissements sont comme des feuilles mortes qui bruissent dans le vent
- Les erreurs sont des cicatrices qui ne guérissent jamais
- Le temps est un fil qui relie tous les événements
- La persistance est l'art de survivre dans l'ombre
- Souvenez-vous que la première occurence peut en dire beaucoup

Le secret de CTFCORP vous attend dans les profondeurs de sa mémoire...

Le format du flag est : 404CTF{IP-PORT-USER-TASKNAME-TIMESTAMP-GROUP}

## Solution

### 1. Analyse des logs avec Chainsaw

Pour ce challenge, nous utiliserons [Chainsaw](https://github.com/WithSecureLabs/chainsaw) sans règles Sigma préétablies pour analyser manuellement les événements Windows et reconstituer la chronologie de l'attaque.

### 2. Installation de Chainsaw (si nécessaire)

```bash
git clone https://github.com/WithSecureLabs/chainsaw.git
cd chainsaw
cargo build --release
```

Ou téléchargez directement la dernière release depuis GitHub.

### 3. Identification des événements clés

D'après l'énoncé, nous devons rechercher plusieurs événements spécifiques dans l'ordre:

1. Une connexion suspecte (EventID 4624)
2. Un ajout à un groupe Administrateurs (EventID 4732)
3. Une création de tâche planifiée (EventID 4698)
4. Une exécution de processus PowerShell (EventID 4688)
5. Une tentative de nettoyage des logs (EventID 4625)

Analysons-les un par un:

#### Étape 1: Connexion suspecte (EventID 4624)

```bash
./chainsaw search -i forensic-et-mat/chall-2/CTFCORP_Security.evtx -e 4624 --json | grep -E "svc-x|10.66.77.88|4444"
```

Dans les résultats, nous identifions:
- IP source: 10.66.77.88
- Port source: 4444
- Utilisateur: svc-x
- Type de connexion: 3 (réseau)

#### Étape 2: Ajout au groupe Administrateurs (EventID 4732)

```bash
./chainsaw search -i forensic-et-mat/chall-2/CTFCORP_Security.evtx -e 4732 --json | grep -E "svc-x|Administrateurs"
```

Nous confirmons:
- Utilisateur ajouté: svc-x
- Groupe cible: Administrateurs

#### Étape 3: Création d'une tâche planifiée (EventID 4698)

```bash
./chainsaw search -i forensic-et-mat/chall-2/CTFCORP_Security.evtx -e 4698 --json
```

Nous identifions:
- Nom de la tâche: WinUpdate_Check_75312
- Utilisateur: svc-x
- Trigger: @reboot
- Commande: powershell.exe avec arguments pour exécuter payload.ps1

#### Étape 4: Exécution de la tâche planifiée (EventID 4688)

```bash
./chainsaw search -i forensic-et-mat/chall-2/CTFCORP_Security.evtx -e 4688 -s "payload.ps1" --json
```

Nous trouvons:
- Processus: powershell.exe
- Chemin du script: C:\Users\svc-x\AppData\Local\Temp\payload.ps1
- Horodatage: 2025-05-14T12:13:48.000000000Z (format Unix: 1747245628)

#### Étape 5: Tentative de nettoyage des logs (EventID 4625)

```bash
./chainsaw search -i forensic-et-mat/chall-2/CTFCORP_Security.evtx -e 4625 -s "wevtutil" --json
```

Nous confirmons:
- Erreur: "Accès refusé"
- Processus: wevtutil.exe

### 4. Extraction du timestamp pour le flag

Pour obtenir le timestamp Unix, nous pouvons utiliser un script Python simple pour convertir l'horodatage Windows:

```python
from datetime import datetime
import time

windows_time = "2025-05-14T12:13:48.000000000Z"
dt_obj = datetime.strptime(windows_time, "%Y-%m-%dT%H:%M:%S.%fZ")
unix_timestamp = int(time.mktime(dt_obj.timetuple()))
print(unix_timestamp)  # Affiche: 1747245628
```

### 5. Génération du flag

En combinant toutes les informations extraites:
- IP: 10.66.77.88
- PORT: 4444
- USER: svc-x
- TASKNAME: WinUpdate_Check_75312
- TIMESTAMP: 1747245628
- GROUP: Administrateurs

Le flag est: `CTF{10.66.77.88-4444-svc-x-WinUpdate_Check_75312-1747245628-Administrateurs}`
