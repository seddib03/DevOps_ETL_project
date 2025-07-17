"""
Gestionnaire de secrets pour l'application ETL DevOps.

Ce module fournit une interface unifiée pour accéder aux secrets 
(tokens d'API, identifiants, etc.) indépendamment de leur source
(fichiers, variables d'environnement, coffre-fort de secrets, etc.).
"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from dotenv import load_dotenv

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


class SecretManager:
    """
    Gestionnaire centralisé pour les secrets de l'application.
    
    Cette classe permet de charger et accéder aux secrets depuis différentes sources :
    - Fichiers YAML dans le dossier secrets
    - Variables d'environnement
    - Fichiers .env
    - (Extensible pour intégrer des solutions comme AWS Secrets Manager, Vault, etc.)
    """
    
    def __init__(self, env: str = "dev"):
        """
        Initialise le gestionnaire de secrets.
        
        Args:
            env: L'environnement actuel ('dev', 'test', 'prod', etc.)
        """
        self.env = env
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.base_path = Path(__file__).parent.parent  # Dossier config/
        self._load_secrets()
    
    def _load_secrets(self) -> None:
        """
        Charge tous les secrets depuis les différentes sources.
        L'ordre de priorité est:
        1. Variables d'environnement
        2. Fichiers .env
        3. Fichiers de secrets YAML
        """
        # Charger les secrets depuis les fichiers YAML
        self._load_from_yaml_files()
        
        # Charger depuis .env (écrase les valeurs précédentes si existe)
        self._load_from_dotenv()
        
        # Charger depuis les variables d'environnement (priorité la plus élevée)
        self._load_from_environment()
        
        logger.info(f"Chargement des secrets terminé pour l'environnement '{self.env}'")
    
    def _load_from_yaml_files(self) -> None:
        """Charge les secrets depuis les fichiers YAML."""
        # Chemin du fichier de secrets spécifique à l'environnement
        secrets_path = self.base_path / "secrets" / f"{self.env}_secrets.yaml"
        
        # Chemin du fichier de secrets local (non versionné)
        local_secrets_path = self.base_path / "secrets" / "local_secrets.yaml"
        
        # Chargement du fichier de secrets par défaut si présent
        default_secrets_path = self.base_path / "secrets" / "default_secrets.yaml"
        
        # Charger les fichiers dans l'ordre : default -> env-specific -> local
        for path in [default_secrets_path, secrets_path, local_secrets_path]:
            if path.exists():
                try:
                    with open(path, "r") as file:
                        secrets_data = yaml.safe_load(file) or {}
                        self._merge_secrets(secrets_data)
                        logger.debug(f"Secrets chargés depuis {path}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement des secrets depuis {path}: {e}")
    
    def _load_from_dotenv(self) -> None:
        """Charge les secrets depuis les fichiers .env."""
        # Fichier .env spécifique à l'environnement
        dotenv_path = self.base_path / f".env.{self.env}"
        
        # Fichier .env local (non versionné)
        local_dotenv_path = self.base_path / ".env.local"
        
        # Charger .env par défaut si présent
        default_dotenv_path = self.base_path / ".env"
        
        # Charger les fichiers dans l'ordre : default -> env-specific -> local
        for path in [default_dotenv_path, dotenv_path, local_dotenv_path]:
            if path.exists():
                try:
                    load_dotenv(dotenv_path=path, override=True)
                    logger.debug(f"Variables d'environnement chargées depuis {path}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du fichier .env {path}: {e}")
    
    def _load_from_environment(self) -> None:
        """
        Charge les secrets depuis les variables d'environnement.
        Convention: PREFIX_SECTION_KEY=value (ex: DEVOPS_ETL_GITLAB_TOKEN=xxx)
        """
        env_prefix = "DEVOPS_ETL_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Extraire la section et la clé
                parts = key[len(env_prefix):].lower().split("_", 1)
                if len(parts) == 2:
                    section, subkey = parts
                    if section not in self.secrets:
                        self.secrets[section] = {}
                    self.secrets[section][subkey] = value
                    logger.debug(f"Secret chargé depuis variable d'environnement: {section}.{subkey}")
    
    def _merge_secrets(self, new_secrets: Dict[str, Any]) -> None:
        """
        Fusionne de nouveaux secrets dans le dictionnaire existant.
        
        Args:
            new_secrets: Dictionnaire contenant les nouveaux secrets à fusionner
        """
        for section, values in new_secrets.items():
            if not isinstance(values, dict):
                continue
                
            if section not in self.secrets:
                self.secrets[section] = {}
            
            for key, value in values.items():
                self.secrets[section][key] = value
    
    def get_secret(self, section: str, key: str, default: Any = None) -> Any:
        """
        Récupère un secret spécifique.
        
        Args:
            section: Section du secret (ex: "gitlab")
            key: Clé du secret (ex: "api_token")
            default: Valeur par défaut si le secret n'existe pas
            
        Returns:
            La valeur du secret ou la valeur par défaut si non trouvé
        """
        return self.secrets.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Récupère tous les secrets d'une section.
        
        Args:
            section: Section des secrets (ex: "gitlab")
            
        Returns:
            Dictionnaire contenant tous les secrets de la section
        """
        return self.secrets.get(section, {})
    
    def set_secret(self, section: str, key: str, value: Any) -> None:
        """
        Définit ou met à jour un secret (en mémoire uniquement).
        
        Args:
            section: Section du secret (ex: "gitlab")
            key: Clé du secret (ex: "api_token")
            value: Valeur du secret
        """
        if section not in self.secrets:
            self.secrets[section] = {}
        self.secrets[section][key] = value
    
    def save_to_local(self) -> bool:
        """
        Sauvegarde les secrets actuels dans le fichier local_secrets.yaml.
        Attention : cette fonction ne doit être utilisée que pour le développement.
        
        Returns:
            True si l'opération a réussi, False sinon
        """
        try:
            local_secrets_path = self.base_path / "secrets" / "local_secrets.yaml"
            with open(local_secrets_path, "w") as file:
                yaml.safe_dump(self.secrets, file)
            logger.info(f"Secrets sauvegardés dans {local_secrets_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des secrets: {e}")
            return False


# Instance singleton du gestionnaire de secrets
_secret_manager = None


def get_secret_manager(env: str = None) -> SecretManager:
    """
    Récupère l'instance du gestionnaire de secrets.
    
    Args:
        env: Environnement à utiliser (si None, utilise l'environnement actuel)
        
    Returns:
        Instance du gestionnaire de secrets
    """
    global _secret_manager
    if _secret_manager is None or env is not None:
        current_env = env or os.environ.get("ENVIRONMENT", "dev")
        _secret_manager = SecretManager(env=current_env)
    return _secret_manager


def get_secret(section: str, key: str, default: Any = None) -> Any:
    """
    Fonction utilitaire pour récupérer un secret spécifique.
    
    Args:
        section: Section du secret (ex: "gitlab")
        key: Clé du secret (ex: "api_token")
        default: Valeur par défaut si le secret n'existe pas
        
    Returns:
        La valeur du secret ou la valeur par défaut si non trouvé
    """
    return get_secret_manager().get_secret(section, key, default)


def get_section_secrets(section: str) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer tous les secrets d'une section.
    
    Args:
        section: Section des secrets (ex: "gitlab")
        
    Returns:
        Dictionnaire contenant tous les secrets de la section
    """
    return get_secret_manager().get_section(section)

