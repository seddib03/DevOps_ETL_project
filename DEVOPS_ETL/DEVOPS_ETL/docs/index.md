# Documentation du Projet DevOps ETL

Bienvenue dans la documentation du projet DevOps ETL, une solution complète d'extraction, transformation et chargement de données provenant d'outils DevOps pour l'analyse de la productivité et de la qualité.

## Table des matières

1. [Guide d'Onboarding](01_ONBOARDING.md)
   - Guide de démarrage pour les nouveaux développeurs
   - Installation et configuration du projet
   - Premier pas avec le système

2. [Architecture Détaillée](02_ARCHITECTURE.md)
   - Vue d'ensemble de l'architecture
   - Principes de conception
   - Structure du projet
   - Flux de données
   - Modules principaux
   - Patterns de conception utilisés

3. [Modèle de Données](03_DATA_MODEL.md)
   - Description des dimensions et faits
   - Schéma de données
   - Relations entre entités
   - Stratégie d'historisation

4. [Décisions d'Architecture (ADR)](04_ADR/001_initial_architecture.md)
   - [ADR-001: Architecture Initiale](04_ADR/001_initial_architecture.md)
   - Autres ADRs...

5. [Statut des Dépendances](DEPENDENCIES_STATUS.md)
   - Liste des bibliothèques utilisées
   - Versions compatibles
   - Problèmes connus

## Sources de données prises en charge

- **GitLab** : Commits, merge requests, issues, pipelines
- **SonarQube** : Métriques de qualité de code, code smells, vulnérabilités
- **DefectDojo** : Rapports de sécurité, vulnérabilités, conformité
- **Dependency Track** : Analyse des dépendances, vulnérabilités des composants

## Principaux KPIs

### Productivité
- Vélocité par développeur/équipe
- Temps moyen de cycle (de l'ouverture d'une issue à sa livraison)
- Temps moyen de review des MRs
- Fréquence des déploiements

### Qualité
- Dette technique
- Couverture de code
- Densité de bugs
- Nombre de vulnérabilités (par sévérité)
- Respect des standards de code

