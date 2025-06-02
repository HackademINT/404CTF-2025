# _Causapscal-des-vents_ : Challenges d'IA de l'édition 2025 du 404 CTF

## Gorfoustral (1/3)
Le capitaine du vaisseau a décidé de se mettre à la mode du moment, il a changé le système d'authentification avec un Grand Modèle de Langage (GML)... C'est sûrement très peu sécurisé, vous pouvez y jeter un coup d'oeil ? 

---

Concrètement : un modèle de langage nommé Gorfoustral-1 300M a été entraîné à partir de GPT2-Medium à retenir un drapeau :
```
User: 404CTF{super_drapeau}
Assistant: False
```

Votre objectif est de récupérer le drapeau à partir du modèle. 

Les fichiers du challenge sont : 
- Les poids du modèle.
- Un script `gorfougym.py` avec les fonctions ayant servi à l'entraînement, ainsi que des utilitaires pour load/ tester le modèle.
- Un notebook pour vous présenter Transformer Lens (non nécessaire).
- Un README.md / poetry.toml pour l'installation de l'environnement.

***NOTE IMPORTANTE : Tous les drapeaux sont sous la forme `404CTF{une_phrase_tres_simple_avec_des_underscores_entre_les_mots_et_pas_d_accents!}`. Ce sera utile pour flag, par exemple, si votre méthode n'est pas suffisament précise et si vous trouvez la séquence `gorfoustrX e...`, essayez `gorfoustral_...`. Ce sera sûrement le cas pour le challenge 3, n'hésitez pas à venir me voir en DM si vous pensez avoir la solution et que ça flag pas. Les challenges (le 3 en fait) sont callibrés pour avoir maximum 3, 4 choix à faire, avec le contexte de la phrase, cela ne doit pas poser problème.***


## Gorfoustral (2/3)
C'était effectivement peu sécurisé. Mais malheureusement notre capitaine est têtu, il a modifié le modèle et dit "c'est fix". 

J'en doute très fort.

## Gorfoustral (3/3)
Au cours d'une discussion échauffée sur la sécurité du modèle, le capitaine a glissé, il a effacé la moitié des poids ! Comment va-t-on faire pour récupérer le mot de passe maintenant ? 

On en a besoin pour sortir...

## Du tatouage
Nos journaux de bord ont été tatoués pour garantir leur intégrité. Le capitaine est très fier de sa méthode, mais je doute que ça soit suffisant. Pouvez-vous jeter un coup d'oeil ?

---
Concrètement : 
Vous avez accès au script utilisé pour créer le challenge. Il contient les méthodes pour générer normalement, générer avec tatouage, ainsi que le "chiffrement" utilisé. 

Vous avez aussi accès à trois journaux contenant des prompts générés par LLM. Dans chaque journal, la moitié des prompts ont été tatoués, l'autre moitié a été générée normalement. La méthode de tatouage utilisée est la technique de la liste rouge/verte (https://arxiv.org/abs/2301.10226), qui nécessite l'utilisation d'une clef secrète. 

Pour chaque journal, la clef secrète est identique, et  il est garanti que c'est toujours un entier entre 1 et 99999. Le drapeau final est la concaténation, avec padding, des clefs secrètes des trois journaux, dans l'ordre suivant : journal 35, 34, 33. 

Par exemple, si la clef utilisée pour le journal 35 est 33, celle pour le journal 34 est 3481, et celle pour le journal 33 est 12345, le drapeau final sera `404CTF{000330348112345}`.

Il est de plus garanti que les phrases tatouées sont au moins tatouées à partir du 20e token.  

## Installation

> [!IMPORTANT]
> Les challenges ont été conçus sur **Python 3.13** 


1. **Installation de l'environment**
    <details open>
    <summary>Avec miniconda (recommandé)</summary>
    Install miniconda: 

    ```shell
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ~/miniconda3/bin/conda init bash
    ```

    ```shell
    source ~/.bashrc
    ```

    Création de l'environnement avec Python 3.13 :
    ```shell
    conda create -n vents python=3.13 -y
    conda activate vents
    ```
    </details>

    <details>
    <summary>Avec python venv</summary>
    
    ```shell 
    python -m venv .venv 
    source .venv/bin/activate
    ```
    </details>

2. **Installation des dépendances**

    ```shell
    pip install poetry 
    poetry install
    ```
