# Architecture du Système ETL DevOps
## Vue d'ensemble

Ce document présente l'architecture détaillée de la solution ETL DevOps conçue pour collecter, transformer et analyser les données de productivité et de qualité provenant de différents outils DevOps (GitLab, SonarQube, DefectDojo, Dependency Track).

L'architecture suit les principes de l'Architecture Hexagonale (ou Ports et Adaptateurs) et du Domain-Driven Design (DDD) pour assurer une séparation claire des préoccupations et une évolutivité optimale.

## Principes architecturaux

### Architecture Hexagonale

L'architecture est conçue selon le principe des Ports et Adaptateurs :

- **Domaine central** : Contient les entités métier et la logique essentielle
- **Ports** : Interfaces définissant comment le domaine interagit avec l'extérieur
- **Adaptateurs** : Implémentations concrètes pour connecter le domaine aux systèmes externes

### Clean Architecture

La solution respecte également les principes de la Clean Architecture :

1. **Indépendance des frameworks** : Le cœur du système ne dépend pas des détails techniques
2. **Testabilité** : Les composants sont facilement testables de façon isolée
3. **Indépendance de l'UI** : La logique métier ne dépend pas de l'interface utilisateur
4. **Indépendance de la base de données** : Le domaine ne connaît pas les détails de persistance
5. **Indépendance des éléments externes** : Le cœur ne dépend pas des API externes

### Domain-Driven Design (DDD)

Le code est organisé autour du domaine métier :

- **Entités** : Objets avec une identité et un cycle de vie
- **Value Objects** : Objets immuables définis par leurs attributs
- **Repositories** : Abstractions pour la persistance des entités
- **Services** : Encapsulation des opérations qui ne relèvent pas naturellement des entités

## Structure du projet

```
devops_etl/
├── src/                         # Code source
│   ├── core/                    # Utilitaires et fonctionnalités transversales
│   │   ├── async_utils.py       # Utilitaires pour traitement asynchrone
│   │   ├── config.py            # Gestion de configuration
│   │   ├── logging.py           # Logging structuré
│   │   ├── exceptions.py        # Exceptions personnalisées
│   │   └── utils/               # Utilitaires divers
│   │
│   ├── domain/                  # Modèle de domaine
│   │   ├── entities/            # Entités du domaine
│   │   ├── value_objects/       # Value objects
│   │   └── repositories/        # Interfaces des repositories
│   │
│   ├── extractors/              # Extraction depuis les sources
│   │   ├── base_extractor.py    # Classe de base pour les extracteurs
│   │   ├── gitlab/              # Extracteurs GitLab
│   │   ├── sonarqube/           # Extracteurs SonarQube
│   │   ├── defect_dojo/         # Extracteurs DefectDojo
│   │   └── dependency_track/    # Extracteurs Dependency Track
│   │
│   ├── transformers/            # Transformation des données
│   │   ├── base_transformer.py  # Classe de base pour transformers
│   │   ├── scd_handler.py       # Gestion des Slowly Changing Dimensions
│   │   ├── history_tracker.py   # Suivi des changements d'état
│   │   ├── gitlab/              # Transformers spécifiques à GitLab
│   │   ├── sonarqube/           # Transformers spécifiques à SonarQube
│   │   ├── defect_dojo/         # Transformers spécifiques à DefectDojo
│   │   └── dependency_track/    # Transformers spécifiques à Dependency Track
│   │
│   ├── loaders/                 # Chargement des données
│   │   ├── abstract_repositories.py # Interfaces des repositories
│   │   ├── file_writer/         # Écriture fichier
│   │   └── database/            # Export base de données (phase 2)
│   │
│   ├── validators/              # Validation des données
│   │   ├── base_validator.py    # Classe de base pour validation
│   │   ├── gitlab/              # Validateurs GitLab
│   │   ├── sonarqube/           # Validateurs SonarQube
│   │   ├── defect_dojo/         # Validateurs DefectDojo
│   │   └── dependency_track/    # Validateurs Dependency Track
│   │
│   ├── models/                  # Modèles analytiques
│   │   ├── dimensions/          # Dimensions
│   │   ├── facts/               # Tables de faits
│   │   └── correlation/         # Corrélation entre sources
│   │
│   ├── analytics/               # Analyse et KPIs
│   │   ├── kpi_aggregator.py    # Agrégation des KPIs
│   │   ├── kpi_calculator.py    # Calcul des KPIs
│   │   └── kpi_definitions/     # Définitions des KPIs
│   │
│   ├── orchestration/           # Orchestration des pipelines
│   │   ├── pipeline.py          # Pipeline ETL
│   │   ├── steps.py             # Étapes du pipeline
│   │   └── job_tracker.py       # Suivi d'état des jobs
│   │
│   ├── shared/                  # Éléments partagés
│   │   ├── domain/              # Éléments du domaine
│   │   ├── exceptions/          # Exceptions personnalisées
│   │   └── utils/               # Utilitaires
│   │
│   ├── containers.py            # Injection de dépendances
│   └── main.py                  # Point d'entrée
```

