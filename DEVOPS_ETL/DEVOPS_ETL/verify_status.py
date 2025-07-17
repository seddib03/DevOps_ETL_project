#!/usr/bin/env python
"""
Script pour vérifier l'état de l'harmonisation et écrire un statut dans un fichier.
"""
import sys
import os
from pathlib import Path

# Créer un fichier de statut
status_file = Path(__file__).parent / "harmonization_status.txt"

with open(status_file, "w", encoding="utf-8") as f:
    f.write("Début de la vérification\n")
    
    try:
        from config.secrets import get_secret, get_section_secrets
        f.write("✅ Import du gestionnaire de secrets réussi\n")
        
        gitlab_secrets = get_section_secrets('gitlab')
        f.write(f"✅ Secrets GitLab: {list(gitlab_secrets.keys())}\n")
    except Exception as e:
        f.write(f"❌ Erreur gestionnaire de secrets: {str(e)}\n")
    
    try:
        from src.extractors.gitlab import GitLabClient
        f.write("✅ Import du client GitLab réussi\n")
    except Exception as e:
        f.write(f"❌ Erreur client GitLab: {str(e)}\n")
    
    try:
        from src.extractors.gitlab import GitLabUsersGateway
        f.write("✅ Import de la passerelle utilisateurs GitLab réussi\n")
    except Exception as e:
        f.write(f"❌ Erreur passerelle utilisateurs: {str(e)}\n")
    
    try:
        from scripts.export_gitlab_users import identify_bot_accounts
        f.write("✅ Import de identify_bot_accounts réussi\n")
        
        # Test simple
        test_users = [{"username": "ghost", "name": "Ghost User"}]
        human_users, bot_users = identify_bot_accounts(test_users)
        f.write(f"✅ Test identify_bot_accounts: {len(human_users)} humains, {len(bot_users)} bots\n")
    except Exception as e:
        f.write(f"❌ Erreur script d'export: {str(e)}\n")
        
    f.write("\nTest terminé\n")

print(f"Vérification terminée. Voir {status_file} pour les détails.")
