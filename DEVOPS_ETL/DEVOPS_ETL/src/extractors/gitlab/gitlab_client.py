"""
Client GitLab consolidé avec conventions de nomenclature améliorées.

Ce module fournit un client GitLab unifié qui combine les meilleures pratiques
de la version améliorée avec la compatibilité BaseExtractor.
"""
import logging
import ssl
import time
from typing import Any, Dict, List, Optional, Union

import gitlab
import urllib3
from gitlab.v4.objects import Project, Group, User
from urllib3.exceptions import InsecureRequestWarning

from src.core.constants import (
    DEFAULT_GITLAB_TIMEOUT,
    DEFAULT_GITLAB_MAX_RETRIES,
    DEFAULT_GITLAB_RETRY_DELAY,
    DEFAULT_GITLAB_ITEMS_PER_PAGE,
    SUPPORTED_GITLAB_RESOURCES,
    SSL_CONFIG,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)
from src.core.exceptions import APIAuthenticationError, APIConnectionError, APIRateLimitError
from src.extractors.base_extractor import BaseExtractor


class GitLabClient(BaseExtractor):
    """
    Client GitLab consolidé avec conventions de nomenclature améliorées.
    
    Ce client fournit une interface standardisée pour extraire les données GitLab
    avec une nomenclature cohérente et des bonnes pratiques de développement.
    Hérite de BaseExtractor pour la compatibilité avec l'architecture existante.
    """

    def __init__(self, gitlab_config: Dict[str, Any]) -> None:
        """
        Initialise le client GitLab avec une configuration validée.
        
        Args:
            gitlab_config: Configuration GitLab avec clés requises et optionnelles
        
        Raises:
            ValueError: Si la configuration est invalide
        """
        # Initialiser BaseExtractor en premier avec la config
        super().__init__(gitlab_config)
        
        self._logger = logging.getLogger(__name__)
        
        # Configuration avec validation
        self._validate_configuration(gitlab_config)
        self._extract_configuration_parameters(gitlab_config)
        
        # Configuration SSL
        self._configure_ssl_settings()
        
        # État de la connexion
        self._gitlab_client: Optional[gitlab.Gitlab] = None
        self._current_user_info: Optional[Dict[str, Any]] = None
        self._connection_status = False
    
    # Propriétés pour la compatibilité avec l'ancien client
    @property
    def api_url(self) -> str:
        """Propriété pour l'URL de l'API."""
        return self._api_url
    
    @property
    def private_token(self) -> str:
        """Propriété pour le token privé."""
        return self._private_token
    
    @property
    def gl(self) -> Optional[gitlab.Gitlab]:
        """Propriété pour le client GitLab."""
        return self._gitlab_client
    
    @property
    def logger(self) -> logging.Logger:
        """Propriété pour le logger."""
        return self._logger
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Valide la configuration GitLab fournie.
        
        Args:
            config: Configuration à valider
            
        Raises:
            ValueError: Si des paramètres obligatoires sont manquants
        """
        required_parameters = ['api_url', 'private_token']
        missing_parameters = [
            param for param in required_parameters 
            if not config.get(param)
        ]
        
        if missing_parameters:
            raise ValueError(
                ERROR_MESSAGES["MISSING_CONFIG"].format(
                    parameter=", ".join(missing_parameters)
                )
            )
    
    def _extract_configuration_parameters(self, config: Dict[str, Any]) -> None:
        """
        Extrait et assigne les paramètres de configuration.
        
        Args:
            config: Configuration GitLab
        """
        self._api_url = config["api_url"]
        self._private_token = config["private_token"]
        self._request_timeout = config.get("timeout", DEFAULT_GITLAB_TIMEOUT)
        self._max_retry_attempts = config.get("max_retries", DEFAULT_GITLAB_MAX_RETRIES)
        self._retry_delay_seconds = config.get("retry_delay", DEFAULT_GITLAB_RETRY_DELAY)
        self._items_per_page = config.get("items_per_page", DEFAULT_GITLAB_ITEMS_PER_PAGE)
        self._ssl_verification_enabled = config.get("verify_ssl", SSL_CONFIG["VERIFY_SSL_DEFAULT"])
        
        # Configuration proxy
        self._proxy_configuration = config.get("proxy", {})
        
        # Configuration des retry
        self._retry_on_errors = config.get("retry_on_errors", True)
        self._retry_on_rate_limit = config.get("retry_on_rate_limit", True)
    
    def _configure_ssl_settings(self) -> None:
        """
        Configure les paramètres SSL selon la configuration.
        """
        if not self._ssl_verification_enabled:
            self._logger.warning(
                "SSL verification disabled. This is not recommended for production."
            )
            urllib3.disable_warnings(InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
    
    def connect(self) -> bool:
        """
        Méthode abstraite requise par BaseExtractor.
        
        Returns:
            bool: True si la connexion est réussie, False sinon
        """
        return self.establish_connection()
    
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Méthode abstraite requise par BaseExtractor.
        
        Args:
            **kwargs: Paramètres d'extraction (resource_type, filters, etc.)
            
        Returns:
            List[Dict[str, Any]]: Données extraites
        """
        resource_type = kwargs.get('resource_type', 'users')
        filters = kwargs.get('filters', {})
        
        if resource_type == 'users':
            return self.extract_gitlab_users(filters)
        elif resource_type == 'projects':
            return self.extract_gitlab_projects(filters)
        elif resource_type == 'groups':
            return self.extract_gitlab_groups(filters)
        else:
            raise ValueError(f"Resource type '{resource_type}' not supported")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Méthode abstraite requise par BaseExtractor.
        
        Returns:
            Dict[str, Any]: Informations sur le statut de la connexion
        """
        try:
            connection_successful = self.validate_connection()
            
            if connection_successful:
                return {
                    'success': True,
                    'status': 'success',
                    'connected': True,
                    'api_url': self._api_url,
                    'user_info': self._current_user_info,
                    'ssl_verification': self._ssl_verification_enabled,
                    'timeout': self._request_timeout,
                    'items_per_page': self._items_per_page,
                    'message': 'Connection successful'
                }
            else:
                return {
                    'success': False,
                    'status': 'failed',
                    'connected': False,
                    'api_url': self._api_url,
                    'error': 'Connection failed',
                    'message': 'Connection failed'
                }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'connected': False,
                'api_url': self._api_url,
                'error': str(e),
                'message': f'Connection test failed: {e}'
            }
    
    def establish_connection(self) -> bool:
        """
        Établit la connexion au serveur GitLab.
        
        Returns:
            bool: True si la connexion est réussie, False sinon
        """
        try:
            self._logger.info("Establishing connection to GitLab API")
            self._logger.debug(f"API URL: {self._api_url}")
            self._logger.debug(f"Token length: {len(self._private_token) if self._private_token else 0}")
            
            # Créer le client GitLab
            self._gitlab_client = gitlab.Gitlab(
                url=self._api_url,
                private_token=self._private_token,
                timeout=self._request_timeout,
                ssl_verify=self._ssl_verification_enabled,
                retry_transient_errors=self._retry_on_errors
            )
            
            self._logger.debug(f"GitLab client created: {self._gitlab_client}")
            self._logger.debug(f"GitLab client user manager: {self._gitlab_client.user}")
            
            # Configurer le proxy si nécessaire
            if self._proxy_configuration:
                self._configure_proxy_settings()
            
            # Tester la connexion
            self._logger.info("Testing GitLab connection...")
            self._gitlab_client.auth()
            self._logger.debug("Authentication successful")
            
            # Dans python-gitlab 6.1.0, user est directement accessible après auth()
            current_user = self._gitlab_client.user
            if current_user is None:
                raise APIConnectionError("Failed to get current user - authentication may have failed")
            
            self._current_user_info = current_user.asdict()
            self._connection_status = True
            self.is_connected = True  # Mettre à jour l'état BaseExtractor
            
            self._logger.info(
                f"GitLab connection successful - User: {self._current_user_info.get('name', 'Unknown')}, Server: {self._api_url}"
            )
            
            return True
            
        except gitlab.GitlabAuthenticationError as e:
            self._logger.error(f"Authentication failed: {e}")
            raise APIAuthenticationError(f"GitLab authentication failed: {e}")
        except gitlab.GitlabGetError as e:
            self._logger.error(f"API error: {e}")
            raise APIConnectionError(f"GitLab API error: {e}")
        except Exception as e:
            self._logger.error(f"Unexpected connection error: {e}")
            raise APIConnectionError(f"Unexpected GitLab connection error: {e}")
    
    def _configure_proxy_settings(self) -> None:
        """
        Configure les paramètres proxy pour le client GitLab.
        """
        if self._proxy_configuration:
            self._gitlab_client.session.proxies.update(self._proxy_configuration)
            self._logger.info("Proxy configuration applied")
    
    def validate_connection(self) -> bool:
        """
        Valide la connexion existante ou établit une nouvelle connexion.
        
        Returns:
            bool: True si la connexion est valide, False sinon
        """
        if not self._connection_status or not self._gitlab_client:
            return self.establish_connection()
        
        try:
            # Tester la connexion avec un appel simple
            self._gitlab_client.user.get()
            return True
        except Exception as e:
            self._logger.warning(f"Connection validation failed: {e}")
            return self.establish_connection()
    
    def extract_gitlab_users(self, user_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extrait les utilisateurs GitLab avec filtrage optionnel.
        
        Args:
            user_filter: Filtres optionnels pour les utilisateurs
        
        Returns:
            List[Dict[str, Any]]: Liste des utilisateurs GitLab
        """
        if not self.validate_connection():
            raise APIConnectionError("Unable to establish GitLab connection")
        
        try:
            self._logger.info("Starting GitLab users extraction")
            
            # Paramètres de requête
            query_parameters = {
                'per_page': self._items_per_page,
                'all': True
            }
            
            # Appliquer les filtres si fournis
            if user_filter:
                query_parameters.update(user_filter)
            
            # Récupérer les utilisateurs avec retry
            users_data = self._fetch_users_with_retry(query_parameters)
            
            # Normaliser les données
            normalized_users = self._normalize_user_data(users_data)
            
            self._logger.info(f"Successfully extracted {len(normalized_users)} users")
            return normalized_users
            
        except Exception as e:
            self._logger.error(f"Error extracting GitLab users: {e}")
            raise APIConnectionError(f"Failed to extract GitLab users: {e}")
    
    def extract_users(self, user_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Méthode de compatibilité pour extract_users.
        
        Args:
            user_filter: Filtres optionnels pour les utilisateurs
        
        Returns:
            List[Dict[str, Any]]: Liste des utilisateurs GitLab
        """
        return self.extract_gitlab_users(user_filter)
    
    def _fetch_users_with_retry(self, query_parameters: Dict[str, Any]) -> List[User]:
        """
        Récupère les utilisateurs avec mécanisme de retry.
        
        Args:
            query_parameters: Paramètres de requête
        
        Returns:
            List[User]: Liste des utilisateurs GitLab
        """
        for attempt in range(self._max_retry_attempts):
            try:
                return self._gitlab_client.users.list(**query_parameters)
            except gitlab.GitlabGetError as e:
                if e.response_code == 429 and self._retry_on_rate_limit:
                    self._handle_rate_limit_error(attempt)
                else:
                    raise
            except Exception as e:
                if attempt == self._max_retry_attempts - 1:
                    raise
                self._logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(self._retry_delay_seconds)
        
        raise APIConnectionError("Max retry attempts exceeded")
    
    def _handle_rate_limit_error(self, attempt: int) -> None:
        """
        Gère les erreurs de limitation de taux.
        
        Args:
            attempt: Numéro de tentative actuelle
        """
        if attempt == self._max_retry_attempts - 1:
            raise APIRateLimitError("GitLab API rate limit exceeded")
        
        delay = self._retry_delay_seconds * (2 ** attempt)  # Exponential backoff
        self._logger.warning(f"Rate limit hit, waiting {delay} seconds")
        time.sleep(delay)
    
    def _normalize_user_data(self, users_data: List[User]) -> List[Dict[str, Any]]:
        """
        Normalise les données utilisateur pour un format standardisé.
        
        Args:
            users_data: Données utilisateur brutes
        
        Returns:
            List[Dict[str, Any]]: Données utilisateur normalisées
        """
        normalized_users = []
        
        for user in users_data:
            try:
                user_dict = user.asdict()
                normalized_user = {
                    'user_id': user_dict.get('id'),
                    'username': user_dict.get('username'),
                    'name': user_dict.get('name'),
                    'email': user_dict.get('email'),
                    'state': user_dict.get('state'),
                    'avatar_url': user_dict.get('avatar_url'),
                    'web_url': user_dict.get('web_url'),
                    'created_at': user_dict.get('created_at'),
                    'bio': user_dict.get('bio'),
                    'location': user_dict.get('location'),
                    'public_email': user_dict.get('public_email'),
                    'skype': user_dict.get('skype'),
                    'linkedin': user_dict.get('linkedin'),
                    'twitter': user_dict.get('twitter'),
                    'website_url': user_dict.get('website_url'),
                    'organization': user_dict.get('organization'),
                    'job_title': user_dict.get('job_title'),
                    'last_sign_in_at': user_dict.get('last_sign_in_at'),
                    'confirmed_at': user_dict.get('confirmed_at'),
                    'theme_id': user_dict.get('theme_id'),
                    'color_scheme_id': user_dict.get('color_scheme_id'),
                    'projects_limit': user_dict.get('projects_limit'),
                    'current_sign_in_at': user_dict.get('current_sign_in_at'),
                    'identities': user_dict.get('identities', []),
                    'can_create_group': user_dict.get('can_create_group'),
                    'can_create_project': user_dict.get('can_create_project'),
                    'two_factor_enabled': user_dict.get('two_factor_enabled'),
                    'external': user_dict.get('external'),
                    'private_profile': user_dict.get('private_profile'),
                    'commit_email': user_dict.get('commit_email'),
                    'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                normalized_users.append(normalized_user)
            except Exception as e:
                self._logger.warning(f"Error normalizing user data: {e}")
                continue
        
        return normalized_users
    
    def extract_gitlab_projects(self, project_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extrait les projets GitLab avec filtrage optionnel.
        
        Args:
            project_filter: Filtres optionnels pour les projets
        
        Returns:
            List[Dict[str, Any]]: Liste des projets GitLab
        """
        if not self.validate_connection():
            raise APIConnectionError("Unable to establish GitLab connection")
        
        try:
            self._logger.info("Starting GitLab projects extraction")
            
            # Paramètres de requête
            query_parameters = {
                'per_page': self._items_per_page,
                'all': True
            }
            
            # Appliquer les filtres si fournis
            if project_filter:
                query_parameters.update(project_filter)
            
            # Récupérer les projets avec retry
            projects_data = self._fetch_projects_with_retry(query_parameters)
            
            # Normaliser les données
            normalized_projects = self._normalize_project_data(projects_data)
            
            self._logger.info(f"Successfully extracted {len(normalized_projects)} projects")
            return normalized_projects
            
        except Exception as e:
            self._logger.error(f"Error extracting GitLab projects: {e}")
            raise APIConnectionError(f"Failed to extract GitLab projects: {e}")
    
    def extract_projects(self, project_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Méthode de compatibilité pour extract_projects.
        
        Args:
            project_filter: Filtres optionnels pour les projets
        
        Returns:
            List[Dict[str, Any]]: Liste des projets GitLab
        """
        return self.extract_gitlab_projects(project_filter)
    
    def _fetch_projects_with_retry(self, query_parameters: Dict[str, Any]) -> List[Project]:
        """
        Récupère les projets avec mécanisme de retry.
        
        Args:
            query_parameters: Paramètres de requête
        
        Returns:
            List[Project]: Liste des projets GitLab
        """
        for attempt in range(self._max_retry_attempts):
            try:
                return self._gitlab_client.projects.list(**query_parameters)
            except gitlab.GitlabGetError as e:
                if e.response_code == 429 and self._retry_on_rate_limit:
                    self._handle_rate_limit_error(attempt)
                else:
                    raise
            except Exception as e:
                if attempt == self._max_retry_attempts - 1:
                    raise
                self._logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(self._retry_delay_seconds)
        
        raise APIConnectionError("Max retry attempts exceeded")
    
    def _normalize_project_data(self, projects_data: List[Project]) -> List[Dict[str, Any]]:
        """
        Normalise les données projet pour un format standardisé.
        
        Args:
            projects_data: Données projet brutes
        
        Returns:
            List[Dict[str, Any]]: Données projet normalisées
        """
        normalized_projects = []
        
        for project in projects_data:
            try:
                project_dict = project.asdict()
                normalized_project = {
                    'project_id': project_dict.get('id'),
                    'name': project_dict.get('name'),
                    'description': project_dict.get('description'),
                    'web_url': project_dict.get('web_url'),
                    'avatar_url': project_dict.get('avatar_url'),
                    'git_ssh_url': project_dict.get('ssh_url_to_repo'),
                    'git_http_url': project_dict.get('http_url_to_repo'),
                    'namespace': project_dict.get('namespace', {}),
                    'owner': project_dict.get('owner'),
                    'created_at': project_dict.get('created_at'),
                    'last_activity_at': project_dict.get('last_activity_at'),
                    'creator_id': project_dict.get('creator_id'),
                    'visibility': project_dict.get('visibility'),
                    'issues_enabled': project_dict.get('issues_enabled'),
                    'merge_requests_enabled': project_dict.get('merge_requests_enabled'),
                    'wiki_enabled': project_dict.get('wiki_enabled'),
                    'jobs_enabled': project_dict.get('jobs_enabled'),
                    'snippets_enabled': project_dict.get('snippets_enabled'),
                    'resolve_outdated_diff_discussions': project_dict.get('resolve_outdated_diff_discussions'),
                    'container_registry_enabled': project_dict.get('container_registry_enabled'),
                    'shared_runners_enabled': project_dict.get('shared_runners_enabled'),
                    'public_jobs': project_dict.get('public_jobs'),
                    'only_allow_merge_if_pipeline_succeeds': project_dict.get('only_allow_merge_if_pipeline_succeeds'),
                    'only_allow_merge_if_all_discussions_are_resolved': project_dict.get('only_allow_merge_if_all_discussions_are_resolved'),
                    'printing_merge_request_link_enabled': project_dict.get('printing_merge_request_link_enabled'),
                    'request_access_enabled': project_dict.get('request_access_enabled'),
                    'merge_method': project_dict.get('merge_method'),
                    'auto_devops_enabled': project_dict.get('auto_devops_enabled'),
                    'auto_devops_deploy_strategy': project_dict.get('auto_devops_deploy_strategy'),
                    'repository_storage': project_dict.get('repository_storage'),
                    'approvals_before_merge': project_dict.get('approvals_before_merge'),
                    'mirror': project_dict.get('mirror'),
                    'mirror_user_id': project_dict.get('mirror_user_id'),
                    'mirror_trigger_builds': project_dict.get('mirror_trigger_builds'),
                    'only_mirror_protected_branches': project_dict.get('only_mirror_protected_branches'),
                    'mirror_overwrites_diverged_branches': project_dict.get('mirror_overwrites_diverged_branches'),
                    'external_authorization_classification_label': project_dict.get('external_authorization_classification_label'),
                    'packages_enabled': project_dict.get('packages_enabled'),
                    'service_desk_enabled': project_dict.get('service_desk_enabled'),
                    'service_desk_address': project_dict.get('service_desk_address'),
                    'autoclose_referenced_issues': project_dict.get('autoclose_referenced_issues'),
                    'suggestion_commit_message': project_dict.get('suggestion_commit_message'),
                    'marked_for_deletion_at': project_dict.get('marked_for_deletion_at'),
                    'marked_for_deletion_on': project_dict.get('marked_for_deletion_on'),
                    'statistics': project_dict.get('statistics'),
                    'container_registry_image_prefix': project_dict.get('container_registry_image_prefix'),
                    '_links': project_dict.get('_links'),
                    'path_with_namespace': project_dict.get('path_with_namespace'),
                    'default_branch': project_dict.get('default_branch'),
                    'tag_list': project_dict.get('tag_list', []),
                    'topics': project_dict.get('topics', []),
                    'ssh_url_to_repo': project_dict.get('ssh_url_to_repo'),
                    'http_url_to_repo': project_dict.get('http_url_to_repo'),
                    'readme_url': project_dict.get('readme_url'),
                    'forks_count': project_dict.get('forks_count'),
                    'star_count': project_dict.get('star_count'),
                    'runners_token': project_dict.get('runners_token'),
                    'ci_default_git_depth': project_dict.get('ci_default_git_depth'),
                    'ci_forward_deployment_enabled': project_dict.get('ci_forward_deployment_enabled'),
                    'public_builds': project_dict.get('public_builds'),
                    'build_git_strategy': project_dict.get('build_git_strategy'),
                    'build_timeout': project_dict.get('build_timeout'),
                    'auto_cancel_pending_pipelines': project_dict.get('auto_cancel_pending_pipelines'),
                    'build_coverage_regex': project_dict.get('build_coverage_regex'),
                    'ci_config_path': project_dict.get('ci_config_path'),
                    'shared_with_groups': project_dict.get('shared_with_groups', []),
                    'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                normalized_projects.append(normalized_project)
            except Exception as e:
                self._logger.warning(f"Error normalizing project data: {e}")
                continue
        
        return normalized_projects
    
    def extract_gitlab_groups(self, group_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extrait les groupes GitLab avec filtrage optionnel.
        
        Args:
            group_filter: Filtres optionnels pour les groupes
        
        Returns:
            List[Dict[str, Any]]: Liste des groupes GitLab
        """
        if not self.validate_connection():
            raise APIConnectionError("Unable to establish GitLab connection")
        
        try:
            self._logger.info("Starting GitLab groups extraction")
            
            # Paramètres de requête
            query_parameters = {
                'per_page': self._items_per_page,
                'all': True
            }
            
            # Appliquer les filtres si fournis
            if group_filter:
                query_parameters.update(group_filter)
            
            # Récupérer les groupes avec retry
            groups_data = self._fetch_groups_with_retry(query_parameters)
            
            # Normaliser les données
            normalized_groups = self._normalize_group_data(groups_data)
            
            self._logger.info(f"Successfully extracted {len(normalized_groups)} groups")
            return normalized_groups
            
        except Exception as e:
            self._logger.error(f"Error extracting GitLab groups: {e}")
            raise APIConnectionError(f"Failed to extract GitLab groups: {e}")
    
    def extract_groups(self, group_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Méthode de compatibilité pour extract_groups.
        
        Args:
            group_filter: Filtres optionnels pour les groupes
        
        Returns:
            List[Dict[str, Any]]: Liste des groupes GitLab
        """
        return self.extract_gitlab_groups(group_filter)
    
    def _fetch_groups_with_retry(self, query_parameters: Dict[str, Any]) -> List[Group]:
        """
        Récupère les groupes avec mécanisme de retry.
        
        Args:
            query_parameters: Paramètres de requête
        
        Returns:
            List[Group]: Liste des groupes GitLab
        """
        for attempt in range(self._max_retry_attempts):
            try:
                return self._gitlab_client.groups.list(**query_parameters)
            except gitlab.GitlabGetError as e:
                if e.response_code == 429 and self._retry_on_rate_limit:
                    self._handle_rate_limit_error(attempt)
                else:
                    raise
            except Exception as e:
                if attempt == self._max_retry_attempts - 1:
                    raise
                self._logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(self._retry_delay_seconds)
        
        raise APIConnectionError("Max retry attempts exceeded")
    
    def _normalize_group_data(self, groups_data: List[Group]) -> List[Dict[str, Any]]:
        """
        Normalise les données groupe pour un format standardisé.
        
        Args:
            groups_data: Données groupe brutes
        
        Returns:
            List[Dict[str, Any]]: Données groupe normalisées
        """
        normalized_groups = []
        
        for group in groups_data:
            try:
                group_dict = group.asdict()
                normalized_group = {
                    'group_id': group_dict.get('id'),
                    'name': group_dict.get('name'),
                    'path': group_dict.get('path'),
                    'description': group_dict.get('description'),
                    'visibility': group_dict.get('visibility'),
                    'lfs_enabled': group_dict.get('lfs_enabled'),
                    'avatar_url': group_dict.get('avatar_url'),
                    'web_url': group_dict.get('web_url'),
                    'request_access_enabled': group_dict.get('request_access_enabled'),
                    'full_name': group_dict.get('full_name'),
                    'full_path': group_dict.get('full_path'),
                    'parent_id': group_dict.get('parent_id'),
                    'projects': group_dict.get('projects', []),
                    'statistics': group_dict.get('statistics'),
                    'created_at': group_dict.get('created_at'),
                    'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                normalized_groups.append(normalized_group)
            except Exception as e:
                self._logger.warning(f"Error normalizing group data: {e}")
                continue
        
        return normalized_groups
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de connexion actuelles.
        
        Returns:
            Dict[str, Any]: Informations de connexion
        """
        return {
            'connected': self._connection_status,
            'api_url': self._api_url,
            'current_user': self._current_user_info,
            'ssl_verification': self._ssl_verification_enabled,
            'timeout': self._request_timeout,
            'items_per_page': self._items_per_page
        }
    
    def close_connection(self) -> None:
        """
        Ferme la connexion GitLab et nettoie les ressources.
        """
        if self._gitlab_client:
            self._gitlab_client = None
        self._connection_status = False
        self._current_user_info = None
        self.is_connected = False  # Mettre à jour l'état BaseExtractor
        self._logger.info("GitLab connection closed")
    
    def close(self) -> None:
        """
        Méthode de compatibilité BaseExtractor pour fermer la connexion.
        """
        self.close_connection()
    
    def __enter__(self):
        """
        Support pour context manager.
        
        Returns:
            GitLabClient: Instance du client
        """
        self.establish_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Support pour context manager - nettoyage automatique.
        
        Args:
            exc_type: Type d'exception
            exc_val: Valeur d'exception
            exc_tb: Traceback d'exception
        """
        self.close_connection()
