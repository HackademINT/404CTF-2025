<div align="center">
  <h1>Algorithmique quantique - <i>Quantum computing</i></h1>
</div>

## Challenges
- 🟦 Machinerie quantique
- 🟩 Grover [1/2]
- 🟧 Grover [2/2]

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
    conda create -n profondeurs python=3.13 -y
    conda activate profondeurs
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
    poetry install --with notebook
    ```