"""
Tests unitaires pour la connexion à GitLab.

Ce module contient des tests pour vérifier que la connexion à l'API GitLab
fonctionne correctement avec les identifiants fournis dans les secrets.
"""
import os
import sys
import pytest
from pathlib import Path
import logging
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from config.secrets import get_section_secrets
import gitlab

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestGitLabConnection:
    """
    Classe de tests pour la connexion à GitLab.
    """
    
    @pytest.fixture
    def gitlab_config(self):
        """Fixture pour obtenir la configuration GitLab depuis les secrets."""
        return get_section_secrets("gitlab")
    
    @pytest.fixture
    def gitlab_client(self, gitlab_config):
        """Fixture pour créer un client GitLab."""
        # Configuration SSL
        ssl_verify = gitlab_config.get('verify_ssl', True)
        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Créer le client GitLab
        return gitlab.Gitlab(
            url=gitlab_config.get('api_url'),
            private_token=gitlab_config.get('private_token'),
            ssl_verify=ssl_verify
        )
    
    def test_gitlab_config_exists(self, gitlab_config):
        """Vérifie que la configuration GitLab existe dans les secrets."""
        assert gitlab_config is not None, "La configuration GitLab n'existe pas dans les secrets"
        assert 'api_url' in gitlab_config, "URL de l'API GitLab non définie dans les secrets"
        assert 'private_token' in gitlab_config, "Token GitLab non défini dans les secrets"
        
        # Vérifier que les valeurs ne sont pas vides
        assert gitlab_config.get('api_url'), "URL de l'API GitLab vide"
        assert gitlab_config.get('private_token'), "Token GitLab vide"
        
        logger.info(f"✅ Configuration GitLab validée: URL={gitlab_config.get('api_url')}")
    
    def test_gitlab_api_accessible(self, gitlab_client):
        """Vérifie que l'API GitLab est accessible (sans authentification)."""
        try:
            # La méthode version() ne nécessite pas d'authentification
            version_info = gitlab_client.version()
            
            assert version_info is not None, "Pas d'informations de version retournées"
            assert 'version' in version_info, "Version GitLab non retournée"
            
            logger.info(f"✅ API GitLab accessible - Version: {version_info.get('version')}")
        except Exception as e:
            logger.error(f"❌ Impossible d'accéder à l'API GitLab: {e}")
            pytest.fail(f"Échec de l'accès à l'API GitLab: {e}")
    
    def test_gitlab_authentication(self, gitlab_client):
        """Vérifie l'authentification avec le token GitLab."""
        try:
            # Tenter l'authentification
            gitlab_client.auth()
            
            # Vérifier qu'on peut accéder aux informations de l'utilisateur courant
            user = gitlab_client.user
            
            assert user is not None, "Pas d'informations utilisateur retournées"
            assert hasattr(user, 'id'), "ID utilisateur non disponible"
            assert hasattr(user, 'name'), "Nom utilisateur non disponible"
            
            logger.info(f"✅ Authentification réussie - Utilisateur: {user.name} (ID: {user.id})")
        except Exception as e:
            logger.error(f"❌ Échec de l'authentification GitLab: {e}")
            pytest.fail(f"Échec de l'authentification GitLab: {e}")
    
    def test_gitlab_users_accessible(self, gitlab_client):
        """Vérifie qu'on peut accéder aux utilisateurs GitLab."""
        try:
            # Récupérer les 5 premiers utilisateurs pour tester
            users = gitlab_client.users.list(per_page=5)
            
            assert users is not None, "Aucun utilisateur retourné"
            assert len(users) > 0, "Liste d'utilisateurs vide"
            
            # Vérifier que les utilisateurs ont les attributs attendus
            for user in users:
                assert hasattr(user, 'id'), "ID utilisateur manquant"
                assert hasattr(user, 'username'), "Nom d'utilisateur manquant"
            
            logger.info(f"✅ Accès aux utilisateurs réussi - {len(users)} utilisateurs récupérés")
            
            # Afficher quelques utilisateurs pour vérification manuelle
            for i, user in enumerate(users[:3], 1):
                logger.info(f"  {i}. {user.name} ({user.username}) - {user.state}")
                
        except Exception as e:
            logger.error(f"❌ Échec de l'accès aux utilisateurs GitLab: {e}")
            pytest.fail(f"Échec de l'accès aux utilisateurs GitLab: {e}")


if __name__ == "__main__":
    # Exécution directe des tests pour le débogage
    pytest.main(["-v", __file__])
