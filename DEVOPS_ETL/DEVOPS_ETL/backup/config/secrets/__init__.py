"""
Module de gestion des secrets pour l'application ETL DevOps.

Ce module permet de gérer les informations sensibles (tokens API, identifiants, etc.)
de manière centralisée et sécurisée.
"""

from .secret_manager import get_secret, get_section_secrets, get_secret_manager

__all__ = ['get_secret', 'get_section_secrets', 'get_secret_manager']
