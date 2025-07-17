"""
Script d'exportation des utilisateurs GitLab au format CSV.

Ce script extrait les utilisateurs de GitLab et les exporte dans un fichier CSV
pour faciliter leur intégration dans d'autres systèmes.
"""
import sys
import os
from pathlib import Path
import csv
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

# Pour résoudre les problèmes d'encodage sur Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.extractors.gitlab import GitLabClient, GitLabUsersGateway
from config.secrets import get_section_secrets

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Champs des utilisateurs à exporter
USER_FIELDS = [
    "id", "username", "name", "email", "state", "created_at", 
    "last_activity_on", "is_admin", "organization", "location",
    "public_email", "website_url", "bio", "web_url"
]

def export_users_to_csv(users: List[Dict[str, Any]], output_path: str) -> None:
    """
    Exporte la liste des utilisateurs dans un fichier CSV.
    
    Args:
        users: Liste des utilisateurs à exporter
        output_path: Chemin du fichier CSV de sortie
    """
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=USER_FIELDS)
            writer.writeheader()
            
            for user in users:
                # Créer un dictionnaire avec uniquement les champs que nous voulons exporter
                user_data = {field: user.get(field, '') for field in USER_FIELDS}
                writer.writerow(user_data)
                
        logger.info(f"Export CSV terminé. {len(users)} utilisateurs exportés dans {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'export CSV: {e}")
        return False

def main():
    print("\n=== Exportation des utilisateurs GitLab au format CSV ===\n")
    
    try:
        # Récupérer les secrets de GitLab
        gitlab_config = get_section_secrets("gitlab")
        
        print(f"Configuration GitLab:")
        print(f"- API URL: {gitlab_config.get('api_url')}")
        print(f"- Vérification SSL: {'Activée' if gitlab_config.get('verify_ssl', True) else 'Désactivée'}")
        
        # Créer le client GitLab
        gitlab_client = GitLabClient(gitlab_config)
        
        # Créer la passerelle pour les utilisateurs
        users_gateway = GitLabUsersGateway(gitlab_client)
        
        # Récupérer tous les utilisateurs
        print("\nRécupération des utilisateurs de GitLab...")
        params = {
            "active": True,  # Uniquement les utilisateurs actifs
            "per_page": 100  # Nombre maximum d'utilisateurs par page
        }
        
        users = users_gateway.get_users(params)
        print(f"Nombre d'utilisateurs récupérés: {len(users)}")
        
        if not users:
            print("Aucun utilisateur à exporter.")
            return
        
        # Créer le dossier de sortie s'il n'existe pas
        output_dir = root_dir / "data" / "output" / "gitlab"
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom du fichier avec horodatage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"gitlab_users_{timestamp}.csv"
        
        # Exporter les utilisateurs
        print(f"\nExportation des utilisateurs vers {output_file}...")
        export_result = export_users_to_csv(users, str(output_file))
        
        if export_result:
            print(f"\nExportation terminée avec succès!")
            print(f"Fichier créé: {output_file}")
        else:
            print(f"\nL'exportation a échoué.")
            
    except Exception as e:
        print(f"\nErreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
