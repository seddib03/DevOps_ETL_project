"""
Module contenant le client GitLab pour interagir avec l'API GitLab.

Ce client utilise la bibliothèque officielle python-gitlab v6.1.0 pour offrir
une interface cohérente et fiable pour l'accès aux données GitLab.
Basé sur la documentation officielle: https://python-gitlab.readthedocs.io/en/stable/
"""
import logging
import ssl
import time
from typing import Any, Dict, List, Optional, Union

import gitlab
import urllib3
from gitlab.v4.objects import Project, Group, User
from urllib3.exceptions import InsecureRequestWarning

from src.core.exceptions import APIAuthenticationError, APIConnectionError, APIRateLimitError
from src.extractors.base_extractor import BaseExtractor


class GitLabClient(BaseExtractor):
    """
    Client pour interagir avec l'API GitLab via la bibliothèque officielle python-gitlab.
    
    Ce client fournit une interface standardisée pour extraire les données GitLab
    avec gestion des erreurs, retry automatique et configuration SSL flexible.
    """

    # Configuration par défaut
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 5
    DEFAULT_ITEMS_PER_PAGE = 100
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialise le client GitLab avec la configuration fournie.
        
        Args:
            config: Dictionnaire contenant la configuration GitLab.
                   Clés requises: 'api_url', 'private_token'
                   Clés optionnelles: 'verify_ssl', 'timeout', 'max_retries', 
                                     'retry_delay', 'items_per_page', 'proxy'
        
        Raises:
            ValueError: Si les paramètres obligatoires sont manquants.
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Extraction et validation des paramètres de configuration
        self._validate_config(config)
        self._extract_config_params(config)
        
        # Configuration SSL
        self._configure_ssl()
        
        # Initialisation du client python-gitlab (lazy loading)
        self.gl: Optional[gitlab.Gitlab] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.is_connected = False
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Valide la configuration GitLab."""
        required_params = ['api_url', 'private_token']
        missing_params = [param for param in required_params if not config.get(param)]
        
        if missing_params:
            raise ValueError(
                f"Paramètres obligatoires manquants dans la configuration GitLab: {', '.join(missing_params)}"
            )
    
    def _extract_config_params(self, config: Dict[str, Any]) -> None:
        """Extrait les paramètres de configuration."""
        self.api_url = config["api_url"]
        self.private_token = config["private_token"]
        self.timeout = config.get("timeout", self.DEFAULT_TIMEOUT)
        self.max_retries = config.get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.retry_delay = config.get("retry_delay", self.DEFAULT_RETRY_DELAY)
        self.items_per_page = config.get("items_per_page", self.DEFAULT_ITEMS_PER_PAGE)
        self.verify_ssl = config.get("verify_ssl", True)
        
        # Configuration du proxy
        self.proxies = self._extract_proxy_config(config.get("proxy", {}))
    
    def _extract_proxy_config(self, proxy_config: Dict[str, Any]) -> Dict[str, str]:
        """Extrait et valide la configuration du proxy."""
        proxies = {}
        if proxy_config:
            if proxy_config.get("http"):
                proxies["http"] = proxy_config["http"]
            if proxy_config.get("https"):
                proxies["https"] = proxy_config["https"]
            
            if proxies:
                self.logger.info(f"Configuration proxy détectée: {list(proxies.keys())}")
        
        return proxies
    
    def _configure_ssl(self) -> None:
        """Configure les paramètres SSL selon la configuration."""
        if not self.verify_ssl:
            urllib3.disable_warnings(InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
            self.logger.warning(
                "AVERTISSEMENT: La vérification SSL est désactivée. "
                "Cette configuration n'est pas recommandée en production."
            )
            self.logger.info("Configuration SSL adaptée pour les certificats d'entreprise internes.")
    
    def connect(self) -> bool:
        """
        Établit la connexion avec l'API GitLab.
        
        Returns:
            True si la connexion est réussie, False sinon.
            
        Raises:
            APIAuthenticationError: Si le token d'authentification est invalide.
            APIConnectionError: Si une erreur de connexion survient.
        """
        try:
            self.gl = self._create_gitlab_client()
            self._authenticate()
            self.is_connected = True
            self.logger.info(f"Connexion à GitLab établie avec succès. Utilisateur: {self.user_info['username']}")
            return True
            
        except gitlab.exceptions.GitlabAuthenticationError as e:
            self.is_connected = False
            self.logger.error(f"Échec d'authentification à GitLab: {e}")
            raise APIAuthenticationError(f"Échec d'authentification: {e}")
            
        except gitlab.exceptions.GitlabConnectionError as e:
            self.is_connected = False
            self.logger.error(f"Erreur de connexion à GitLab: {e}")
            raise APIConnectionError(f"Erreur de connexion à GitLab: {e}")
            
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"Erreur inattendue lors de la connexion à GitLab: {e}")
            raise APIConnectionError(f"Erreur inattendue lors de la connexion: {e}")
    
    def _create_gitlab_client(self) -> gitlab.Gitlab:
        """Crée et configure le client GitLab."""
        client = gitlab.Gitlab(
            url=self.api_url,
            private_token=self.private_token,
            ssl_verify=self.verify_ssl,
            timeout=self.timeout,
            retry_transient_errors=True,
            per_page=self.items_per_page
        )
        
        # Configuration du proxy si défini
        if self.proxies:
            client.session.proxies.update(self.proxies)
            self.logger.info(f"Proxy configuré pour GitLab: {list(self.proxies.keys())}")
        
        return client
    
    def _authenticate(self) -> None:
        """Effectue l'authentification et stocke les informations utilisateur."""
        self.gl.auth()
        user = self.gl.user
        self.user_info = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Teste la connexion à GitLab et retourne des informations détaillées.
        
        Returns:
            Dictionnaire contenant les informations sur la connexion, y compris:
            - success: Booléen indiquant si la connexion est réussie
            - version: Version de l'API GitLab
            - user_info: Informations sur l'utilisateur connecté
            - error: Message d'erreur (si applicable)
            
        Raises:
            APIConnectionError: Si une erreur de connexion survient.
        """
        result = {
            "success": False,
            "api_url": self.api_url
        }
        
        # Créer le client si nécessaire
        if self.gl is None:
            self.gl = self._create_gitlab_client()
        
        try:
            # Tester l'accès à la version (ne nécessite pas d'authentification)
            version_info = self._get_version_info()
            result.update(version_info)
            
            # Tester l'authentification
            self._authenticate()
            result["user_info"] = self.user_info
            result["success"] = True
            
            self.logger.info(
                f"Test de connexion GitLab réussi: Version={result.get('version', 'N/A')}, "
                f"User={result['user_info']['username']}"
            )
            
        except gitlab.exceptions.GitlabAuthenticationError as e:
            result["error"] = f"Erreur d'authentification: {str(e)}"
            self.logger.error(f"Test de connexion GitLab échoué (auth): {e}")
            
        except Exception as e:
            result["error"] = f"Erreur d'accès API: {str(e)}"
            self.logger.error(f"Impossible d'accéder à l'API GitLab: {e}")
        
        return result
    
    def _get_version_info(self) -> Dict[str, Any]:
        """Récupère les informations de version de GitLab."""
        try:
            version_info = self.gl.version()
            return {
                "version": version_info.get("version"),
                "api_version": version_info.get("api_version"),
                "revision": version_info.get("revision")
            }
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer les informations de version: {e}")
            return {}
        
        return result
    
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Méthode principale d'extraction de données depuis GitLab.
        Implémentation de la méthode abstraite de la classe BaseExtractor.
        
        Args:
            **kwargs: Paramètres spécifiques pour l'extraction.
                      - resource: Type de ressource à extraire (projects, users, etc.)
                      - resource_id: ID optionnel de la ressource
                      - params: Paramètres supplémentaires pour la requête
        
        Returns:
            Liste de dictionnaires représentant les données extraites.
            
        Raises:
            ValueError: Si les paramètres fournis sont invalides.
            APIConnectionError: Si une erreur de connexion survient.
        """
        resource = kwargs.get("resource")
        resource_id = kwargs.get("resource_id")
        params = kwargs.get("params", {})
        
        if not resource:
            raise ValueError("Le paramètre 'resource' est obligatoire pour l'extraction GitLab.")
        
        # Vérifier que le client est initialisé
        if self.gl is None:
            self.connect()
            
        try:
            # Utiliser les managers spécifiques de python-gitlab v6.1.0
            # https://python-gitlab.readthedocs.io/en/stable/api-objects.html
            
            # Mapper les noms de ressources aux méthodes correspondantes dans l'API GitLab v6.1.0
            resource_mapping = {
                "users": self.gl.users,
                "projects": self.gl.projects,
                "groups": self.gl.groups,
                "issues": self.gl.issues,
                "merge_requests": self.gl.mergerequests,
                # Ajouter d'autres mappings au besoin
            }
            
            # Obtenir le gestionnaire de ressources
            manager = resource_mapping.get(resource)
            
            if manager is not None:
                if resource_id:
                    # Récupération d'une ressource spécifique par ID
                    try:
                        item = manager.get(resource_id, **params)
                        # Convertir l'objet GitLab en dictionnaire
                        return [self._object_to_dict(item)]
                    except gitlab.exceptions.GitlabGetError as e:
                        self.logger.error(f"Erreur lors de la récupération de la ressource {resource}/{resource_id}: {e}")
                        return []
                else:
                    # Liste de ressources avec pagination automatique
                    # La pagination est gérée automatiquement par python-gitlab v6.1.0
                    try:
                        items = manager.list(**params)
                        return [self._object_to_dict(item) for item in items]
                    except gitlab.exceptions.GitlabListError as e:
                        self.logger.error(f"Erreur lors de la récupération des ressources {resource}: {e}")
                        return []
            else:
                # Pour les endpoints qui n'ont pas de manager spécifique
                # Utiliser les méthodes HTTP génériques
                endpoint = f"/{resource}"
                if resource_id:
                    endpoint += f"/{resource_id}"
                
                # Ajouter le paramètre per_page pour la pagination
                if "per_page" not in params:
                    params["per_page"] = self.items_per_page
                
                return self._get_paginated_results(endpoint, params)
                
        except gitlab.exceptions.GitlabAuthenticationError as e:
            self.logger.error(f"Erreur d'authentification lors de l'accès à {resource}: {e}")
            raise APIAuthenticationError(f"Erreur d'authentification GitLab: {e}")
        except gitlab.exceptions.GitlabRateLimitError as e:
            self.logger.error(f"Limite de taux dépassée pour {resource}: {e}")
            raise APIRateLimitError(f"Limite de taux GitLab dépassée: {e}")
        except gitlab.exceptions.GitlabConnectionError as e:
            self.logger.error(f"Erreur de connexion pour {resource}: {e}")
            raise APIConnectionError(f"Erreur de connexion GitLab: {e}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données GitLab pour {resource}: {e}")
            raise APIConnectionError(f"Erreur lors de l'extraction des données GitLab: {e}")
    
    def _object_to_dict(self, obj) -> Dict[str, Any]:
        """
        Convertit un objet GitLab en dictionnaire.
        
        Args:
            obj: L'objet GitLab à convertir
            
        Returns:
            Dictionnaire représentant l'objet GitLab
        """
        if hasattr(obj, 'attributes'):
            return obj.attributes
        elif hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        else:
            return obj
    
    def extract_incremental(self, from_date: str, to_date: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Extrait les données de manière incrémentielle depuis GitLab.
        
        Args:
            from_date: Date de début au format YYYY-MM-DD.
            to_date: Date de fin optionnelle au format YYYY-MM-DD.
            **kwargs: Paramètres spécifiques pour l'extraction.
                      - resource: Type de ressource à extraire
        
        Returns:
            Liste de dictionnaires représentant les données extraites.
        """
        resource = kwargs.get("resource")
        params = kwargs.get("params", {})
        
        # Ajouter les filtres de date
        params["created_after"] = from_date
        if to_date:
            params["created_before"] = to_date
        
        # Utiliser la méthode d'extraction standard avec les paramètres de date
        return self.extract(resource=resource, params=params)
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Effectue une requête vers l'API GitLab avec gestion des erreurs et retries.
        Cette implémentation utilise la bibliothèque python-gitlab plutôt que des requêtes HTTP directes.
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Point d'accès de l'API (sans l'URL de base)
            params: Paramètres de requête (query string)
            data: Données à envoyer dans le corps de la requête
            
        Returns:
            Réponse de l'API sous forme de dictionnaire ou liste de dictionnaires
            
        Raises:
            APIAuthenticationError: Si l'authentification échoue (401, 403)
            APIRateLimitError: Si la limite de taux est atteinte (429)
            APIConnectionError: Pour les autres erreurs de connexion
        """
        # Initialiser le client si nécessaire
        if self.gl is None:
            self.connect()
        
        # Standardiser l'endpoint (retirer le / initial si présent)
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
            
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # Utiliser les méthodes HTTP de python-gitlab
                if method.upper() == "GET":
                    response = self.gl.http_get(endpoint, query_data=params)
                elif method.upper() == "POST":
                    response = self.gl.http_post(endpoint, query_data=params, post_data=data)
                elif method.upper() == "PUT":
                    response = self.gl.http_put(endpoint, query_data=params, post_data=data)
                elif method.upper() == "DELETE":
                    response = self.gl.http_delete(endpoint, query_data=params)
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")
                    
                # La bibliothèque python-gitlab gère déjà les codes d'erreur et lance des exceptions
                # Nous retournons simplement la réponse
                return response
                    
            except gitlab.exceptions.GitlabAuthenticationError as e:
                # Erreur d'authentification
                raise APIAuthenticationError(f"Authentification échouée à GitLab: {e}")
                
            except gitlab.exceptions.GitlabRateLimitError as e:
                # Limite de taux atteinte
                retry_after = e.retry_after if hasattr(e, 'retry_after') else self.retry_delay
                self.logger.warning(f"Limite de taux GitLab atteinte. Attente de {retry_after} secondes.")
                if retries < self.max_retries:
                    time.sleep(retry_after)
                    retries += 1
                    continue
                raise APIRateLimitError(f"Limite de taux GitLab atteinte après {retries} tentatives.")
                
            except gitlab.exceptions.GitlabConnectionError as e:
                # Erreur de connexion
                if retries < self.max_retries:
                    retries += 1
                    self.logger.warning(f"Erreur de connexion à GitLab, tentative {retries}/{self.max_retries}: {str(e)}")
                    time.sleep(self.retry_delay)
                    continue
                last_error = e
                raise APIConnectionError(f"Erreur de connexion à GitLab après {retries} tentatives: {str(e)}")
                
            except gitlab.exceptions.GitlabError as e:
                # Autres erreurs GitLab
                if retries < self.max_retries:
                    retries += 1
                    self.logger.warning(f"Erreur GitLab, tentative {retries}/{self.max_retries}: {str(e)}")
                    time.sleep(self.retry_delay)
                    continue
                last_error = e
                raise APIConnectionError(f"Erreur GitLab après {retries} tentatives: {str(e)}")
                
            except Exception as e:
                # Erreurs inattendues
                last_error = e
                self.logger.error(f"Erreur inattendue lors de la requête GitLab: {e}")
                raise APIConnectionError(f"Erreur inattendue lors de la requête GitLab: {str(e)}")
    
    def _get_paginated_results(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Récupère tous les résultats paginés d'un endpoint GitLab.
        Utilise la pagination automatique de python-gitlab v6.1.0.
        
        Args:
            endpoint: Point d'accès de l'API
            params: Paramètres de requête
            
        Returns:
            Liste complète des résultats de toutes les pages
        """
        # Initialiser le client si nécessaire
        if self.gl is None:
            self.connect()
            
        # Standardiser l'endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
            
        params = params or {}
        results = []
        
        # S'assurer que per_page est défini pour optimiser la pagination
        if "per_page" not in params:
            params["per_page"] = self.items_per_page
        
        try:
            # Utiliser la méthode http_list de python-gitlab v6.1.0 avec pagination automatique
            # https://python-gitlab.readthedocs.io/en/stable/api-usage.html#gitlab.Gitlab.http_list
            self.logger.debug(f"Récupération des données depuis {endpoint} avec params={params}")
            
            # get_next_page=True active la récupération automatique de toutes les pages
            all_items = self.gl.http_list(endpoint, query_data=params, get_next_page=True, 
                                        as_list=False, page=1, retry_transient_errors=True)
            
            # Convertir les résultats en dictionnaires
            for item in all_items:
                if hasattr(item, 'attributes'):
                    results.append(item.attributes)
                else:
                    results.append(item)
            
            self.logger.info(f"Récupération de {len(results)} résultats depuis {endpoint}")
            return results
            
        except gitlab.exceptions.GitlabListError as e:
            self.logger.error(f"Erreur lors de la récupération des résultats paginés depuis {endpoint}: {e}")
            raise APIConnectionError(f"Erreur lors de la récupération des résultats paginés: {e}")
        except gitlab.exceptions.GitlabHttpError as e:
            self.logger.error(f"Erreur HTTP lors de la récupération depuis {endpoint}: {e}")
            raise APIConnectionError(f"Erreur HTTP lors de l'accès à GitLab: {e}")
        except gitlab.exceptions.GitlabAuthenticationError as e:
            self.logger.error(f"Erreur d'authentification lors de l'accès à {endpoint}: {e}")
            raise APIAuthenticationError(f"Erreur d'authentification GitLab: {e}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la récupération des résultats depuis {endpoint}: {e}")
            raise APIConnectionError(f"Erreur inattendue lors de la récupération des résultats: {e}")
            
    def extract_users(self, active_only: bool = False, include_bots: bool = True, 
                      per_page: int = None) -> List[Dict[str, Any]]:
        """
        Extrait tous les utilisateurs GitLab avec options de filtrage.
        
        Args:
            active_only: Si True, ne récupère que les utilisateurs actifs
            include_bots: Si True, inclut les comptes bots
            per_page: Nombre d'éléments par page (utilise la valeur par défaut si None)
            
        Returns:
            Liste des utilisateurs GitLab sous forme de dictionnaires
            
        Raises:
            APIConnectionError: Si une erreur de connexion survient
        """
        if self.gl is None:
            self.connect()
        
        params = {}
        
        # Filtrer par statut actif si demandé
        if active_only:
            params["active"] = True
        
        # Configurer la pagination
        if per_page:
            params["per_page"] = per_page
        else:
            params["per_page"] = self.items_per_page
        
        try:
            # Utiliser le manager users pour récupérer tous les utilisateurs
            users = self.gl.users.list(all=True, **params)
            
            # Convertir en dictionnaires et filtrer les bots si nécessaire
            result = []
            for user in users:
                user_dict = self._object_to_dict(user)
                
                # Filtrer les bots si demandé
                if not include_bots and user_dict.get('bot', False):
                    continue
                
                result.append(user_dict)
            
            self.logger.info(f"Récupération de {len(result)} utilisateurs GitLab")
            return result
            
        except gitlab.exceptions.GitlabListError as e:
            self.logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            raise APIConnectionError(f"Erreur lors de la récupération des utilisateurs: {e}")
    
    def extract_projects(self, owned: bool = False, starred: bool = False, 
                        visibility: str = None, per_page: int = None) -> List[Dict[str, Any]]:
        """
        Extrait tous les projets GitLab avec options de filtrage.
        
        Args:
            owned: Si True, ne récupère que les projets possédés par l'utilisateur
            starred: Si True, ne récupère que les projets favoris
            visibility: Niveau de visibilité ('public', 'internal', 'private')
            per_page: Nombre d'éléments par page
            
        Returns:
            Liste des projets GitLab sous forme de dictionnaires
        """
        if self.gl is None:
            self.connect()
        
        params = {}
        
        if owned:
            params["owned"] = True
        if starred:
            params["starred"] = True
        if visibility:
            params["visibility"] = visibility
        if per_page:
            params["per_page"] = per_page
        else:
            params["per_page"] = self.items_per_page
        
        try:
            projects = self.gl.projects.list(all=True, **params)
            result = [self._object_to_dict(project) for project in projects]
            
            self.logger.info(f"Récupération de {len(result)} projets GitLab")
            return result
            
        except gitlab.exceptions.GitlabListError as e:
            self.logger.error(f"Erreur lors de la récupération des projets: {e}")
            raise APIConnectionError(f"Erreur lors de la récupération des projets: {e}")
    
    def close(self) -> None:
        """
        Ferme la session et libère les ressources.
        """
        # Rien à faire pour python-gitlab car il gère lui-même les sessions
        self.is_connected = False
        self.gl = None
        super().close()
