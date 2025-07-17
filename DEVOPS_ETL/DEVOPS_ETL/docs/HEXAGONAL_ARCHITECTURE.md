# Architecture Hexagonale pour DevOps ETL

Ce document décrit l'implémentation de l'architecture hexagonale (ou ports & adapters) pour le projet DevOps ETL.

## Structure de l'Architecture

L'architecture est organisée en trois couches principales :

```
src/
  ├── domain/          # Couche de domaine (cœur métier)
  │   ├── entities/    # Entités du domaine
  │   ├── value_objects/  # Objets de valeur
  │   ├── services/    # Services du domaine
  │   └── ports/       # Interfaces pour les repositories et services externes
  ├── application/     # Couche d'application (cas d'utilisation)
  │   └── use_cases/   # Implémentation des cas d'utilisation
  └── adapters/        # Couche d'adaptateurs (implémentations concrètes)
      ├── gitlab/      # Adaptateurs pour GitLab
      ├── persistence/ # Adaptateurs pour la persistance
      └── services/    # Adaptateurs pour les services externes
```

## Couches de l'Architecture

### 1. Couche de Domaine

La couche de domaine contient la logique métier essentielle, indépendante des technologies externes. Elle comprend :

- **Entités** : Objets avec une identité (Project, Developer, CodeQualityMetric, etc.)
- **Objets de valeur** : Objets immuables sans identité propre (DateRange, CommitActivity, etc.)
- **Services du domaine** : Services qui orchestrent plusieurs entités (ProjectAnalysisService)
- **Ports** : Interfaces que les adaptateurs doivent implémenter pour interagir avec le domaine

Cette couche définit les règles métier et ne dépend d'aucune technologie externe.

### 2. Couche d'Application

La couche d'application coordonne le flux d'informations entre l'interface utilisateur et la couche de domaine. Elle contient :

- **Cas d'utilisation** : Classes qui orchestrent les opérations pour répondre aux besoins utilisateur
- **DTOs** (Data Transfer Objects) : Structures de données pour l'échange avec l'extérieur

Cette couche dépend du domaine mais reste indépendante des détails d'infrastructure.

### 3. Couche d'Adaptateurs

La couche d'adaptateurs contient les implémentations concrètes des interfaces définies par le domaine :

- **Adaptateurs GitLab** : Implémentations des repositories utilisant l'API GitLab
- **Adaptateurs de persistance** : Implémentations pour stocker les données
- **Adaptateurs de services** : Implémentations des services externes (notification, logging, etc.)

Cette couche dépend des technologies externes et implémente les ports définis par le domaine.

## Flux de Données

1. **Entrée** : Une requête arrive via un point d'entrée (CLI, API, etc.)
2. **Application** : Un cas d'utilisation orchestres les opérations nécessaires
3. **Domaine** : La logique métier est exécutée via les entités et services
4. **Adaptateurs** : Les données sont récupérées ou persistées via les adaptateurs
5. **Sortie** : La réponse est formatée et renvoyée au client

## Avantages de cette Architecture

- **Testabilité** : La logique métier peut être testée indépendamment des frameworks et technologies
- **Flexibilité** : Les implémentations d'infrastructure peuvent être remplacées sans modifier le domaine
- **Maintainabilité** : Séparation claire des responsabilités entre les différentes couches
- **Évolution** : Possibilité d'ajouter de nouvelles fonctionnalités sans modifier le code existant

## Utilisation

Voir le script de démonstration `scripts/demo_hexagonal.py` pour un exemple d'utilisation de cette architecture.

```python
# Création des adaptateurs
gitlab_client = GitLabClient(url="...", token="...")
project_repo = GitLabProjectRepository(gitlab_client)

# Utilisation d'un cas d'utilisation
use_case = ExportProjectsUseCase(project_repo)
output_file = use_case.execute(output_path="export.csv")
```
