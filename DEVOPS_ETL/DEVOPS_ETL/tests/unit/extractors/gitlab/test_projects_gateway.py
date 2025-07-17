"""
Tests unitaires pour GitLabProjectsGateway.

Ce module contient les tests pour la classe GitLabProjectsGateway qui
permet d'interagir avec les projets GitLab via le client harmonisé.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call

from src.extractors.gitlab.gitlab_client import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway


class TestGitLabProjectsGateway:
    """Tests pour la classe GitLabProjectsGateway."""

    @pytest.fixture
    def mock_gitlab_client(self):
        """Fixture pour créer un mock de GitLabClient."""
        mock_client = MagicMock(spec=GitLabClient)
        mock_client.is_connected = True
        return mock_client

    @pytest.fixture
    def projects_gateway(self, mock_gitlab_client):
        """Fixture pour créer un gateway projets avec un client mocké."""
        return GitLabProjectsGateway(mock_gitlab_client)

    def test_get_projects_without_params(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération des projets sans paramètres."""
        # Configuration du mock
        mock_projects = [{"id": 1, "name": "project1"}, {"id": 2, "name": "project2"}]
        mock_gitlab_client.api_get.return_value = mock_projects

        # Appel de la méthode à tester
        result = projects_gateway.get_projects()

        # Vérifications
        assert result == mock_projects
        mock_gitlab_client.api_get.assert_called_once_with("projects", {})

    def test_get_projects_with_params(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération des projets avec paramètres."""
        # Configuration du mock
        mock_projects = [{"id": 1, "name": "project1"}]
        mock_gitlab_client.api_get.return_value = mock_projects
        
        # Paramètres de recherche
        search_params = {"search": "project1", "visibility": "public"}

        # Appel de la méthode à tester
        result = projects_gateway.get_projects(search_params)

        # Vérifications
        assert result == mock_projects
        mock_gitlab_client.api_get.assert_called_once_with("projects", search_params)

    def test_get_project_by_id(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération d'un projet par son ID."""
        # Configuration du mock
        mock_project = {"id": 123, "name": "testproject"}
        mock_gitlab_client.api_get.return_value = mock_project

        # Appel de la méthode à tester
        result = projects_gateway.get_project_by_id(123)

        # Vérifications
        assert result == mock_project
        mock_gitlab_client.api_get.assert_called_once_with("projects/123", {})

    def test_get_project_by_path(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération d'un projet par son chemin."""
        # Configuration du mock pour retourner un seul projet
        mock_project = {"id": 456, "path_with_namespace": "group/testproject"}
        mock_projects = [mock_project]
        mock_gitlab_client.api_get.return_value = mock_projects

        # Appel de la méthode à tester
        result = projects_gateway.get_project_by_path("group/testproject")

        # Vérifications
        assert result == mock_project
        mock_gitlab_client.api_get.assert_called_once_with("projects", {"search": "testproject"})

    def test_get_project_by_path_not_found(self, projects_gateway, mock_gitlab_client):
        """Teste le comportement lorsqu'un projet n'est pas trouvé par chemin."""
        # Configuration du mock pour retourner une liste vide (projet non trouvé)
        mock_gitlab_client.api_get.return_value = []

        # Appel de la méthode à tester
        result = projects_gateway.get_project_by_path("nonexistent/project")

        # Vérifications
        assert result is None
        mock_gitlab_client.api_get.assert_called_once_with("projects", {"search": "project"})

    def test_get_project_commits(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération des commits d'un projet."""
        # Configuration du mock
        mock_commits = [
            {"id": "abc123", "message": "First commit"},
            {"id": "def456", "message": "Second commit"}
        ]
        mock_gitlab_client.api_get.return_value = mock_commits

        # Appel de la méthode à tester
        result = projects_gateway.get_project_commits(123)

        # Vérifications
        assert result == mock_commits
        mock_gitlab_client.api_get.assert_called_once_with("projects/123/repository/commits", {})

    def test_get_project_branches(self, projects_gateway, mock_gitlab_client):
        """Teste la récupération des branches d'un projet."""
        # Configuration du mock
        mock_branches = [
            {"name": "main", "merged": False},
            {"name": "feature", "merged": False}
        ]
        mock_gitlab_client.api_get.return_value = mock_branches

        # Appel de la méthode à tester
        result = projects_gateway.get_project_branches(123)

        # Vérifications
        assert result == mock_branches
        mock_gitlab_client.api_get.assert_called_once_with("projects/123/repository/branches", {})
