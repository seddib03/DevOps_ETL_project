# Guide des Conventions de Nomenclature - ETL DevOps

## Vue d'ensemble

Ce guide définit les conventions de nomenclature pour le projet ETL DevOps, basées sur les meilleures pratiques Python (PEP 8) et les standards modernes de développement.

## 1. Conventions Python (PEP 8)

### Variables et Fonctions
- **Format**: `snake_case` (minuscules avec underscores)
- **Exemples**:
  ```python
  # ✅ Correct
  user_name = "admin"
  last_activity_date = datetime.now()
  api_response_timeout = 30
  
  # ❌ Incorrect
  userName = "admin"
  lastActivityDate = datetime.now()
  APIResponseTimeout = 30
  ```

### Classes
- **Format**: `PascalCase` (première lettre majuscule pour chaque mot)
- **Exemples**:
  ```python
  # ✅ Correct
  class GitLabClient:
  class UserDataValidator:
  class APIConnectionError:
  
  # ❌ Incorrect
  class gitlabClient:
  class userDataValidator:
  class apiConnectionError:
  ```

### Constantes
- **Format**: `UPPER_SNAKE_CASE` (majuscules avec underscores)
- **Exemples**:
  ```python
  # ✅ Correct
  DEFAULT_TIMEOUT = 30
  MAX_RETRY_ATTEMPTS = 3
  API_BASE_URL = "https://gitlab.oncf.net"
  
  # ❌ Incorrect
  default_timeout = 30
  MaxRetryAttempts = 3
  apiBaseUrl = "https://gitlab.oncf.net"
  ```

### Modules et Packages
- **Format**: `snake_case` (minuscules avec underscores si nécessaire)
- **Exemples**:
  ```python
  # ✅ Correct
  gitlab_client.py
  secret_manager.py
  api_exceptions.py
  
  # ❌ Incorrect
  GitLabClient.py
  SecretManager.py
  APIExceptions.py
  ```

## 2. Conventions Spécifiques au Projet

### Noms de Fichiers

#### Scripts
- **Format**: `{action}_{resource}_{type}.py`
- **Exemples**:
  ```python
  # ✅ Correct
  export_gitlab_users.py
  validate_sonarqube_connection.py
  transform_dependency_data.py
  
  # ❌ Incorrect
  gitlab_users_export.py  # ordre inversé
  GitLabUsersExport.py    # PascalCase
  export-gitlab-users.py # hyphens
  ```

#### Modules de Code
- **Format**: `{domain}_{type}.py`
- **Exemples**:
  ```python
  # ✅ Correct
  gitlab_client.py
  sonarqube_extractor.py
  user_transformer.py
  data_validator.py
  
  # ❌ Incorrect
  GitLabClient.py
  SonarQubeExtractor.py
  ```

#### Fichiers de Configuration
- **Format**: `{env}_{type}.yaml`
- **Exemples**:
  ```yaml
  # ✅ Correct
  dev_secrets.yaml
  prod_config.yaml
  local_settings.yaml
  
  # ❌ Incorrect
  secrets-dev.yaml
  ProdConfig.yaml
  LocalSettings.yaml
  ```

### Variables et Attributs

#### Variables d'Instance
- **Format**: `snake_case`
- **Attributs privés**: préfixe `_`
- **Exemples**:
  ```python
  # ✅ Correct
  self.api_url = config.get("api_url")
  self.private_token = config.get("private_token")
  self._gitlab_client = None  # privé
  
  # ❌ Incorrect
  self.apiUrl = config.get("api_url")
  self.privateToken = config.get("private_token")
  self.__gitlab_client = None  # double underscore réservé
  ```

#### Variables de Configuration
- **Format**: descriptif et explicite
- **Exemples**:
  ```python
  # ✅ Correct
  gitlab_api_timeout = config.get("timeout", 30)
  max_retry_attempts = config.get("max_retries", 3)
  ssl_verification_enabled = config.get("verify_ssl", True)
  
  # ❌ Incorrect
  timeout = config.get("timeout", 30)
  retries = config.get("max_retries", 3)
  ssl = config.get("verify_ssl", True)
  ```

### Méthodes et Fonctions

#### Méthodes Publiques
- **Format**: verbe d'action + objet
- **Exemples**:
  ```python
  # ✅ Correct
  def extract_users(self) -> List[Dict]:
  def validate_connection(self) -> bool:
  def transform_user_data(self, user: Dict) -> Dict:
  
  # ❌ Incorrect
  def users(self) -> List[Dict]:  # pas de verbe
  def connection(self) -> bool:   # pas de verbe
  def userTransform(self, user: Dict) -> Dict:  # camelCase
  ```

#### Méthodes Privées
- **Format**: préfixe `_` + verbe d'action
- **Exemples**:
  ```python
  # ✅ Correct
  def _validate_config(self, config: Dict) -> None:
  def _create_gitlab_client(self) -> gitlab.Gitlab:
  def _parse_response_data(self, response: Dict) -> List:
  
  # ❌ Incorrect
  def __validate_config(self, config: Dict) -> None:  # double underscore
  def validateConfig(self, config: Dict) -> None:     # camelCase
  ```

