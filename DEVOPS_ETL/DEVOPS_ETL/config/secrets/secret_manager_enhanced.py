"""
Gestionnaire de secrets avec conventions de nomenclature améliorées.

Ce module fournit une interface moderne et robuste pour l'accès aux secrets
avec validation, mise en cache et gestion d'erreurs selon les meilleures pratiques.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
import yaml

from src.core.exceptions import (
    ConfigurationError,
    SecurityError,
    ValidationError
)
from src.core.constants import (
    SECRET_CACHE_TTL,
    SECRET_VALIDATION_RULES,
    SUPPORTED_ENVIRONMENTS,
    FILE_PATHS,
    FILE_EXTENSIONS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)

# Configuration du logging
logger = logging.getLogger(__name__)


@dataclass
class SecretCacheEntry:
    """
    Entrée de cache pour les secrets avec métadonnées.
    
    Contient les informations nécessaires pour la gestion
    du cache des secrets et leur validation.
    """
    secret_value: Any
    cached_timestamp: float
    access_count: int = 0
    last_access_time: float = field(default_factory=time.time)
    section_name: str = ""
    secret_hash: str = ""
    
    def is_cache_expired(self, ttl_seconds: int = SECRET_CACHE_TTL) -> bool:
        """
        Vérifie si l'entrée de cache a expiré.
        
        Args:
            ttl_seconds: Durée de vie du cache en secondes
            
        Returns:
            True si le cache a expiré, False sinon
        """
        current_time = time.time()
        return (current_time - self.cached_timestamp) > ttl_seconds
    
    def update_access_metrics(self) -> None:
        """Met à jour les métriques d'accès pour cette entrée."""
        self.access_count += 1
        self.last_access_time = time.time()


