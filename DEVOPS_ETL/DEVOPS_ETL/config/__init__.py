"""
Module de configuration centrale pour l'application ETL DevOps.

Ce module expose une interface unifiée pour accéder aux configurations et secrets
de l'application, indépendamment de leur mécanisme de stockage sous-jacent.
"""

from config.settings import get_secret, get_config_value, get_environment
from config.secrets import get_section_secrets, get_secret_manager

__all__ = [
    'get_secret',           # Récupérer un secret (format: 'section.key')
    'get_section_secrets',  # Récupérer toute une section de secrets
    'get_config_value',     # Récupérer une valeur de configuration non sensible
    'get_environment',      # Obtenir l'environnement courant
    'get_secret_manager'    # Accès direct au gestionnaire de secrets (avancé)
]
