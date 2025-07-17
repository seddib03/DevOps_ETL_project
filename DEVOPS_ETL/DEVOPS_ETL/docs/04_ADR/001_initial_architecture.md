# ADR-001: Architecture Initiale du Projet DevOps ETL

## Statut

Accepté

## Date

2023-11-10

## Contexte

Le projet DevOps ETL a pour objectif d'extraire des données depuis divers outils DevOps (GitLab, SonarQube, DefectDojo, Dependency Track) afin de générer des KPIs permettant d'évaluer la performance des équipes et la qualité des projets. Nous avons besoin d'une architecture robuste, évolutive et maintenable pour répondre à ces besoins.

## Décision

Nous adoptons une architecture hexagonale (aussi connue sous le nom d'architecture "ports et adaptateurs") avec une approche Domain-Driven Design (DDD) pour organiser le projet. Cette architecture permettra une séparation claire des préoccupations et facilitera l'ajout de nouveaux outils ou sources de données.

### Principes architecturaux

1. **Hexagonal/Clean Architecture** : Séparer le domaine métier des détails techniques
2. **Domain-Driven Design** : Modéliser le domaine avec précision
3. **Dependency Injection** : Faciliter les tests et l'inversion de dépendances
4. **SOLID Principles** : Guider la conception des composants

### Structure de projet

```
src/
   analytics/          # Logique d'analyse et de calcul des KPIs
   core/               # Composants fondamentaux (config, logging, etc.)
   domain/             # Modèle de domaine (entités, value objects)
   extractors/         # Adaptateurs pour extraire les données des sources externes
   loaders/            # Adaptateurs pour charger les données transformées
   models/             # Modèles de données pour le stockage
   orchestration/      # Orchestration du pipeline ETL
   shared/             # Éléments partagés entre les composants
   transformers/       # Transformation des données brutes en modèle domaine
   validators/         # Validation des données
```

### Flux de données

1. **Extraction** : Les extracteurs récupèrent les données brutes des sources externes
2. **Transformation** : Les transformateurs convertissent ces données en modèle domaine
3. **Validation** : Les validateurs garantissent l'intégrité et la cohérence des données
4. **Chargement** : Les chargeurs stockent les données dans leur destination finale
5. **Analyse** : Les analyseurs calculent les KPIs à partir des données chargées

## Conséquences

### Avantages

1. **Testabilité** : L'architecture favorise les tests unitaires et l'injection de dépendances
2. **Évolutivité** : Facilite l'ajout de nouvelles sources de données ou de nouveaux KPIs
3. **Maintenabilité** : Séparation claire des responsabilités
4. **Domaine central** : Focus sur le métier plutôt que sur les détails techniques
5. **Indépendance** : Minimise les couplages entre les composants

### Inconvénients

1. **Complexité initiale** : L'architecture peut sembler complexe pour les nouveaux développeurs
2. **Overhead** : Plus de code pour respecter les abstractions
3. **Courbe d'apprentissage** : Nécessite une bonne compréhension des principes architecturaux

## Options considérées

1. **Architecture en couches traditionnelle** : Plus simple mais moins flexible
2. **Architecture orientée microservices** : Plus complexe à mettre en place et à maintenir pour ce projet
3. **Approche monolithique simple** : Plus rapide à implémenter mais moins évolutive

## Remarques supplémentaires

Nous utiliserons Python 3.10 comme langage principal, avec les bibliothèques suivantes :

- **Pydantic** : Validation de données et sérialisation
- **SQLAlchemy** : ORM pour l'interaction avec les bases de données
- **Dependency Injector** : Pour l'injection de dépendances
- **Pandas** : Pour la manipulation et l'analyse des données
- **Requests** / **Python clients officiels** : Pour l'interaction avec les APIs
