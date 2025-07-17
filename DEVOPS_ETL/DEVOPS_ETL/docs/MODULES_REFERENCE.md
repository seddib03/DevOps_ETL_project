# Modules principaux du projet DevOps ETL

Ce document présente les modules principaux du projet DevOps ETL après harmonisation et optimisation.

## 1. Extracteurs de données

### 1.1 GitLab

- **GitLabClient** (`src/extractors/gitlab/gitlab_client.py`) :
  - Client principal pour interagir avec l'API GitLab
  - Implémenté avec la bibliothèque python-gitlab
  - Gère la connexion, l'authentification et les requêtes API

- **GitLabUsersGateway** (`src/extractors/gitlab/users_gateway.py`) :
  - Interface pour accéder aux utilisateurs GitLab
  - Fournit des méthodes pour récupérer et filtrer les utilisateurs

- **GitLabProjectsGateway** (`src/extractors/gitlab/projects_gateway.py`) :
  - Interface pour accéder aux projets GitLab
  - Fournit des méthodes pour récupérer les projets et leurs données associées

- **GitLabStatsExtractor** (`src/extractors/gitlab/stats_extractor.py`) :
  - Génère des statistiques à partir des données GitLab
  - Analyse les données extraites pour produire des métriques

### 1.2 SonarQube

- **SonarQubeClient** (`src/extractors/sonarqube/sonarqube_client.py`) :
  - Client pour interagir avec l'API SonarQube
  - Gère la connexion et les requêtes API

- **SonarQubeProjectsGateway** (`src/extractors/sonarqube/projects_gateway.py`) :
  - Interface pour accéder aux projets SonarQube et leurs métriques

## 2. Transformateurs de données

- **BaseTransformer** (`src/transformers/base_transformer.py`) :
  - Classe de base pour tous les transformateurs
  - Définit l'interface commune pour les transformations de données

- **TransformerService** (`src/transformers/transformer_service.py`) :
  - Orchestration des transformations
  - Applique les règles de transformation aux données extraites

- **SCDHandler** (`src/transformers/scd_handler.py`) :
  - Gestion des Slowly Changing Dimensions (Type 2)
  - Permet de suivre l'historique des modifications

- **HistoryTracker** (`src/transformers/history_tracker.py`) :
  - Suit les modifications des données au fil du temps

## 3. Chargeurs de données

- **AbstractRepository** (`src/loaders/abstract_repositories.py`) :
  - Interface générique pour la persistance des données
  - Abstraction pour différentes destinations de données

- **ExcelWriter** (`src/loaders/file_writer/excel_writer.py`) :
  - Écriture des données dans des fichiers Excel
  - Formatage et structuration des rapports

## 4. Gestion de la configuration

- **SecretManager** (`config/secrets/secret_manager.py`) :
  - Gestion des secrets et des informations d'authentification
  - Chargement à partir de fichiers YAML et variables d'environnement
  - Mise en cache pour optimiser les performances

- **Settings** (`config/settings.py`) :
  - Configuration globale de l'application
  - Paramètres spécifiques à l'environnement

## 5. Scripts d'extraction

- **export_gitlab_users.py** (`scripts/export_gitlab_users.py`) :
  - Script principal pour l'export des utilisateurs GitLab
  - Version standard consolidée

- **export_gitlab_users_hex.py** (`scripts/export_gitlab_users_hex.py`) :
  - Version hexagonale du script d'export
  - Suit l'architecture ports et adaptateurs

## 6. Tests

- **Tests unitaires** (`tests/unit/`) :
  - Tests des composants individuels
  - Validation du comportement des modules

- **Tests d'intégration** (`tests/integration/`) :
  - Tests des interactions entre composants
  - Validation des flux de bout en bout

## 7. Orchestration

- **Steps** (`src/orchestration/steps.py`) :
  - Étapes individuelles du pipeline ETL
  - Actions atomiques dans le processus d'ETL

- **Pipeline** (`src/orchestration/pipeline.py`) :
  - Orchestration du flux de travail ETL complet
  - Séquencement des étapes d'extraction, transformation et chargement

- **JobTracker** (`src/orchestration/job_tracker.py`) :
  - Suivi de l'exécution des tâches
  - Gestion des états et des journaux d'exécution

## 8. Modèles de données

- **Dimensions** (`src/models/dimensions/`) :
  - Tables de dimensions pour le modèle en étoile
  - Entités principales (projets, développeurs, dates, outils)

- **Faits** (`src/models/facts/`) :
  - Tables de faits contenant les métriques
  - Mesures liées aux dimensions (qualité du code, activité de développement, vulnérabilités)

## 9. Analytics

- **KPICalculator** (`src/analytics/kpi_calculator.py`) :
  - Calcul des indicateurs de performance clés
  - Traitement des données brutes en métriques significatives

- **KPIAggregator** (`src/analytics/kpi_aggregator.py`) :
  - Agrégation des KPI sur différentes dimensions
  - Production de tableaux de bord et de rapports

- **KPI Definitions** (`src/analytics/kpi_definitions/`) :
  - Définitions des métriques DORA, qualité et productivité
  - Formules et logique de calcul
