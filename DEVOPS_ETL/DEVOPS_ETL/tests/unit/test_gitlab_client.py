"""
Test unitaire pour la connexion GitLab avec le client mis à jour qui utilise python-gitlab.

Ce module contient des tests qui vérifient que la connexion à GitLab fonctionne
correctement avec la bibliothèque python-gitlab.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ajouter le répertoire racine au path pour permettre les imports relatifs
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.secrets import get_section_secrets
from src.extractors.gitlab.gitlab_client import GitLabClient
from src.core.exceptions import APIConnectionError, APIAuthenticationError


class TestGitLabClient(unittest.TestCase):
    """Test de la classe GitLabClient mise à jour avec python-gitlab."""
    
    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.gitlab_config = get_section_secrets("gitlab")
        # Vérification des secrets nécessaires
        if not self.gitlab_config or not self.gitlab_config.get("api_url") or not self.gitlab_config.get("private_token"):
            self.skipTest("Configuration GitLab manquante ou incomplète")
            
        # Création du client
        self.client = GitLabClient(self.gitlab_config)
    
    def test_init(self):
        """Teste l'initialisation du client GitLab."""
        self.assertEqual(self.client.api_url, self.gitlab_config.get("api_url"))
        self.assertEqual(self.client.private_token, self.gitlab_config.get("private_token"))
        self.assertFalse(self.client.is_connected)
        self.assertIsNone(self.client.gl)
    
    @patch('gitlab.Gitlab')
    def test_connect_success(self, mock_gitlab):
        """Teste la connexion réussie au serveur GitLab."""
        # Configuration du mock
        mock_gl_instance = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 123
        mock_user.username = "testuser"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.is_admin = False
        
        mock_gl_instance.user = mock_user
        mock_gitlab.return_value = mock_gl_instance
        
        # Test de la connexion
        result = self.client.connect()
        
        # Vérification des appels
        mock_gitlab.assert_called_once_with(
            url=self.gitlab_config.get("api_url"),
            private_token=self.gitlab_config.get("private_token"),
            ssl_verify=self.client.verify_ssl,
            timeout=self.client.timeout,
            retry_transient_errors=True,
            per_page=self.client.items_per_page
        )
        mock_gl_instance.auth.assert_called_once()
        
        # Vérification des résultats
        self.assertTrue(result)
        self.assertTrue(self.client.is_connected)
        self.assertIsNotNone(self.client.user_info)
        self.assertEqual(self.client.user_info['username'], "testuser")
    
    @patch('gitlab.Gitlab')
    def test_connect_auth_error(self, mock_gitlab):
        """Teste la gestion des erreurs d'authentification."""
        # Configuration du mock
        mock_gl_instance = MagicMock()
        mock_gl_instance.auth.side_effect = Exception("Authentication failed")
        mock_gitlab.return_value = mock_gl_instance
        
        # Test de la connexion avec erreur
        with self.assertRaises(APIConnectionError):
            self.client.connect()
        
        # Vérification des résultats
        self.assertFalse(self.client.is_connected)
    
    @patch('gitlab.Gitlab')
    def test_make_request(self, mock_gitlab):
        """Teste la méthode _make_request."""
        # Configuration du mock
        mock_gl_instance = MagicMock()
        mock_gl_instance.http_get.return_value = {"id": 1, "name": "test"}
        mock_gitlab.return_value = mock_gl_instance
        
        # Configurer le client
        self.client.gl = mock_gl_instance
        self.client.is_connected = True
        
        # Test de la méthode
        result = self.client._make_request("GET", "/test", params={"param": "value"})
        
        # Vérification des appels
        mock_gl_instance.http_get.assert_called_once_with("test", query_data={"param": "value"})
        
        # Vérification des résultats
        self.assertEqual(result, {"id": 1, "name": "test"})
    
    @patch('gitlab.Gitlab')
    def test_get_paginated_results(self, mock_gitlab):
        """Teste la méthode _get_paginated_results."""
        # Configuration du mock
        mock_gl_instance = MagicMock()
        mock_result1 = MagicMock()
        mock_result1.attributes = {"id": 1, "name": "test1"}
        mock_result2 = MagicMock()
        mock_result2.attributes = {"id": 2, "name": "test2"}
        mock_gl_instance.http_list.return_value = [mock_result1, mock_result2]
        mock_gitlab.return_value = mock_gl_instance
        
        # Configurer le client
        self.client.gl = mock_gl_instance
        self.client.is_connected = True
        
        # Test de la méthode
        results = self.client._get_paginated_results("/test", params={"param": "value"})
        
        # Vérification des appels
        mock_gl_instance.http_list.assert_called_once_with("test", query_data={"param": "value"})
        
        # Vérification des résultats
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[1]["id"], 2)


if __name__ == '__main__':
    unittest.main()