## 3. Conventions de Domaine Métier

### Entités GitLab
- **Format**: préfixe du domaine + entité
- **Exemples**:
  ```python
  # ✅ Correct
  gitlab_user_data = {}
  gitlab_project_info = {}
  gitlab_merge_request = {}
  
  # ❌ Incorrect
  user_data = {}      # trop générique
  project_info = {}   # trop générique
  mr = {}             # abréviation
  ```

### Données Transformées
- **Format**: suffixe indiquant le type de données
- **Exemples**:
  ```python
  # ✅ Correct
  enriched_user_data = []
  validated_project_list = []
  transformed_statistics = {}
  
  # ❌ Incorrect
  enriched_users = []    # pas assez spécifique
  valid_projects = []    # ambiguë
  stats = {}             # abréviation
  ```

## 4. Conventions de Fichiers de Sortie

### Fichiers Excel
- **Format**: `{resource}_{timestamp}.xlsx`
- **Exemples**:
  ```python
  # ✅ Correct
  gitlab_users_2025-07-15--1030.xlsx
  sonarqube_projects_2025-07-15--1030.xlsx
  
  # ❌ Incorrect
  users_export.xlsx               # pas de timestamp
  GitLabUsers_2025-07-15.xlsx     # PascalCase
  gitlab-users-20250715.xlsx      # hyphens et format date
  ```

### Fichiers de Log
- **Format**: `{application}_{level}_{date}.log`
- **Exemples**:
  ```python
  # ✅ Correct
  etl_info_2025-07-15.log
  gitlab_error_2025-07-15.log
  
  # ❌ Incorrect
  app.log                  # pas de date
  ETL_INFO_2025-07-15.log  # majuscules
  ```

## 5. Recommandations Spécifiques

### Améliorations Suggérées pour le Projet Actuel

#### Fichiers à Renommer
```python
# Actuel → Recommandé
gitlab_users_export.py → export_gitlab_users.py
gitlab_users_export_optimized.py → export_gitlab_users_optimized.py
secret_manager.py → secret_manager.py ✅ (déjà correct)
gitlab_client.py → gitlab_client.py ✅ (déjà correct)
```

#### Variables à Améliorer
```python
# Dans gitlab_client.py
# Actuel → Recommandé
self.gl → self._gitlab_client
self.user_info → self._current_user_info
self.is_connected → self._connection_status

# Dans secret_manager.py
# Actuel → Recommandé
self.secrets → self._loaded_secrets
self.base_path → self._config_base_path
```

#### Méthodes à Renommer
```python
# Actuel → Recommandé
def extract() → def extract_resources()
def connect() → def establish_connection()
def test_connection() → def validate_connection()
```

### Constantes à Définir
```python
# À ajouter dans un fichier constants.py
DEFAULT_GITLAB_TIMEOUT = 30
DEFAULT_GITLAB_MAX_RETRIES = 3
DEFAULT_GITLAB_RETRY_DELAY = 5
DEFAULT_GITLAB_ITEMS_PER_PAGE = 100

SUPPORTED_GITLAB_RESOURCES = [
    "users", "projects", "groups", "issues", "merge_requests"
]

EXCEL_EXPORT_COLUMNS = [
    "idUser", "Username", "FullName", "Email", "AccountStatus",
    "CreatedDate", "LastActivityDate", "IsAdmin", "InactivityDays",
    "DataQualityScore", "ProfileUrl", "AccountType"
]
```

## 6. Outils de Validation

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
```

### Configuration Flake8
```ini
# setup.cfg
[flake8]
max-line-length = 100
exclude = .git,__pycache__,docs/source/conf.py,old,build,dist
ignore = E203,W503
```

## 7. Documentation des Conventions

### Docstrings
```python
def extract_gitlab_users(self, active_only: bool = False) -> List[Dict[str, Any]]:
    """
    Extrait les utilisateurs GitLab avec options de filtrage.
    
    Args:
        active_only: Si True, ne récupère que les utilisateurs actifs
        
    Returns:
        Liste des utilisateurs GitLab sous forme de dictionnaires
        
    Raises:
        APIConnectionError: Si une erreur de connexion survient
        
    Example:
        >>> client = GitLabClient(config)
        >>> users = client.extract_gitlab_users(active_only=True)
        >>> len(users)
        42
    """
```

### Type Hints
```python
from typing import Dict, List, Optional, Union, Any

def process_user_data(
    user_data: Dict[str, Any],
    include_inactive: bool = False
) -> Optional[Dict[str, Union[str, int, bool]]]:
    """Process user data with type safety."""
```

## 8. Checklist de Révision

### Avant Commit
- [ ] Noms de variables en `snake_case`
- [ ] Noms de classes en `PascalCase`  
- [ ] Constantes en `UPPER_SNAKE_CASE`
- [ ] Noms de méthodes avec verbes d'action
- [ ] Attributs privés avec préfixe `_`
- [ ] Docstrings complètes avec type hints
- [ ] Noms de fichiers descriptifs et cohérents
- [ ] Variables nommées de manière explicite

Cette convention garantit un code lisible, maintenable et conforme aux standards Python.
