"""
Module de configuration centralisée pour l'application ETL DevOps.

Ce module fournit un accès simplifié aux paramètres et secrets de l'application,
avec une interface unifiée pour les différents environnements.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Import direct pour éviter les importations circulaires
from config.secrets.secret_manager import get_secret_value as _get_secret_value

# Configuration du logging
logger = logging.getLogger(__name__)

# Environnement par défaut
DEFAULT_ENVIRONMENT = os.environ.get('DEVOPS_ETL_ENV', 'local')


def get_environment() -> str:
    """
    Récupère l'environnement courant depuis les variables d'environnement.
    
    Returns:
        Nom de l'environnement (local, dev, test, prod)
    """
    return os.environ.get('DEVOPS_ETL_ENV', DEFAULT_ENVIRONMENT)


def get_secret(key_path: str, default_value: Any = None) -> Any:
    """
    Récupère un secret depuis le gestionnaire de secrets.
    
    Cette fonction est une interface simplifiée qui divise le chemin de clé
    en section et clé.
    
    Args:
        key_path: Chemin de la clé au format 'section.key'
        default_value: Valeur par défaut si la clé n'existe pas
        
    Returns:
        Valeur du secret ou valeur par défaut
        
    Exemple:
        `python
        gitlab_token = get_secret('gitlab.token')
        `
    """
    if '.' not in key_path:
        logger.warning(f"Format de clé invalide: {key_path}. Utilisez 'section.key'")
        return default_value
    
    section, key = key_path.split('.', 1)
    return _get_secret_value(section, key, default_value, get_environment())


def get_config_value(key: str, default_value: Any = None) -> Any:
    """
    Récupère une valeur de configuration non sensible.
    
    Args:
        key: Clé de configuration
        default_value: Valeur par défaut
        
    Returns:
        Valeur de configuration
    """
    # Pour le moment, on utilise le même mécanisme que les secrets
    # À l'avenir, on pourrait implémenter un mécanisme séparé pour les configurations non sensibles
    return get_secret(f"config.{key}", default_value)
