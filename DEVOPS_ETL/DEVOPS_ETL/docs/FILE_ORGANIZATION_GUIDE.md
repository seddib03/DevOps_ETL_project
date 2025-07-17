# Guide d'organisation des fichiers et conventions

## 🎯 Objectif

Ce guide établit les conventions d'organisation des fichiers et de structure du projet DevOps ETL selon les meilleures pratiques de développement Python.

## 📁 Structure de projet standardisée

### Principe d'organisation

```
DEVOPS_ETL/
├── 📂 src/                    # Code source principal
│   ├── 📂 core/               # Fonctionnalités centrales
│   ├── 📂 extractors/         # Extracteurs de données
│   ├── 📂 transformers/       # Transformateurs de données
│   ├── 📂 loaders/           # Chargeurs de données
│   └── 📂 models/            # Modèles de données
├── 📂 scripts/               # Scripts d'exécution
├── 📂 tests/                 # Tests automatisés
│   ├── 📂 unit/              # Tests unitaires
│   ├── 📂 integration/       # Tests d'intégration
│   ├── 📂 fixtures/          # Données de test
│   └── 📂 utils/             # Utilitaires de test
├── 📂 utils/                 # Utilitaires de maintenance
├── 📂 config/                # Configuration
├── 📂 docs/                  # Documentation
├── 📂 data/                  # Données et exports
└── 📂 requirements/          # Dépendances
```

## 🏗️ Conventions de nommage des fichiers

### 1. Fichiers Python (`.py`)

#### Modules et packages
- **Format** : `snake_case`
- **Exemples** :
  - ✅ `gitlab_client.py`
  - ✅ `secret_manager.py`
  - ✅ `data_processor.py`
  - ❌ `GitLabClient.py`
  - ❌ `secretManager.py`

#### Scripts exécutables
- **Format** : `action_resource_modifier.py`
- **Exemples** :
  - ✅ `export_gitlab_users_improved.py`
  - ✅ `clean_project_cache.py`
  - ✅ `verify_excel_export.py`
  - ❌ `gitlab_export.py`
  - ❌ `cleanup.py`

#### Tests
- **Format** : `test_module_name.py`
- **Exemples** :
  - ✅ `test_gitlab_client.py`
  - ✅ `test_secrets_enhanced.py`
  - ✅ `test_sonarqube_connection_enhanced.py`
  - ❌ `gitlab_test.py`
  - ❌ `TestSecrets.py`

### 2. Fichiers de configuration

#### YAML/JSON
- **Format** : `environment_purpose.yaml`
- **Exemples** :
  - ✅ `local_secrets.yaml`
  - ✅ `dev_environment.yaml`
  - ✅ `prod_database.json`
  - ❌ `secrets.yaml`
  - ❌ `config.json`

#### Fichiers de requirements
- **Format** : `requirements-purpose.txt`
- **Exemples** :
  - ✅ `requirements.txt`
  - ✅ `requirements-dev.txt`
  - ✅ `requirements-test.txt`
  - ❌ `dev_requirements.txt`
  - ❌ `test-requirements.txt`

### 3. Fichiers de documentation

#### Markdown
- **Format** : `TITLE_PURPOSE.md` (UPPER_CASE pour documents importants)
- **Exemples** :
  - ✅ `README.md`
  - ✅ `NAMING_CONVENTIONS.md`
  - ✅ `ARCHITECTURE.md`
  - ✅ `CODE_IMPROVEMENTS_SUMMARY.md`
  - ❌ `readme.md`
  - ❌ `naming-conventions.md`

## 📂 Organisation par répertoire

### `/src/` - Code source

#### Principe
- **Un module par fonctionnalité**
- **Hiérarchie claire par domaine**
- **Séparation des responsabilités**

