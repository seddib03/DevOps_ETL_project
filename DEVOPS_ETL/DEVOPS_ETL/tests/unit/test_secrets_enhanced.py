"""
Test unitaire pour le gestionnaire de secrets amélioré.

Ce module teste les fonctionnalités du gestionnaire de secrets
avec les conventions de nomenclature améliorées.
"""
import sys
import os
from pathlib import Path
import logging
import pytest
from unittest.mock import patch, mock_open

# Ajouter le répertoire racine au path pour permettre les imports relatifs
project_root_directory = Path(__file__).parent.parent.parent
sys.path.append(str(project_root_directory))

from config.secrets import get_secret, get_section_secrets, get_secret_manager
from config.secrets.secret_manager_enhanced import (
    get_enhanced_secret_manager,
    EnhancedSecretManager,
    SecretValidationService
)
from src.core.exceptions import ConfigurationError, SecurityError, ValidationError

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestSecretManager:
    """Tests pour le gestionnaire de secrets standard."""
    
    def test_get_secret_manager_instance(self):
        """Test de récupération de l'instance du gestionnaire de secrets."""
        secret_manager = get_secret_manager()
        assert secret_manager is not None
        assert hasattr(secret_manager, 'secrets')
    
    def test_get_section_secrets_gitlab(self):
        """Test de récupération des secrets GitLab."""
        try:
            gitlab_secrets = get_section_secrets("gitlab")
            assert isinstance(gitlab_secrets, dict)
            assert "api_url" in gitlab_secrets
            assert "private_token" in gitlab_secrets
            print(f"✅ Secrets GitLab récupérés: {list(gitlab_secrets.keys())}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des secrets GitLab: {e}")
            pytest.fail(f"Impossible de récupérer les secrets GitLab: {e}")
    
    def test_get_individual_secret(self):
        """Test de récupération d'un secret individuel."""
        try:
            gitlab_api_url = get_secret("gitlab", "api_url")
            assert gitlab_api_url is not None
            assert isinstance(gitlab_api_url, str)
            print(f"✅ URL GitLab récupérée: {gitlab_api_url}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du secret: {e}")
            pytest.fail(f"Impossible de récupérer le secret: {e}")


class TestEnhancedSecretManager:
    """Tests pour le gestionnaire de secrets amélioré."""
    
    def test_enhanced_secret_manager_initialization(self):
        """Test d'initialisation du gestionnaire de secrets amélioré."""
        try:
            enhanced_manager = get_enhanced_secret_manager("local")
            assert enhanced_manager is not None
            assert isinstance(enhanced_manager, EnhancedSecretManager)
            assert enhanced_manager._environment == "local"
            print("✅ Gestionnaire de secrets amélioré initialisé")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            pytest.fail(f"Impossible d'initialiser le gestionnaire amélioré: {e}")
    
    def test_enhanced_secret_manager_cache_statistics(self):
        """Test des statistiques de cache du gestionnaire amélioré."""
        try:
            enhanced_manager = get_enhanced_secret_manager("local")
            cache_stats = enhanced_manager.get_cache_statistics()
            
            assert isinstance(cache_stats, dict)
            assert "environment" in cache_stats
            assert "cache_size" in cache_stats
            assert "cache_hit_rate" in cache_stats
            
            print(f"✅ Statistiques de cache: {cache_stats}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des statistiques: {e}")
            pytest.fail(f"Impossible de récupérer les statistiques: {e}")


class TestSecretValidationService:
    """Tests pour le service de validation des secrets."""
    
    def test_validation_service_initialization(self):
        """Test d'initialisation du service de validation."""
        validation_service = SecretValidationService()
        assert validation_service is not None
        assert hasattr(validation_service, '_validation_rules')
        print("✅ Service de validation initialisé")
    
    def test_validate_gitlab_section(self):
        """Test de validation d'une section GitLab."""
        validation_service = SecretValidationService()
        
        # Données de test valides
        valid_gitlab_data = {
            "api_url": "https://gitlab.example.com",
            "private_token": "glpat-valid-token-123456789",
            "verify_ssl": False
        }
        
        try:
            validation_result = validation_service.validate_secret_section(
                "gitlab", valid_gitlab_data
            )
            assert validation_result["validation_successful"] is True
            assert validation_result["section_name"] == "gitlab"
            print("✅ Validation GitLab réussie")
        except ValidationError as e:
            print(f"❌ Erreur de validation: {e}")
            pytest.fail(f"Validation échouée: {e}")


def test_secrets_integration():
    """Test d'intégration complet du système de secrets."""
    print("\\n=== Test d'intégration des secrets ===")
    
    try:
        # Test du gestionnaire standard
        print("\\n1. Test du gestionnaire standard:")
        standard_manager = get_secret_manager()
        print(f"   - Sections disponibles: {list(standard_manager.secrets.keys())}")
        
        # Test du gestionnaire amélioré
        print("\\n2. Test du gestionnaire amélioré:")
        enhanced_manager = get_enhanced_secret_manager("local")
        available_sections = enhanced_manager.list_available_sections()
        print(f"   - Sections disponibles: {available_sections}")
        
        # Test de récupération des secrets GitLab
        print("\\n3. Test de récupération des secrets GitLab:")
        gitlab_secrets = enhanced_manager.get_secret_section("gitlab")
        print(f"   - Clés disponibles: {list(gitlab_secrets.keys())}")
        
        # Test des statistiques de cache
        print("\\n4. Test des statistiques de cache:")
        cache_stats = enhanced_manager.get_cache_statistics()
        print(f"   - Taille du cache: {cache_stats['cache_size']}")
        print(f"   - Taux de hit: {cache_stats['cache_hit_rate']}%")
        
        print("\\n✅ Test d'intégration terminé avec succès")
        
    except Exception as e:
        print(f"\\n❌ Erreur lors du test d'intégration: {e}")
        raise


def main():
    """Fonction principale pour exécuter les tests manuellement."""
    print("=== Tests du gestionnaire de secrets amélioré ===\\n")
    
    # Exécution des tests
    test_secrets_integration()
    
    print("\\n=== Tests terminés ===")


if __name__ == "__main__":
    main()
