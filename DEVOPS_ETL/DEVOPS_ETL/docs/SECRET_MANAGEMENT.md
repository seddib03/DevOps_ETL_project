"""
Documentation sur la gestion des secrets et la configuration dans l'ETL DevOps.

Ce document décrit l'architecture du système de gestion des secrets,
son utilisation et les meilleures pratiques associées.
"""

# Gestion des Secrets dans l'ETL DevOps

## Architecture de la gestion des secrets

Le système de gestion des secrets dans l'ETL DevOps suit une architecture en couches:

1. **Interface unifiée** (`config/__init__.py`):
   - Point d'entrée unique et simplifié pour les utilisateurs
   - Expose les fonctions `get_secret`, `get_section_secrets`, etc.

2. **Interface de configuration** (`config/settings.py`):
   - Fournit l'abstraction pour les configurations non sensibles
   - Gère les variables d'environnement et autres paramètres globaux

3. **Gestionnaire de secrets** (`config/secrets/secret_manager.py`):
   - Implémente la logique de chargement, validation et mise en cache
   - Gère différents environnements et sources de secrets

### Diagramme d'architecture

```
┌─────────────────────────────────────────┐
│ Application (scripts, services, etc.)   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Interface unifiée (config/__init__.py)  │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌────────────────┐    ┌─────────────────────────┐
│  settings.py   │    │ secret_manager.py       │
│  (non-secrets) │    │ (secret_manager.py)     │
└────────────────┘    └─────────────────────────┘
                                  │
                      ┌───────────┴──────────┐
                      │                      │
                      ▼                      ▼
               ┌─────────────┐      ┌────────────────┐
               │ YAML Files  │      │ Autres sources │
               │ par env     │      │ (futur)        │
               └─────────────┘      └────────────────┘
```

## Utilisation

### Pour les développeurs

L'utilisation recommandée est via l'interface unifiée:

```python
from config import get_secret, get_section_secrets, get_environment

# Récupérer un secret spécifique
gitlab_token = get_secret('gitlab.token')

# Récupérer une section entière
gitlab_config = get_section_secrets('gitlab')

# Connaître l'environnement courant
env = get_environment()
```

### Pour les administrateurs

La gestion des secrets se fait via les fichiers YAML dans le répertoire `config/secrets`:

- `local_secrets.yaml` - Environnement de développement local
- `dev_secrets.yaml` - Environnement de développement partagé
- `test_secrets.yaml` - Environnement de test
- `prod_secrets.yaml` - Environnement de production

Format recommandé:

```yaml
gitlab:
  url: "https://gitlab.example.com"
  token: "glpat-XXXXXXXXXXXX"
  api_version: "v4"

sonarqube:
  url: "https://sonar.example.com"
  token: "XXXXXXXX"
```

## Fonctionnalités avancées

### Mise en cache

Le gestionnaire implémente un cache sophistiqué:

- **TTL configurable**: Les secrets expirent après une durée définie
- **Statistiques**: Suivi des hits/misses du cache
- **Rafraîchissement**: Possibilité de rafraîchir explicitement le cache

### Validation

Le système valide automatiquement les secrets:

- **Format**: Vérification du format des valeurs (URLs, tokens, etc.)
- **Cohérence**: Vérification des champs obligatoires
- **Sécurité**: Détection des problèmes potentiels (tokens faibles, URLs non HTTPS)

## Bonnes pratiques

1. **Toujours utiliser l'interface unifiée**:
   ```python
   # Bon
   from config import get_secret
   
   # À éviter
   from config.secrets.secret_manager import get_secret_value
   ```

2. **Utiliser des sections et des clés cohérentes**:
   ```python
   # Structure recommandée: service.paramètre
   db_url = get_secret('database.url')
   gitlab_token = get_secret('gitlab.token')
   ```

3. **Gérer les valeurs par défaut**:
   ```python
   # Fournir une valeur par défaut pour les paramètres optionnels
   timeout = get_secret('api.timeout', 30)
   ```

4. **Éviter de stocker des secrets en dur**:
   ```python
   # À éviter absolument
   TOKEN = "glpat-XXXXXXXXXXXX"
   
   # Recommandé
   TOKEN = get_secret('gitlab.token')
   ```

## Migration et évolution

Le système actuel est basé sur des fichiers YAML, mais a été conçu pour pouvoir évoluer:

- Support futur pour AWS Secrets Manager, HashiCorp Vault, etc.
- Rotation automatique des secrets
- Audit et journalisation des accès

## Validation et dépannage

Pour valider la configuration du gestionnaire de secrets, utilisez le script dédié:

```bash
python scripts/validate_secrets.py
```

En cas de problème, vérifiez:
1. La présence des fichiers de secrets dans le bon environnement
2. Les permissions d'accès aux fichiers
3. Les variables d'environnement (`DEVOPS_ETL_ENV`)

## Référence API complète

### Interface unifiée (`config`)

| Fonction | Description | Arguments |
|----------|-------------|-----------|
| `get_secret(key_path, default_value=None)` | Récupère un secret | `key_path`: chemin au format 'section.clé'<br>`default_value`: valeur par défaut |
| `get_section_secrets(section_name)` | Récupère une section entière | `section_name`: nom de la section |
| `get_environment()` | Retourne l'environnement courant | - |
| `get_config_value(key, default_value=None)` | Récupère une valeur de config | `key`: clé de configuration<br>`default_value`: valeur par défaut |
| `get_secret_manager()` | Accès direct au gestionnaire | - |

### Gestionnaire amélioré (`EnhancedSecretManager`)

Pour les cas avancés nécessitant un accès direct au gestionnaire:

| Méthode | Description |
|---------|-------------|
| `get_secret_section(section_name, use_cache=True, validate_data=True)` | Récupère une section avec options de cache et validation |
| `get_secret_value(section_name, secret_key, default_value=None)` | Récupère une valeur spécifique |
| `list_available_sections()` | Liste les sections disponibles |
| `refresh_cache()` | Rafraîchit le cache |
| `get_cache_statistics()` | Retourne les statistiques du cache |