#### Structure recommandée
```
src/
├── core/
│   ├── __init__.py
│   ├── constants.py           # Constantes globales
│   ├── exceptions.py          # Exceptions personnalisées
│   ├── logging.py             # Configuration logging
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py      # Utilitaires de date
│       └── string_utils.py    # Utilitaires de chaînes
├── extractors/
│   ├── __init__.py
│   ├── base_extractor.py      # Classe de base
│   ├── gitlab/
│   │   ├── __init__.py
│   │   ├── gitlab_client_improved.py  # Client principal
│   │   └── users_gateway.py           # Gateway utilisateurs
│   └── sonarqube/
│       ├── __init__.py
│       ├── sonarqube_client.py
│       └── projects_gateway.py
```

### `/scripts/` - Scripts d'exécution

#### Principe
- **Scripts utilisables directement**
- **Fonctionnalité spécifique par script**
- **Noms explicites avec action**

#### Convention de nommage
```
<action>_<resource>_<modifier>.py
```

#### Exemples
```
scripts/
├── export_gitlab_users_improved.py    # Export utilisateurs GitLab
├── export_sonarqube_projects.py       # Export projets SonarQube
├── generate_audit_report.py           # Génération rapport d'audit
└── sync_database_users.py             # Synchronisation utilisateurs
```

### `/tests/` - Tests automatisés