class SecretValidationService:
    """
    Service de validation des secrets avec règles configurables.
    
    Ce service applique des règles de validation pour s'assurer
    que les secrets respectent les exigences de sécurité.
    """
    
    def __init__(self):
        """Initialise le service de validation."""
        self._logger = logging.getLogger(__name__)
        self._validation_rules = SECRET_VALIDATION_RULES
    
    def validate_secret_section(self, section_name: str, 
                              section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide une section de secrets selon les règles définies.
        
        Args:
            section_name: Nom de la section à valider
            section_data: Données de la section
            
        Returns:
            Résultat de la validation avec détails
            
        Raises:
            ValidationError: Si la validation échoue
        """
        validation_result = {
            "section_name": section_name,
            "validation_successful": True,
            "validation_errors": [],
            "validation_warnings": [],
            "validated_timestamp": datetime.now().isoformat()
        }
        
        # Validation des règles par section
        section_rules = self._validation_rules.get(section_name, {})
        
        # Vérification des champs obligatoires
        required_fields = section_rules.get("required_fields", [])
        missing_required_fields = [
            field for field in required_fields 
            if field not in section_data or not section_data[field]
        ]
        
        if missing_required_fields:
            error_message = f"Champs obligatoires manquants: {missing_required_fields}"
            validation_result["validation_errors"].append(error_message)
            validation_result["validation_successful"] = False
        
        # Validation des formats
        format_rules = section_rules.get("format_validation", {})
        for field_name, format_pattern in format_rules.items():
            if field_name in section_data:
                field_value = section_data[field_name]
                if not self._validate_field_format(field_value, format_pattern):
                    error_message = f"Format invalide pour {field_name}: {field_value}"
                    validation_result["validation_errors"].append(error_message)
                    validation_result["validation_successful"] = False
        
        # Validation de la sécurité
        security_checks = section_rules.get("security_checks", {})
        security_validation = self._validate_security_constraints(
            section_data, security_checks
        )
        
        if not security_validation["security_valid"]:
            validation_result["validation_errors"].extend(
                security_validation["security_errors"]
            )
            validation_result["validation_successful"] = False
        
        # Avertissements de sécurité
        validation_result["validation_warnings"].extend(
            security_validation["security_warnings"]
        )
        
        if not validation_result["validation_successful"]:
            error_details = "; ".join(validation_result["validation_errors"])
            raise ValidationError(f"Validation échouée pour {section_name}: {error_details}")
        
        return validation_result
    
    def _validate_field_format(self, field_value: Any, format_pattern: str) -> bool:
        """
        Valide le format d'un champ selon le pattern spécifié.
        
        Args:
            field_value: Valeur du champ à valider
            format_pattern: Pattern de validation
            
        Returns:
            True si le format est valide, False sinon
        """
        if not isinstance(field_value, str):
            return False
        
        # Validation des URLs
        if format_pattern == "url":
            return field_value.startswith(("http://", "https://"))
        
        # Validation des tokens GitLab (format glpat- ou autre)
        if format_pattern == "token":
            return len(field_value) >= 15  # Réduction du seuil pour les tokens GitLab
        
        # Validation des emails
        if format_pattern == "email":
            return "@" in field_value and "." in field_value
        
        return True
    
    def _validate_security_constraints(self, section_data: Dict[str, Any], 
                                     security_checks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide les contraintes de sécurité pour une section.
        
        Args:
            section_data: Données de la section
            security_checks: Règles de sécurité à appliquer
            
        Returns:
            Résultat de la validation de sécurité
        """
        security_result = {
            "security_valid": True,
            "security_errors": [],
            "security_warnings": []
        }
        
        # Vérification des tokens faibles
        if security_checks.get("check_weak_tokens", False):
            for field_name, field_value in section_data.items():
                if "token" in field_name.lower() and isinstance(field_value, str):
                    if len(field_value) < 20:
                        security_result["security_warnings"].append(
                            f"Token potentiellement faible: {field_name}"
                        )
        
        # Vérification des URLs non sécurisées
        if security_checks.get("check_insecure_urls", False):
            for field_name, field_value in section_data.items():
                if "url" in field_name.lower() and isinstance(field_value, str):
                    if field_value.startswith("http://"):
                        security_result["security_warnings"].append(
                            f"URL non sécurisée (HTTP): {field_name}"
                        )
        
        return security_result


class EnhancedSecretManager:
    """
    Gestionnaire de secrets amélioré avec conventions de nomenclature.
    
    Ce gestionnaire fournit un accès sécurisé et efficace aux secrets
    avec mise en cache intelligente et validation complète.
    """
    
    def __init__(self, environment: str = "local"):
        """
        Initialise le gestionnaire de secrets amélioré.
        
        Args:
            environment: Environnement cible (local, dev, prod)
            
        Raises:
            ConfigurationError: Si l'environnement n'est pas supporté
        """
        self._environment = environment
        self._logger = logging.getLogger(__name__)
        self._cache_lock = Lock()
        self._secret_cache: Dict[str, SecretCacheEntry] = {}
        self._validation_service = SecretValidationService()
        
        # Validation de l'environnement
        if environment not in SUPPORTED_ENVIRONMENTS:
            raise ConfigurationError(
                f"Environnement non supporté: {environment}. "
                f"Environnements supportés: {SUPPORTED_ENVIRONMENTS}"
            )
        
        # Initialisation des chemins
        self._secrets_file_path = self._build_secrets_file_path()
        self._cache_statistics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_evictions": 0,
            "validation_successes": 0,
            "validation_failures": 0
        }
        
        self._logger.info(f"Gestionnaire de secrets initialisé pour l'environnement: {environment}")
    
    def get_secret_section(self, section_name: str, 
                          use_cache: bool = True,
                          validate_data: bool = True) -> Dict[str, Any]:
        """
        Récupère une section de secrets avec mise en cache et validation.
        
        Args:
            section_name: Nom de la section à récupérer
            use_cache: Si True, utilise le cache si disponible
            validate_data: Si True, valide les données avant retour
            
        Returns:
            Données de la section de secrets
            
        Raises:
            ConfigurationError: Si la section n'existe pas
            SecurityError: Si la validation de sécurité échoue
        """
        # Vérification du cache
        if use_cache:
            cached_section = self._get_cached_section(section_name)
            if cached_section is not None:
                self._cache_statistics["cache_hits"] += 1
                return cached_section
        
        # Chargement des secrets depuis le fichier
        self._cache_statistics["cache_misses"] += 1
        
        try:
            all_secrets_data = self._load_secrets_from_file()
            
            if section_name not in all_secrets_data:
                available_sections = list(all_secrets_data.keys())
                raise ConfigurationError(
                    f"Section '{section_name}' non trouvée. "
                    f"Sections disponibles: {available_sections}"
                )
            
            section_data = all_secrets_data[section_name]
            
            # Validation des données si requise
            if validate_data:
                try:
                    self._validation_service.validate_secret_section(
                        section_name, section_data
                    )
                    self._cache_statistics["validation_successes"] += 1
                    
                except ValidationError as validation_error:
                    self._cache_statistics["validation_failures"] += 1
                    self._logger.error(f"Validation échouée pour {section_name}: {validation_error}")
                    raise SecurityError(f"Données de secrets invalides: {validation_error}")
            
            # Mise en cache des données
            if use_cache:
                self._cache_secret_section(section_name, section_data)
            
            return section_data
            
        except Exception as loading_error:
            error_message = f"Erreur de configuration des secrets: {loading_error}"
            self._logger.error(error_message)
            raise ConfigurationError(error_message)
    
    def get_secret_value(self, section_name: str, secret_key: str, 
                        default_value: Any = None) -> Any:
        """
        Récupère une valeur de secret spécifique.
        
        Args:
            section_name: Nom de la section
            secret_key: Clé du secret
            default_value: Valeur par défaut si non trouvée
            
        Returns:
            Valeur du secret ou la valeur par défaut
        """
        try:
            section_data = self.get_secret_section(section_name)
            return section_data.get(secret_key, default_value)
            
        except (ConfigurationError, SecurityError) as secret_error:
            self._logger.warning(f"Impossible de récupérer {secret_key}: {secret_error}")
            return default_value
    
    def list_available_sections(self) -> List[str]:
        """
        Liste les sections de secrets disponibles.
        
        Returns:
            Liste des noms de sections disponibles
        """
        try:
            all_secrets_data = self._load_secrets_from_file()
            return list(all_secrets_data.keys())
            
        except Exception as loading_error:
            self._logger.error(f"Erreur lors du listing des sections: {loading_error}")
            return []
    
    def refresh_cache(self) -> Dict[str, Any]:
        """
        Rafraîchit le cache des secrets.
        
        Returns:
            Statistiques du rafraîchissement
        """
        with self._cache_lock:
            cache_size_before = len(self._secret_cache)
            self._secret_cache.clear()
            
            refresh_statistics = {
                "cache_cleared": True,
                "entries_cleared": cache_size_before,
                "refresh_timestamp": datetime.now().isoformat()
            }
            
            self._logger.info(f"Cache rafraîchi: {cache_size_before} entrées supprimées")
            return refresh_statistics
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache et de la validation.
        
        Returns:
            Statistiques complètes du gestionnaire
        """
        with self._cache_lock:
            current_cache_size = len(self._secret_cache)
            cache_hit_rate = (
                self._cache_statistics["cache_hits"] / 
                max(1, self._cache_statistics["cache_hits"] + self._cache_statistics["cache_misses"])
            ) * 100
            
            validation_success_rate = (
                self._cache_statistics["validation_successes"] /
                max(1, self._cache_statistics["validation_successes"] + self._cache_statistics["validation_failures"])
            ) * 100
        
        return {
            "environment": self._environment,
            "cache_size": current_cache_size,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "validation_success_rate": round(validation_success_rate, 2),
            "statistics": self._cache_statistics.copy(),
            "secrets_file_path": str(self._secrets_file_path)
        }
    
    def _get_cached_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une section depuis le cache si disponible et valide.
        
        Args:
            section_name: Nom de la section à récupérer
            
        Returns:
            Données de la section ou None si non disponible
        """
        with self._cache_lock:
            if section_name not in self._secret_cache:
                return None
            
            cache_entry = self._secret_cache[section_name]
            
            # Vérification de l'expiration du cache
            if cache_entry.is_cache_expired():
                del self._secret_cache[section_name]
                self._cache_statistics["cache_evictions"] += 1
                return None
            
            # Mise à jour des métriques d'accès
            cache_entry.update_access_metrics()
            return cache_entry.secret_value
    
    def _cache_secret_section(self, section_name: str, section_data: Dict[str, Any]) -> None:
        """
        Met en cache une section de secrets.
        
        Args:
            section_name: Nom de la section
            section_data: Données de la section
        """
        with self._cache_lock:
            # Génération du hash pour la validation d'intégrité
            data_hash = hashlib.sha256(str(section_data).encode()).hexdigest()
            
            cache_entry = SecretCacheEntry(
                secret_value=section_data.copy(),
                cached_timestamp=time.time(),
                section_name=section_name,
                secret_hash=data_hash
            )
            
            self._secret_cache[section_name] = cache_entry
    
    def _load_secrets_from_file(self) -> Dict[str, Any]:
        """
        Charge les secrets depuis le fichier YAML.
        
        Returns:
            Dictionnaire des secrets chargés
            
        Raises:
            ConfigurationError: Si le fichier ne peut pas être chargé
        """
        if not self._secrets_file_path.exists():
            raise ConfigurationError(
                f"Fichier de secrets non trouvé: {self._secrets_file_path}"
            )
        
        try:
            with open(self._secrets_file_path, 'r', encoding='utf-8') as secrets_file:
                secrets_data = yaml.safe_load(secrets_file)
                
                if not isinstance(secrets_data, dict):
                    raise ConfigurationError("Format de fichier de secrets invalide")
                
                return secrets_data
                
        except yaml.YAMLError as yaml_error:
            raise ConfigurationError(f"Erreur de parsing YAML: {yaml_error}")
        except Exception as file_error:
            raise ConfigurationError(f"Erreur de lecture du fichier: {file_error}")
    
    def _build_secrets_file_path(self) -> Path:
        """
        Construit le chemin du fichier de secrets selon l'environnement.
        
        Returns:
            Chemin du fichier de secrets
        """
        project_root = Path(__file__).parent.parent.parent
        secrets_directory = project_root / FILE_PATHS["SECRETS_DIR"]
        
        # Sélection du fichier selon l'environnement
        if self._environment == "local":
            secrets_filename = f"local_secrets{FILE_EXTENSIONS['YAML']}"
        else:
            secrets_filename = f"{self._environment}_secrets{FILE_EXTENSIONS['YAML']}"
        
        return secrets_directory / secrets_filename