## Flux de données

Le flux de données dans le système suit un modèle ETL classique, mais avec une approche modulaire et extensible :

1. **Extraction** : Les adaptateurs d'entrée (extractors) récupèrent les données brutes depuis les API des outils DevOps
2. **Transformation** : Les données sont transformées en modèles de domaine et alignées sur le schéma cible
3. **Validation** : Les données sont validées pour assurer leur intégrité et cohérence
4. **Chargement** : Les données transformées sont chargées dans les destinations (Excel/PostgreSQL)
5. **Analyse** : Les KPIs sont calculés à partir des données chargées

### Diagramme de flux de données

```
┌──────────┐    ┌───────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────┐
│ Sources  │───>│ Extractors│───>│ Transformers│───>│ Loaders  │───>│ Storage │
└──────────┘    └───────────┘    └─────────────┘    └──────────┘    └─────────┘
     │                │                 │                                 │
     │                │                 │                                 │
     │                │                 │                                 ▼
     │                │                 │                           ┌─────────┐
     │                │                 │                           │ Reports │
     │                │                 │                           └─────────┘
     │                │                 │
     │                │                 ▼
     │                │          ┌─────────────┐
     │                └────────> │ Validators  │
     │                           └─────────────┘
     │
     ▼
┌──────────────┐
│ Orchestrator │
└──────────────┘
```

## Modules principaux

### Core

Ce module fournit les fonctionnalités transversales utilisées par tous les autres modules :

- Configuration centralisée
- Logging structuré
- Gestion des exceptions
- Utilitaires divers

### Domain

Contient les entités métier et les règles de domaine :

- Entités représentant les concepts métier (Project, Developer, Commit, etc.)
- Value Objects pour les concepts immuables (CommitId, Version, etc.)
- Interfaces des repositories pour la persistance

### Extractors

Responsables de l'extraction des données depuis les sources externes :

- Adaptateurs pour chaque source de données (GitLab, SonarQube, etc.)
- Transformation des données brutes en modèles de domaine
- Gestion des erreurs et des retries

### Transformers

Responsables de la transformation des données en modèle analytique :

- Implémentation des règles de transformation
- Gestion des historisations (Slowly Changing Dimensions)
- Enrichissement des données

### Loaders

Chargement des données transformées vers les destinations :

- Export vers Excel (Phase 1)
- Chargement dans PostgreSQL (Phase 2)

### Validators

Validation des données pour assurer leur qualité :

- Vérification de la cohérence des données
- Détection des anomalies
- Validation des contraintes métier

### Models

Définition des modèles analytiques :

- Dimensions (Project, Developer, Date, etc.)
- Faits (Code Quality, Development Activity, etc.)
- Corrélation entre sources de données

### Analytics

Calcul et agrégation des KPIs :

- Définition des KPIs
- Calcul des métriques
- Agrégation pour le reporting

### Orchestration

Coordination du processus ETL :

- Définition des pipelines
- Gestion des dépendances entre étapes
- Suivi des jobs et reprise sur erreur

## Patterns de conception utilisés

### Inversion de dépendance

Les modules de haut niveau ne dépendent pas des modules de bas niveau, tous dépendent d'abstractions.

### Repository

Abstraction de la couche de persistance permettant de masquer les détails techniques d'accès aux données.

### Strategy

Utilisation de stratégies différentes pour les transformations selon les sources de données.

### Factory

Création d'objets complexes via des fabriques spécialisées.

### Decorator

Ajout de comportements aux composants sans modifier leur structure.

### Observer

Notification des changements d'état aux composants intéressés.

## Gestion des données historisées

Le système implémente une gestion des Slowly Changing Dimensions (SCD) de type 2 pour conserver l'historique des changements :

- Conservation des versions historiques des entités
- Gestion des dates de validité (valid_from, valid_to)
- Suivi des changements d'état

## Scalabilité et performances

L'architecture est conçue pour permettre une scalabilité horizontale :

- Traitement parallèle des différentes sources de données
- Extraction incrémentielle pour limiter le volume de données
- Mise en cache des résultats intermédiaires

## Sécurité

La sécurité est intégrée dans l'architecture :

- Stockage sécurisé des secrets (tokens API, mots de passe)
- Audit logging des actions sensibles
- Limitation des privilèges selon le principe du moindre privilège

## Phase d'implémentation

### Phase 1: Excel (POC)

- Extraction depuis les sources
- Transformation basique des données
- Export vers Excel structuré
- Dashboarding via Power BI connecté à Excel

### Phase 2: PostgreSQL (Production)

- Modèle de données dimensionnel complet
- Historisation des données (SCD Type 2)
- Orchestration avancée avec Apache Airflow
- Dashboarding via Power BI connecté à PostgreSQL

## Conclusion

Cette architecture modulaire et évolutive permet de gérer efficacement l'extraction, la transformation et l'analyse des données DevOps tout en maintenant une séparation claire des responsabilités et une facilité de maintenance.

