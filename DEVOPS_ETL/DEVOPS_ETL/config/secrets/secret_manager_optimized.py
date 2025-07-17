"""
Gestionnaire de secrets optimisé pour l'application ETL DevOps.

Ce module fournit une interface unifiée pour accéder aux secrets 
avec les meilleures pratiques de sécurité et performance.

Version optimisée avec :
- Gestion d'erreurs améliorée
- Validation des données
- Cache intelligent
- Sécurité renforcée
"""
import os
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from dotenv import load_dotenv

# Configuration du logger
logger = logging.getLogger(__name__)

class SecretSource(Enum):
    """Sources possibles pour les secrets."""
    YAML_FILE = "yaml_file"
    ENVIRONMENT = "environment"
    DOTENV = "dotenv"
    DEFAULT = "default"

class SecretManager:
    """
    Gestionnaire centralisé et optimisé pour les secrets de l'application.
    
    Fonctionnalités :
    - Chargement depuis multiples sources avec priorité
    - Validation des données
    - Cache intelligent
    - Gestion d'erreurs robuste
    """
    
    def __init__(self, env: str = "dev"):
        """
        Initialise le gestionnaire de secrets.
        
        Args:
            env: Environnement cible ('dev', 'test', 'prod', etc.)
        """
        self.env = self._validate_environment(env)
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.base_path = Path(__file__).parent.parent
        self._secret_sources: Dict[str, SecretSource] = {}
        
        # Chargement des secrets avec gestion d'erreurs
        try:
            self._load_secrets()
        except Exception as e:
            logger.error(f"Erreur critique lors du chargement des secrets: {e}")
            raise
    
    def _validate_environment(self, env: str) -> str:
        """
        Valide l'environnement fourni.
        
        Args:
            env: Nom de l'environnement
            
        Returns:
            Environnement validé
            
        Raises:
            ValueError: Si l'environnement est invalide
        """
        if not env or not isinstance(env, str):
            raise ValueError("L'environnement doit être une chaîne non vide")
        
        # Environnements autorisés
        valid_envs = ["dev", "test", "staging", "prod", "local"]
        if env not in valid_envs:
            logger.warning(f"Environnement '{env}' non standard. Environnements recommandés: {valid_envs}")
        
        return env.lower()
    
    def _load_secrets(self) -> None:
        """
        Charge tous les secrets depuis les différentes sources.
        
        Ordre de priorité :
        1. Variables d'environnement (plus haute priorité)
        2. Fichiers .env
        3. Fichiers secrets YAML locaux
        4. Fichiers secrets YAML d'environnement
        5. Fichiers secrets par défaut (plus basse priorité)
        """
        logger.info(f"Chargement des secrets pour l'environnement '{self.env}'")
        
        # Chargement dans l'ordre de priorité croissante
        self._load_from_yaml_files()
        self._load_from_dotenv()
        self._load_from_environment()
        
        # Validation finale
        self._validate_loaded_secrets()
        
        logger.info(f"Chargement des secrets terminé pour l'environnement '{self.env}'")
    
    def _load_from_yaml_files(self) -> None:
        """Charge les secrets depuis les fichiers YAML."""
        yaml_files = self._get_yaml_file_paths()
        
        for file_path, source_type in yaml_files:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        secrets_data = yaml.safe_load(file) or {}
                        self._merge_secrets(secrets_data, SecretSource.YAML_FILE)
                        logger.debug(f"Secrets chargés depuis {file_path}")
                        
                except yaml.YAMLError as e:
                    logger.error(f"Erreur de format YAML dans {file_path}: {e}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    def _get_yaml_file_paths(self) -> list:
        """
        Retourne les chemins des fichiers YAML dans l'ordre de priorité.
        
        Returns:
            Liste des tuples (chemin, type_source)
        """
        secrets_dir = self.base_path / "secrets"
        
        return [
            (secrets_dir / "default_secrets.yaml", SecretSource.DEFAULT),
            (secrets_dir / f"{self.env}_secrets.yaml", SecretSource.YAML_FILE),
            (secrets_dir / "local_secrets.yaml", SecretSource.YAML_FILE),
        ]
    
    def _load_from_dotenv(self) -> None:
        """Charge les secrets depuis les fichiers .env."""
        dotenv_files = self._get_dotenv_file_paths()
        
        for file_path in dotenv_files:
            if file_path.exists():
                try:
                    load_dotenv(dotenv_path=file_path, override=True)
                    logger.debug(f"Variables d'environnement chargées depuis {file_path}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du fichier .env {file_path}: {e}")
    
    def _get_dotenv_file_paths(self) -> list:
        """
        Retourne les chemins des fichiers .env dans l'ordre de priorité.
        
        Returns:
            Liste des chemins de fichiers .env
        """
        return [
            self.base_path / ".env",
            self.base_path / f".env.{self.env}",
            self.base_path / ".env.local",
        ]
    
    def _load_from_environment(self) -> None:
        """Charge les secrets depuis les variables d'environnement."""
        # Préfixes pour les variables d'environnement
        prefixes = [f"{self.env.upper()}_", "GITLAB_", "SONARQUBE_", "DEFECTDOJO_"]
        
        for key, value in os.environ.items():
            for prefix in prefixes:
                if key.startswith(prefix):
                    self._parse_environment_variable(key, value)
                    break
    
    def _parse_environment_variable(self, key: str, value: str) -> None:
        """
        Parse une variable d'environnement et l'ajoute aux secrets.
        
        Args:
            key: Nom de la variable
            value: Valeur de la variable
        """
        # Exemple: GITLAB_API_URL -> gitlab.api_url
        try:
            parts = key.lower().split("_")
            if len(parts) >= 2:
                section = parts[0]
                field = "_".join(parts[1:])
                
                if section not in self.secrets:
                    self.secrets[section] = {}
                
                self.secrets[section][field] = value
                self._secret_sources[f"{section}.{field}"] = SecretSource.ENVIRONMENT
                
        except Exception as e:
            logger.warning(f"Impossible de parser la variable d'environnement {key}: {e}")
    
    def _merge_secrets(self, secrets_data: Dict[str, Any], source: SecretSource) -> None:
        """
        Fusionne les données de secrets avec les données existantes.
        
        Args:
            secrets_data: Données à fusionner
            source: Source des données
        """
        if not isinstance(secrets_data, dict):
            logger.warning(f"Données de secrets invalides (type: {type(secrets_data)})")
            return
        
        for section, values in secrets_data.items():
            if not isinstance(values, dict):
                logger.warning(f"Section '{section}' invalide: doit être un dictionnaire")
                continue
            
            if section not in self.secrets:
                self.secrets[section] = {}
            
            for key, value in values.items():
                # Enregistrer la source du secret
                self._secret_sources[f"{section}.{key}"] = source
                
                # Fusionner la valeur
                self.secrets[section][key] = value
    
    def _validate_loaded_secrets(self) -> None:
        """Valide les secrets chargés."""
        if not self.secrets:
            logger.warning("Aucun secret chargé")
            return
        
        # Vérifier les sections critiques
        critical_sections = ["gitlab"]
        
        for section in critical_sections:
            if section not in self.secrets:
                logger.error(f"Section critique '{section}' manquante dans les secrets")
            else:
                self._validate_section(section)
    
    def _validate_section(self, section: str) -> None:
        """
        Valide une section spécifique des secrets.
        
        Args:
            section: Nom de la section à valider
        """
        section_data = self.secrets.get(section, {})
        
        if section == "gitlab":
            required_fields = ["api_url", "private_token"]
            for field in required_fields:
                if not section_data.get(field):
                    logger.error(f"Champ obligatoire manquant: {section}.{field}")
    
    def get_secret(self, section: str, key: str, default: Any = None) -> Any:
        """
        Récupère un secret spécifique.
        
        Args:
            section: Section du secret
            key: Clé du secret
            default: Valeur par défaut si le secret n'existe pas
            
        Returns:
            Valeur du secret ou valeur par défaut
        """
        try:
            return self.secrets.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du secret {section}.{key}: {e}")
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Récupère une section complète des secrets.
        
        Args:
            section: Nom de la section
            
        Returns:
            Dictionnaire contenant tous les secrets de la section
        """
        return self.secrets.get(section, {}).copy()
    
    def has_secret(self, section: str, key: str) -> bool:
        """
        Vérifie si un secret existe.
        
        Args:
            section: Section du secret
            key: Clé du secret
            
        Returns:
            True si le secret existe, False sinon
        """
        return section in self.secrets and key in self.secrets[section]
    
    def get_secret_source(self, section: str, key: str) -> Optional[SecretSource]:
        """
        Récupère la source d'un secret.
        
        Args:
            section: Section du secret
            key: Clé du secret
            
        Returns:
            Source du secret ou None si non trouvé
        """
        return self._secret_sources.get(f"{section}.{key}")
    
    def list_secrets(self) -> Dict[str, list]:
        """
        Liste tous les secrets disponibles (sans leurs valeurs).
        
        Returns:
            Dictionnaire des sections et leurs clés
        """
        return {
            section: list(keys.keys())
            for section, keys in self.secrets.items()
        }
    
    def save_secrets(self, section: str, secrets: Dict[str, Any]) -> None:
        """
        Sauvegarde les secrets dans le fichier local.
        
        Args:
            section: Section à sauvegarder
            secrets: Dictionnaire des secrets à sauvegarder
        """
        try:
            local_secrets_path = self.base_path / "secrets" / "local_secrets.yaml"
            
            # Charger les secrets existants
            existing_secrets = {}
            if local_secrets_path.exists():
                with open(local_secrets_path, "r", encoding="utf-8") as file:
                    existing_secrets = yaml.safe_load(file) or {}
            
            # Mettre à jour la section
            existing_secrets[section] = secrets
            
            # Sauvegarder
            with open(local_secrets_path, "w", encoding="utf-8") as file:
                yaml.safe_dump(existing_secrets, file, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Secrets sauvegardés pour la section '{section}'")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des secrets: {e}")
            raise


# Instance globale du gestionnaire de secrets
_secret_manager_instance: Optional[SecretManager] = None

def get_secret_manager(env: str = None) -> SecretManager:
    """
    Récupère l'instance globale du gestionnaire de secrets.
    
    Args:
        env: Environnement (utilise 'dev' par défaut)
        
    Returns:
        Instance du gestionnaire de secrets
    """
    global _secret_manager_instance
    
    if _secret_manager_instance is None or (env and _secret_manager_instance.env != env):
        _secret_manager_instance = SecretManager(env or "dev")
    
    return _secret_manager_instance

def get_secret(section: str, key: str, default: Any = None) -> Any:
    """
    Fonction utilitaire pour récupérer un secret.
    
    Args:
        section: Section du secret
        key: Clé du secret
        default: Valeur par défaut
        
    Returns:
        Valeur du secret
    """
    return get_secret_manager().get_secret(section, key, default)

def get_section_secrets(section: str) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer une section complète.
    
    Args:
        section: Nom de la section
        
    Returns:
        Dictionnaire des secrets de la section
    """
    return get_secret_manager().get_section(section)
