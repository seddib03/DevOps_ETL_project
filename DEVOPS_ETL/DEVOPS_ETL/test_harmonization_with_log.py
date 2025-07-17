#!/usr/bin/env python
"""
Script pour tester que l'harmonisation des fichiers est correcte.
Ce script écrit les résultats dans un fichier de log.
"""
import sys
import os
from pathlib import Path
import traceback

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Fichier de log pour les résultats
LOG_FILE = root_dir / "harmonization_test_results.txt"

def log_message(message):
    """Écrit un message dans le fichier de log et la console."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    print(message)

def test_secret_manager():
    """Test du gestionnaire de secrets."""
    try:
        from config.secrets import get_secret, get_section_secrets
        log_message("\n✅ Import du gestionnaire de secrets réussi")
        
        gitlab_secrets = get_section_secrets('gitlab')
        log_message(f"✅ Récupération des secrets GitLab: {list(gitlab_secrets.keys())}")
        
        api_url = get_secret('gitlab', 'api_url')
        log_message(f"✅ URL GitLab: {api_url}")
        
        return True
    except Exception as e:
        log_message(f"\n❌ Échec du test du gestionnaire de secrets: {e}")
        log_message(traceback.format_exc())
        return False

def test_gitlab_client():
    """Test du client GitLab."""
    try:
        from src.extractors.gitlab import GitLabClient
        log_message("\n✅ Import du client GitLab réussi")
        
        client = GitLabClient()
        log_message(f"✅ Client GitLab initialisé: {client}")
        
        return True
    except Exception as e:
        log_message(f"\n❌ Échec du test du client GitLab: {e}")
        log_message(traceback.format_exc())
        return False

def test_gitlab_users_gateway():
    """Test de la passerelle pour les utilisateurs GitLab."""
    try:
        from src.extractors.gitlab import GitLabUsersGateway, GitLabClient
        log_message("\n✅ Import de la passerelle utilisateurs GitLab réussi")
        
        client = GitLabClient()
        gateway = GitLabUsersGateway(client)
        log_message(f"✅ Passerelle utilisateurs GitLab initialisée: {gateway}")
        
        return True
    except Exception as e:
        log_message(f"\n❌ Échec du test de la passerelle utilisateurs GitLab: {e}")
        log_message(traceback.format_exc())
        return False

def test_export_gitlab_users():
    """Test du script d'export des utilisateurs GitLab."""
    try:
        from scripts.export_gitlab_users import identify_bot_accounts
        log_message("\n✅ Import de la fonction identify_bot_accounts réussi")
        
        # Test avec un utilisateur factice
        test_users = [
            {"username": "ghost", "name": "Ghost User", "email": "ghost@example.com"}
        ]
        
        human_users, bot_users = identify_bot_accounts(test_users)
        log_message(f"✅ Fonction identify_bot_accounts exécutée: {len(human_users)} humains, {len(bot_users)} bots")
        
        return True
    except Exception as e:
        log_message(f"\n❌ Échec du test du script d'export: {e}")
        log_message(traceback.format_exc())
        return False

def main():
    """Exécute tous les tests."""
    # Réinitialiser le fichier de log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== Vérification de l'harmonisation des fichiers ===\n")
    
    log_message("=== Vérification de l'harmonisation des fichiers ===")
    
    results = []
    results.append(("Secret Manager", test_secret_manager()))
    results.append(("GitLab Client", test_gitlab_client()))
    results.append(("GitLab Users Gateway", test_gitlab_users_gateway()))
    results.append(("Export GitLab Users", test_export_gitlab_users()))
    
    log_message("\n=== Résultats des tests ===")
    for name, result in results:
        status = "✅ Réussi" if result else "❌ Échec"
        log_message(f"{status} - {name}")
    
    # Calcul du statut global
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    log_message(f"\nRésultat global: {success_count}/{total_count} tests réussis")
    
    log_message(f"\nVoir le fichier {LOG_FILE} pour les détails complets.")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
