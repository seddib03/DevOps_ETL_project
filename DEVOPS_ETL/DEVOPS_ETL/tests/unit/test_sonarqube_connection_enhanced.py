"""
Test unitaire pour la connexion SonarQube.

Ce module teste la connexion et les fonctionnalités de base
du client SonarQube avec les conventions améliorées.
"""
import sys
import pytest
from pathlib import Path
from typing import Dict, Optional
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine au path pour permettre les imports relatifs
project_root_directory = Path(__file__).parent.parent.parent
sys.path.append(str(project_root_directory))

from src.core.config import ConfigManager
from src.core.logging import configure_logging
from src.extractors.sonarqube.sonarqube_client import SonarQubeClient
from src.extractors.sonarqube.projects_gateway import SonarQubeProjectsGateway
from src.core.exceptions import APIAuthenticationError, ConnectionError

# Configuration du logging
configure_logging()
import logging
logger = logging.getLogger(__name__)


class TestSonarQubeConnection:
    """Tests pour la connexion SonarQube."""
    
    def test_sonarqube_config_loading(self):
        """Test du chargement de la configuration SonarQube."""
        try:
            config_manager = ConfigManager()
            sonarqube_config = config_manager.get_secrets("sonarqube")
            
            assert isinstance(sonarqube_config, dict)
            assert "url" in sonarqube_config
            assert "token" in sonarqube_config
            
            print(f"✅ Configuration SonarQube chargée: {list(sonarqube_config.keys())}")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la configuration: {e}")
            pytest.fail(f"Impossible de charger la configuration SonarQube: {e}")
    
    def test_sonarqube_client_initialization(self):
        """Test d'initialisation du client SonarQube."""
        try:
            config_manager = ConfigManager()
            sonarqube_config = config_manager.get_secrets("sonarqube")
            
            sonarqube_client = SonarQubeClient(sonarqube_config)
            assert sonarqube_client is not None
            
            print("✅ Client SonarQube initialisé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du client: {e}")
            pytest.fail(f"Impossible d'initialiser le client SonarQube: {e}")
    
    @patch('requests.get')
    def test_sonarqube_connection_validation(self, mock_get):
        """Test de validation de la connexion SonarQube."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "9.9.0"}
        mock_get.return_value = mock_response
        
        try:
            config_manager = ConfigManager()
            sonarqube_config = config_manager.get_secrets("sonarqube")
            
            sonarqube_client = SonarQubeClient(sonarqube_config)
            connection_result = sonarqube_client.test_connection()
            
            assert connection_result is True
            print("✅ Test de connexion SonarQube réussi (mocké)")
            
        except Exception as e:
            print(f"❌ Erreur lors du test de connexion: {e}")
            pytest.fail(f"Test de connexion échoué: {e}")
    
    @patch('requests.get')
    def test_sonarqube_projects_gateway(self, mock_get):
        """Test du gateway des projets SonarQube."""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "components": [
                {"key": "project1", "name": "Project 1"},
                {"key": "project2", "name": "Project 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        try:
            config_manager = ConfigManager()
            sonarqube_config = config_manager.get_secrets("sonarqube")
            
            sonarqube_client = SonarQubeClient(sonarqube_config)
            projects_gateway = SonarQubeProjectsGateway(sonarqube_client)
            
            projects_list = projects_gateway.get_projects()
            assert isinstance(projects_list, list)
            assert len(projects_list) == 2
            
            print(f"✅ Gateway des projets testé: {len(projects_list)} projets trouvés")
            
        except Exception as e:
            print(f"❌ Erreur lors du test du gateway: {e}")
            pytest.fail(f"Test du gateway échoué: {e}")


def test_sonarqube_integration():
    """Test d'intégration complet pour SonarQube."""
    print("\\n=== Test d'intégration SonarQube ===")
    
    try:
        # Test de chargement de la configuration
        print("\\n1. Test de chargement de la configuration:")
        config_manager = ConfigManager()
        sonarqube_config = config_manager.get_secrets("sonarqube")
        
        sonarqube_url = sonarqube_config.get("url", "Non défini")
        sonarqube_token = sonarqube_config.get("token", "Non défini")
        
        print(f"   - URL SonarQube: {sonarqube_url}")
        print(f"   - Token configuré: {'Oui' if sonarqube_token != 'Non défini' else 'Non'}")
        
        # Test d'initialisation du client
        print("\\n2. Test d'initialisation du client:")
        sonarqube_client = SonarQubeClient(sonarqube_config)
        print("   - Client SonarQube initialisé")
        
        # Test de connexion réelle (optionnel)
        print("\\n3. Test de connexion (optionnel):")
        try:
            connection_result = sonarqube_client.test_connection()
            if connection_result:
                print("   - ✅ Connexion SonarQube réussie")
            else:
                print("   - ❌ Connexion SonarQube échouée")
        except Exception as conn_error:
            print(f"   - ⚠️ Test de connexion ignoré: {conn_error}")
        
        print("\\n✅ Test d'intégration SonarQube terminé")
        
    except Exception as e:
        print(f"\\n❌ Erreur lors du test d'intégration: {e}")
        raise


def main():
    """Fonction principale pour exécuter les tests manuellement."""
    print("=== Tests de connexion SonarQube ===\\n")
    
    # Exécution des tests
    test_sonarqube_integration()
    
    print("\\n=== Tests terminés ===")


if __name__ == "__main__":
    main()
