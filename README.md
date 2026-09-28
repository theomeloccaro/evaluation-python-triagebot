# TriageBot

Outil en ligne de commande qui trie les tickets du support de *Dungeon Delivery*
avec un LLM local (Ollama).

## Prérequis

- Python 3.14
- [Ollama](https://ollama.com/download), lancé

## Installation

```bash
git clone <url-du-depot>
cd <dossier-du-depot>
python -m venv .venv
```

Activer le venv :

- Windows (PowerShell) : `.\.venv\Scripts\Activate.ps1`
- Windows (cmd) : `.venv\Scripts\activate.bat`
- macOS / Linux : `source .venv/bin/activate`

Puis :

```bash
python -m pip install -r requirements.txt
ollama pull llama3.2:3b
```

## Lancement

```bash
python -m triagebot
```

Options : `-i` fichier de tickets (défaut `tickets.json`), `-m` modèle Ollama
(défaut `llama3.2:3b`), `--no-drafts` pour ne pas générer les brouillons.

Le programme affiche un tableau de bord et crée :

- `results.json` : chaque ticket avec son analyse, son statut, son brouillon de réponse et son escalade ;
- `report.md` : un rapport pour le manager.

## Fonctionnement

- Les tickets vides et les doublons sont écartés avant l'appel au LLM.
- Chaque réponse du LLM est vérifiée. Si elle est invalide, on réessaie 2 fois, puis le ticket passe en `to_check`.
- La langue du joueur est détectée avec `langdetect`, et le brouillon doit être dans cette langue.
- L'escalade est décidée en Python, sans LLM :
  - `toxicity` → modération
  - `payment` avec urgence ≥ 4 → responsable support
  - `to_check` → relecture humaine
  - le reste → traitement standard

## Tests (bonus)

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```
