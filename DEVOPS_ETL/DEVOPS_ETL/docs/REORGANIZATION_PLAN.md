# Plan d'amélioration et de réorganisation du projet

## 🎯 Problèmes identifiés

### 1. Fichiers de tests mal organisés
- `scripts/test_secrets.py` → doit être dans `tests/`
- `scripts/test_sonarqube_connection.py` → doit être dans `tests/`
- `scripts/run_gitlab_tests.py` → doit être dans `tests/`

### 2. Fichiers dupliqués et obsolètes
- `scripts/export_gitlab_users.py` vs `scripts/export_gitlab_users_improved.py`
- `scripts/gitlab_users_export.py` vs versions optimisées
- `scripts/gitlab_users_export.py.bak` → fichier de sauvegarde à supprimer
- Plusieurs versions du même script d'export

### 3. Scripts utilitaires à regrouper
- `scripts/clean_project.py` → utilitaire de maintenance
- `scripts/verify_excel_export.py` → utilitaire de vérification

## 🔧 Actions à entreprendre

### Phase 1 : Réorganisation des tests
1. Déplacer les fichiers de tests vers `tests/`
2. Créer une structure cohérente pour les tests
3. Mettre à jour les imports et références

### Phase 2 : Nettoyage des doublons
1. Identifier les fichiers obsolètes
2. Supprimer les doublons
3. Conserver uniquement les versions améliorées

### Phase 3 : Organisation des utilitaires
1. Créer un dossier `utils/` pour les utilitaires
2. Réorganiser les scripts par fonction
3. Documenter l'utilisation de chaque script

### Phase 4 : Amélioration de la documentation
1. Créer un index des scripts disponibles
2. Documenter les conventions d'organisation
3. Mettre à jour les guides d'utilisation

## 📁 Structure cible

```
scripts/
├── __init__.py
├── export_gitlab_users_improved.py    # Version finale
├── gitlab_connection_simple.py        # Utilitaire de test connexion
└── gitlab_stats.py                    # Export statistiques

tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_gitlab_connection.py
│   ├── test_gitlab_client.py
│   ├── test_secrets.py              # ← Déplacé de scripts/
│   ├── test_sonarqube_connection.py # ← Déplacé de scripts/
│   └── extractors/
├── integration/
│   └── test_gitlab_integration.py   # ← Nouveau
└── utils/
    └── test_runner.py               # ← Renommé de run_gitlab_tests.py

utils/
├── __init__.py
├── clean_project.py                 # ← Déplacé de scripts/
└── verify_excel_export.py          # ← Déplacé de scripts/
```

## 🚀 Prochaines étapes

1. **Validation de la structure** avec l'équipe
2. **Migration progressive** des fichiers
3. **Tests de régression** après chaque migration
4. **Mise à jour de la documentation**

---
*Plan d'amélioration - Version 1.0*
*Date: 15 juillet 2025*
