#!/usr/bin/env python
"""
Script pour tester que l'harmonisation des fichiers est correcte.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

def test_secret_manager():
    """Test du gestionnaire de secrets."""
    try:
        from config.secrets import get_secret, get_section_secrets
        print("\n✅ Import du gestionnaire de secrets réussi")
        
        gitlab_secrets = get_section_secrets('gitlab')
        print(f"✅ Récupération des secrets GitLab: {list(gitlab_secrets.keys())}")
        
        api_url = get_secret('gitlab', 'api_url')
        print(f"✅ URL GitLab: {api_url}")
        
        return True
    except Exception as e:
        print(f"\n❌ Échec du test du gestionnaire de secrets: {e}")
        return False

def test_gitlab_client():
    """Test du client GitLab."""
    try:
        from src.extractors.gitlab import GitLabClient
        print("\n✅ Import du client GitLab réussi")
        
        client = GitLabClient()
        print(f"✅ Client GitLab initialisé: {client}")
        
        return True
    except Exception as e:
        print(f"\n❌ Échec du test du client GitLab: {e}")
        return False

def test_gitlab_users_gateway():
    """Test de la passerelle pour les utilisateurs GitLab."""
    try:
        from src.extractors.gitlab import GitLabUsersGateway, GitLabClient
        print("\n✅ Import de la passerelle utilisateurs GitLab réussi")
        
        client = GitLabClient()
        gateway = GitLabUsersGateway(client)
        print(f"✅ Passerelle utilisateurs GitLab initialisée: {gateway}")
        
        return True
    except Exception as e:
        print(f"\n❌ Échec du test de la passerelle utilisateurs GitLab: {e}")
        return False

def test_export_gitlab_users():
    """Test du script d'export des utilisateurs GitLab."""
    try:
        from scripts.export_gitlab_users import identify_bot_accounts
        print("\n✅ Import de la fonction identify_bot_accounts réussi")
        
        # Test avec un utilisateur factice
        test_users = [
            {"username": "ghost", "name": "Ghost User", "email": "ghost@example.com"}
        ]
        
        human_users, bot_users = identify_bot_accounts(test_users)
        print(f"✅ Fonction identify_bot_accounts exécutée: {len(human_users)} humains, {len(bot_users)} bots")
        
        return True
    except Exception as e:
        print(f"\n❌ Échec du test du script d'export: {e}")
        return False

def main():
    """Exécute tous les tests."""
    print("=== Vérification de l'harmonisation des fichiers ===")
    
    results = []
    results.append(("Secret Manager", test_secret_manager()))
    results.append(("GitLab Client", test_gitlab_client()))
    results.append(("GitLab Users Gateway", test_gitlab_users_gateway()))
    results.append(("Export GitLab Users", test_export_gitlab_users()))
    
    print("\n=== Résultats des tests ===")
    for name, result in results:
        status = "✅ Réussi" if result else "❌ Échec"
        print(f"{status} - {name}")
    
    # Calcul du statut global
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    print(f"\nRésultat global: {success_count}/{total_count} tests réussis")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
