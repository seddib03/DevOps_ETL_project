"""
Tests unitaires pour le client GitLab harmonisé.

Ce module contient des tests complets pour la classe GitLabClient harmonisée
qui utilise la bibliothèque python-gitlab.
"""

import pytest
import responses
import json
from unittest.mock import MagicMock, patch, ANY

from src.extractors.gitlab.gitlab_client import GitLabClient
from src.core.exceptions import APIConnectionError, APIAuthenticationError, ExtractionError


class TestGitLabClientComplete:
    """Tests complets pour la classe GitLabClient harmonisée."""
    
    @pytest.fixture
    def gitlab_config(self):
        """Fixture pour créer une configuration GitLab de test."""
        return {
            "api_url": "https://gitlab.example.com/api/v4",
            "private_token": "fake_token",
            "verify_ssl": True
        }
    
    @pytest.fixture
    def gitlab_client(self, gitlab_config):
        """Fixture pour créer un client GitLab avec une configuration de test."""
        return GitLabClient(gitlab_config)
    
    @responses.activate
    def test_connect_successful(self, gitlab_client):
        """Teste une connexion réussie à l'API GitLab."""
        # Simuler une réponse réussie à l'API Version
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/version",
            json={"version": "15.5.0"},
            status=200
        )
        
        # Exécuter la méthode connect
        result = gitlab_client.connect()
        
        # Vérifier que la connexion est réussie
        assert result is True
        assert gitlab_client.is_connected is True
    
    @responses.activate
    def test_connect_authentication_error(self, gitlab_client):
        """Teste une erreur d'authentification lors de la connexion."""
        # Simuler une erreur d'authentification
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/version",
            json={"message": "401 Unauthorized"},
            status=401
        )
        
        # Vérifier que l'exception appropriée est levée
        with pytest.raises(APIAuthenticationError):
            gitlab_client.connect()
        
        # Vérifier que le client n'est pas connecté
        assert gitlab_client.is_connected is False
    
    @responses.activate
    def test_connect_connection_error(self, gitlab_client):
        """Teste une erreur de connexion à l'API GitLab."""
        # Simuler une erreur de connexion
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/version",
            body=Exception("Connection error"),
            status=503
        )
        
        # Vérifier que l'exception appropriée est levée
        with pytest.raises(APIConnectionError):
            gitlab_client.connect()
        
        # Vérifier que le client n'est pas connecté
        assert gitlab_client.is_connected is False
    
    @responses.activate
    def test_test_connection(self, gitlab_client):
        """Teste la méthode test_connection du client GitLab."""
        # Simuler une réponse réussie à l'API Version
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/version",
            json={"version": "15.5.0"},
            status=200
        )
        
        # Simuler une réponse réussie à l'API User
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/user",
            json={"id": 1, "username": "test_user"},
            status=200
        )
        
        # Exécuter la méthode test_connection
        result = gitlab_client.test_connection()
        
        # Vérifier le résultat
        assert result["success"] is True
        assert "version" in result
        assert "current_user" in result
        assert result["current_user"]["username"] == "test_user"
    
    @responses.activate
    def test_api_get_successful(self, gitlab_client):
        """Teste une requête GET réussie à l'API GitLab."""
        # Marquer le client comme connecté
        gitlab_client.is_connected = True
        
        # Simuler une réponse réussie
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/projects",
            json=[{"id": 1, "name": "project1"}, {"id": 2, "name": "project2"}],
            status=200
        )
        
        # Exécuter la méthode api_get
        result = gitlab_client.api_get("projects", {})
        
        # Vérifier le résultat
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "project1"
    
    @responses.activate
    def test_api_get_with_params(self, gitlab_client):
        """Teste une requête GET avec paramètres à l'API GitLab."""
        # Marquer le client comme connecté
        gitlab_client.is_connected = True
        
        # Simuler une réponse réussie
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/projects?visibility=public",
            json=[{"id": 1, "name": "public_project"}],
            status=200
        )
        
        # Exécuter la méthode api_get avec des paramètres
        result = gitlab_client.api_get("projects", {"visibility": "public"})
        
        # Vérifier le résultat
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "public_project"
    
    def test_api_get_not_connected(self, gitlab_client):
        """Teste le comportement de api_get lorsque le client n'est pas connecté."""
        # S'assurer que le client n'est pas connecté
        gitlab_client.is_connected = False
        
        # Vérifier que l'exception appropriée est levée
        with pytest.raises(ExtractionError, match="Client GitLab non connecté"):
            gitlab_client.api_get("projects", {})
    
    @responses.activate
    def test_api_post_successful(self, gitlab_client):
        """Teste une requête POST réussie à l'API GitLab."""
        # Marquer le client comme connecté
        gitlab_client.is_connected = True
        
        # Simuler une réponse réussie
        responses.add(
            responses.POST,
            "https://gitlab.example.com/api/v4/projects",
            json={"id": 3, "name": "new_project"},
            status=201
        )
        
        # Préparer les données à envoyer
        data = {"name": "new_project", "visibility": "private"}
        
        # Exécuter la méthode api_post
        result = gitlab_client.api_post("projects", data)
        
        # Vérifier le résultat
        assert isinstance(result, dict)
        assert result["name"] == "new_project"
    
    @responses.activate
    def test_pagination_handling(self, gitlab_client):
        """Teste la gestion de la pagination dans les requêtes API."""
        # Marquer le client comme connecté
        gitlab_client.is_connected = True
        
        # Simuler une réponse paginée (page 1)
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/users?per_page=2&page=1",
            json=[{"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}],
            status=200,
            headers={
                'X-Page': '1',
                'X-Per-Page': '2',
                'X-Total': '5',
                'X-Total-Pages': '3',
                'Link': '<https://gitlab.example.com/api/v4/users?per_page=2&page=2>; rel="next"'
            }
        )
        
        # Simuler une réponse paginée (page 2)
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/users?per_page=2&page=2",
            json=[{"id": 3, "username": "user3"}, {"id": 4, "username": "user4"}],
            status=200,
            headers={
                'X-Page': '2',
                'X-Per-Page': '2',
                'X-Total': '5',
                'X-Total-Pages': '3',
                'Link': '<https://gitlab.example.com/api/v4/users?per_page=2&page=3>; rel="next"'
            }
        )
        
        # Simuler une réponse paginée (page 3)
        responses.add(
            responses.GET,
            "https://gitlab.example.com/api/v4/users?per_page=2&page=3",
            json=[{"id": 5, "username": "user5"}],
            status=200,
            headers={
                'X-Page': '3',
                'X-Per-Page': '2',
                'X-Total': '5',
                'X-Total-Pages': '3'
            }
        )
        
        # Exécuter la méthode api_get avec pagination
        result = gitlab_client.api_get("users", {"per_page": 2, "page": 1})
        
        # Vérifier que toutes les pages ont été fusionnées
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0]["username"] == "user1"
        assert result[4]["username"] == "user5"