#### Principe
- **Mirroir de la structure src/**
- **Tests unitaires isolés**
- **Tests d'intégration séparés**

#### Structure recommandée
```
tests/
├── __init__.py
├── conftest.py                        # Configuration pytest
├── unit/
│   ├── __init__.py
│   ├── test_constants.py              # Tests des constantes
│   ├── test_exceptions.py             # Tests des exceptions
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── test_base_extractor.py
│   │   ├── gitlab/
│   │   │   ├── __init__.py
│   │   │   └── test_gitlab_client.py
│   │   └── sonarqube/
│   │       ├── __init__.py
│   │       └── test_sonarqube_client.py
│   └── transformers/
├── integration/
│   ├── __init__.py
│   ├── test_gitlab_integration.py     # Tests d'intégration GitLab
│   └── test_sonarqube_integration.py  # Tests d'intégration SonarQube
├── fixtures/
│   ├── __init__.py
│   ├── gitlab_users_sample.json       # Données de test GitLab
│   └── sonarqube_projects_sample.json # Données de test SonarQube
└── utils/
    ├── __init__.py
    └── test_runner_enhanced.py        # Utilitaires de test
```

### `/utils/` - Utilitaires de maintenance

#### Principe
- **Outils de maintenance**
- **Scripts de support**
- **Utilitaires de diagnostic**

#### Exemples
```
utils/
├── __init__.py
├── clean_project.py                   # Nettoyage du projet
├── verify_excel_export.py             # Vérification des exports
├── generate_documentation.py          # Génération de documentation
└── database_maintenance.py            # Maintenance base de données
```

### `/config/` - Configuration

#### Principe
- **Configuration par environnement**
- **Secrets sécurisés**
- **Paramètres modulaires**

#### Structure recommandée
```
config/
├── __init__.py
├── settings.py                        # Configuration principale
├── environments/
│   ├── local.yaml                     # Configuration locale
│   ├── dev.yaml                       # Configuration développement
│   └── prod.yaml                      # Configuration production
└── secrets/
    ├── __init__.py
    ├── secret_manager_enhanced.py     # Gestionnaire de secrets
    ├── local_secrets.yaml             # Secrets locaux
    └── dev_secrets.yaml               # Secrets développement
```

### `/docs/` - Documentation

#### Principe
- **Documentation technique**
- **Guides d'utilisation**
- **Décisions architecturales**

#### Structure recommandée
```
docs/
├── index.md                           # Page d'accueil
├── 01_ONBOARDING.md                   # Guide d'intégration
├── 02_ARCHITECTURE.md                 # Architecture technique
├── 03_DATA_MODEL.md                   # Modèle de données
├── NAMING_CONVENTIONS.md              # Conventions de nommage
├── CODE_IMPROVEMENTS_SUMMARY.md       # Améliorations du code
├── SCRIPTS_INDEX.md                   # Index des scripts
└── 04_ADR/                            # Architecture Decision Records
    ├── 001_initial_architecture.md
    └── 002_naming_conventions.md
```

## 🔍 Règles de validation

### 1. Validation des noms de fichiers

#### Script de validation
```python
def validate_file_name(file_path: Path) -> bool:
    """Valide le nom d'un fichier selon les conventions."""
    file_name = file_path.name
    
    # Fichiers Python
    if file_name.endswith('.py'):
        return re.match(r'^[a-z][a-z0-9_]*\.py$', file_name) is not None
    
    # Fichiers de test
    if file_name.startswith('test_'):
        return re.match(r'^test_[a-z][a-z0-9_]*\.py$', file_name) is not None
    
    # Fichiers de configuration
    if file_name.endswith(('.yaml', '.yml', '.json')):
        return re.match(r'^[a-z][a-z0-9_]*\.(yaml|yml|json)$', file_name) is not None
    
    return True
```

### 2. Structure des imports

#### Ordre recommandé
```python
# 1. Imports standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 2. Imports third-party
import gitlab
import pandas as pd
import yaml

# 3. Imports locaux
from src.core.constants import GITLAB_API_TIMEOUT
from src.core.exceptions import APIConnectionError
from src.extractors.base_extractor import BaseExtractor
```

### 3. Conventions de documentation

#### Docstring de module
```python
"""
Module de gestion des utilisateurs GitLab.

Ce module fournit les fonctionnalités pour extraire, transformer
et charger les données utilisateur depuis GitLab.
"""
```

#### Docstring de classe
```python
class GitLabUserManager:
    """
    Gestionnaire des utilisateurs GitLab avec conventions améliorées.
    
    Cette classe fournit une interface standardisée pour gérer
    les utilisateurs GitLab avec les meilleures pratiques.
    
    Attributes:
        _gitlab_client: Client GitLab configuré
        _logger: Logger pour les messages
    """
```

#### Docstring de fonction
```python
def extract_gitlab_users(self, include_bot_accounts: bool = True) -> List[Dict[str, Any]]:
    """
    Extrait les utilisateurs GitLab avec filtrage optionnel.
    
    Args:
        include_bot_accounts: Si True, inclut les comptes bots
        
    Returns:
        Liste des utilisateurs GitLab avec leurs métadonnées
        
    Raises:
        APIConnectionError: Si la connexion GitLab échoue
        APIAuthenticationError: Si l'authentification échoue
    """
```

## 🛠️ Outils de validation

### 1. Pre-commit hooks

#### Configuration `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
```

### 2. Configuration IDE

#### VS Code settings.json
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.provider": "isort",
    "files.watcherExclude": {
        "**/__pycache__/**": true,
        "**/.pytest_cache/**": true
    }
}
```

## 📊 Métriques de qualité

### 1. Indicateurs de structure

- **Profondeur maximale** : 4 niveaux de répertoires
- **Fichiers par répertoire** : Maximum 20 fichiers
- **Taille des modules** : Maximum 500 lignes
- **Complexité cyclomatique** : Maximum 10 par fonction

### 2. Conventions de nommage

- **Cohérence** : 100% des fichiers respectent les conventions
- **Lisibilité** : Noms explicites et sans abréviation
- **Longueur** : Noms de 3 à 50 caractères
- **Descriptivité** : Noms auto-documentés

## 🚀 Migration progressive

### Phase 1 : Nouveaux fichiers (✅ Terminée)
- Appliquer les conventions à tous les nouveaux fichiers
- Utiliser les templates standardisés
- Valider avec les outils de contrôle

### Phase 2 : Réorganisation (✅ Terminée)
- Déplacer les fichiers dans la bonne structure
- Supprimer les doublons et fichiers obsolètes
- Mettre à jour les imports et références

### Phase 3 : Refactorisation (En cours)
- Renommer les fichiers existants selon les conventions
- Restructurer le code selon les principes
- Mettre à jour la documentation

### Phase 4 : Validation (À venir)
- Tests de régression complets
- Validation des performances
- Formation de l'équipe

---
*Guide d'organisation - Version 1.0*
*Date: 15 juillet 2025*
*Projet DevOps ETL - Équipe Data Engineering*
