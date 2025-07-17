# Index des scripts et utilitaires

## Vue d'ensemble

Ce document répertorie tous les scripts et utilitaires disponibles dans le projet DevOps ETL après réorganisation selon les meilleures pratiques.

## 📁 Structure organisée

### Scripts principaux (`scripts/`)

#### 1. `export_gitlab_users_improved.py` ⭐ **RECOMMANDÉ**
- **Fonction** : Export des utilisateurs GitLab avec conventions améliorées
- **Utilisation** : `python scripts/export_gitlab_users_improved.py`
- **Caractéristiques** :
  - Nomenclature cohérente selon PEP 8
  - Classes spécialisées par responsabilité
  - Gestion d'erreurs robuste
  - Statistiques d'export enrichies
  - Documentation complète

#### 2. `gitlab_connection_simple.py`
- **Fonction** : Test simple de connexion GitLab
- **Utilisation** : `python scripts/gitlab_connection_simple.py`
- **Caractéristiques** :
  - Test de base de l'authentification
  - Validation de la configuration
  - Utilitaire de diagnostic

#### 3. `gitlab_stats.py`
- **Fonction** : Export des statistiques GitLab
- **Utilisation** : `python scripts/gitlab_stats.py`
- **Caractéristiques** :
  - Extraction des métriques de projets
  - Statistiques d'utilisation
  - Rapports de performance

### Scripts legacy (`scripts/` - À réviser)

#### 4. `export_gitlab_users.py` ⚠️ **LEGACY**
- **Statut** : Version antérieure, à remplacer par `export_gitlab_users_improved.py`
- **Fonction** : Export utilisateurs GitLab (version basique)

#### 5. `export_gitlab_users_hex.py` ⚠️ **LEGACY**
- **Statut** : Version hexagonale, remplacée par la version améliorée
- **Fonction** : Export utilisateurs avec architecture hexagonale

#### 6. `gitlab_users_export.py` ⚠️ **LEGACY**
- **Statut** : Version obsolète, à supprimer
- **Fonction** : Export utilisateurs (version originale)

#### 7. `gitlab_users_export_optimized.py` ⚠️ **LEGACY**
- **Statut** : Version optimisée, remplacée par la version améliorée
- **Fonction** : Export utilisateurs optimisé

### Tests (`tests/`)

#### Tests unitaires (`tests/unit/`)

##### 1. `test_secrets_enhanced.py` ⭐ **NOUVEAU**
- **Fonction** : Tests du gestionnaire de secrets amélioré
- **Utilisation** : `python -m pytest tests/unit/test_secrets_enhanced.py -v`
- **Caractéristiques** :
  - Tests du gestionnaire standard et amélioré
  - Validation des fonctionnalités de cache
  - Tests d'intégration complets

##### 2. `test_sonarqube_connection_enhanced.py` ⭐ **NOUVEAU**
- **Fonction** : Tests de connexion SonarQube améliorés
- **Utilisation** : `python -m pytest tests/unit/test_sonarqube_connection_enhanced.py -v`
- **Caractéristiques** :
  - Tests de connexion avec mocks
  - Validation de la configuration
  - Tests du gateway des projets

##### 3. `test_gitlab_connection.py`
- **Fonction** : Tests de connexion GitLab
- **Utilisation** : `python -m pytest tests/unit/test_gitlab_connection.py -v`

##### 4. `test_gitlab_client.py`
- **Fonction** : Tests du client GitLab
- **Utilisation** : `python -m pytest tests/unit/test_gitlab_client.py -v`

#### Utilitaires de tests (`tests/utils/`)

##### 1. `test_runner_enhanced.py` ⭐ **NOUVEAU**
- **Fonction** : Exécuteur de tests amélioré avec rapports
- **Utilisation** : `python tests/utils/test_runner_enhanced.py --category all --verbose`
- **Caractéristiques** :
  - Exécution par catégorie
  - Génération de rapports HTML/JSON
  - Gestion d'erreurs robuste
  - Interface en ligne de commande

### Utilitaires (`utils/`)

#### 1. `clean_project.py` ⭐ **DÉPLACÉ**
- **Fonction** : Nettoyage du projet (cache, fichiers temporaires)
- **Utilisation** : `python utils/clean_project.py`
- **Caractéristiques** :
  - Suppression des __pycache__
  - Nettoyage des fichiers temporaires
  - Suppression des anciens exports

#### 2. `verify_excel_export.py` ⭐ **DÉPLACÉ**
- **Fonction** : Vérification des fichiers Excel exportés
- **Utilisation** : `python utils/verify_excel_export.py <chemin_fichier>`
- **Caractéristiques** :
  - Validation de la structure Excel
  - Vérification de l'intégrité des données
  - Rapport de validation

## 🚀 Utilisation recommandée

### Pour l'export des utilisateurs GitLab
```bash
# Version recommandée avec toutes les améliorations
python scripts/export_gitlab_users_improved.py
```

### Pour les tests
```bash
# Tests complets avec rapport
python tests/utils/test_runner_enhanced.py --category all --verbose --report html

# Tests spécifiques
python tests/utils/test_runner_enhanced.py --category gitlab --verbose
python tests/utils/test_runner_enhanced.py --category secrets --verbose
python tests/utils/test_runner_enhanced.py --category sonarqube --verbose
```

### Pour la maintenance
```bash
# Nettoyage du projet
python utils/clean_project.py

# Vérification d'un export
python utils/verify_excel_export.py data/output/gitlab/users/gitlab_users_2025-07-15.xlsx
```

## 📊 Statut des fichiers

### ✅ Fichiers recommandés (à utiliser)
- `scripts/export_gitlab_users_improved.py`
- `scripts/gitlab_connection_simple.py`
- `scripts/gitlab_stats.py`
- `tests/unit/test_secrets_enhanced.py`
- `tests/unit/test_sonarqube_connection_enhanced.py`
- `tests/utils/test_runner_enhanced.py`
- `utils/clean_project.py`
- `utils/verify_excel_export.py`

### ⚠️ Fichiers legacy (à réviser/supprimer)
- `scripts/export_gitlab_users.py`
- `scripts/export_gitlab_users_hex.py`
- `scripts/gitlab_users_export.py`
- `scripts/gitlab_users_export_optimized.py`

### 🗑️ Fichiers supprimés
- `scripts/gitlab_users_export.py.bak`
- `scripts/test_secrets.py` (déplacé)
- `scripts/test_sonarqube_connection.py` (déplacé)
- `scripts/run_gitlab_tests.py` (remplacé)

## 🔧 Prochaines étapes

1. **Migration progressive** : Remplacer l'utilisation des scripts legacy par les versions améliorées
2. **Tests de régression** : Valider que les nouvelles versions fonctionnent correctement
3. **Documentation** : Mettre à jour les guides d'utilisation
4. **Suppression** : Supprimer les fichiers legacy après validation complète

---
*Index des scripts - Version 1.0*
*Date: 15 juillet 2025*
*Projet DevOps ETL - Équipe Data Engineering*
