#!/bin/bash
# Script pour installer les dépendances et tester la connexion GitLab

echo "=== Installation de l'environnement virtuel ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installation des dépendances ==="
pip install -r requirements.txt

echo "=== Test de connexion GitLab ==="
python scripts/test_gitlab_connection.py

echo "=== Test terminé ==="
echo "Pour activer l'environnement virtuel ultérieurement, exécutez: source venv/bin/activate"
