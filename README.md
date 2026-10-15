# Gestion des étudiants en Python

Application de bureau pour gérer les étudiants, les promotions et leurs notes.

## Fonctionnalités

- Gestion des étudiants par filière et niveau.
- Ajout de notes et calcul des moyennes.
- Recherche, suppression et statistiques par promotion.
- Import et export CSV et Excel.
- Interface graphique Tkinter avec ttkbootstrap.

## Installation

Python 3 avec Tkinter est nécessaire.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python etud_gui.py
```

## Structure

- `etud.py` : classes métier et import/export.
- `etud_gui.py` : interface graphique.

## Limites

Projet pédagogique avec authentification de démonstration. Les exports contenant des données d'étudiants ne doivent pas être publiés. Le fichier Excel local n'est pas inclus.