# Instance globale du gestionnaire amélioré
_enhanced_secret_manager_instance: Optional[EnhancedSecretManager] = None
_manager_lock = Lock()


def get_enhanced_secret_manager(environment: str = "local") -> EnhancedSecretManager:
    """
    Retourne une instance singleton du gestionnaire de secrets amélioré.
    
    Args:
        environment: Environnement cible
        
    Returns:
        Instance du gestionnaire de secrets
    """
    global _enhanced_secret_manager_instance
    
    with _manager_lock:
        if _enhanced_secret_manager_instance is None or _enhanced_secret_manager_instance._environment != environment:
            _enhanced_secret_manager_instance = EnhancedSecretManager(environment)
    
    return _enhanced_secret_manager_instance


def get_section_secrets(section_name: str, environment: str = "local") -> Dict[str, Any]:
    """
    Fonction de convenance pour récupérer une section de secrets.
    
    Args:
        section_name: Nom de la section
        environment: Environnement cible
        
    Returns:
        Données de la section de secrets
    """
    manager = get_enhanced_secret_manager(environment)
    return manager.get_secret_section(section_name)


def get_secret_value(section_name: str, secret_key: str, 
                    default_value: Any = None, environment: str = "local") -> Any:
    """
    Fonction de convenance pour récupérer une valeur de secret.
    
    Args:
        section_name: Nom de la section
        secret_key: Clé du secret
        default_value: Valeur par défaut
        environment: Environnement cible
        
    Returns:
        Valeur du secret ou la valeur par défaut
    """
    manager = get_enhanced_secret_manager(environment)
    return manager.get_secret_value(section_name, secret_key, default_value)
