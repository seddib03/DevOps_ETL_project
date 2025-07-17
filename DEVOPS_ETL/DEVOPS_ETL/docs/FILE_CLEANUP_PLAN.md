# Plan de nettoyage et d'harmonisation des fichiers

## Fichiers obsolètes identifiés

### 1. Fichiers de backup/working (à supprimer)
- `src/extractors/gitlab/gitlab_client_backup.py` - Backup de l'ancien client GitLab
- `src/extractors/gitlab/gitlab_client_consolidated.py` - Fichier de travail pour consolidation
- `src/extractors/gitlab/gitlab_client_improved.py` - Version améliorée maintenant intégrée

### 2. Scripts redondants (à évaluer)
- `scripts/export_gitlab_users_improved.py` - Version améliorée
- `scripts/export_gitlab_users_hex.py` - Version hexagonale
- `scripts/gitlab_users_export_optimized.py` - Version optimisée
- `scripts/gitlab_users_export.py` - Version de base

### 3. Gestionnaires de secrets multiples (à harmoniser)
- `config/secrets/secret_manager.py` - Version de base (245 lignes)
- `config/secrets/secret_manager_optimized.py` - Version optimisée (400 lignes)  
- `config/secrets/secret_manager_enhanced.py` - Version améliorée (492 lignes)

### 4. Tests potentiellement obsolètes
- `tests/unit/test_secrets_enhanced.py` - Tests pour version enhanced
- `tests/unit/test_sonarqube_connection_enhanced.py` - Tests enhanced

## Recommandations de nomenclature

### Fichiers principaux (à conserver)
1. `secret_manager_enhanced.py` → `secret_manager.py` (version finale)
2. `test_secrets_enhanced.py` → `test_secrets.py` (tests finaux)
3. `test_runner_enhanced.py` → `test_runner.py` (version finale)

### Scripts à harmoniser
1. `export_gitlab_users_improved.py` → `export_gitlab_users.py` (version finale)
2. `gitlab_users_export_optimized.py` → supprimer (redondant)
3. `export_gitlab_users_hex.py` → conserver si architecture hexagonale active

## Actions proposées

### Phase 1 : Nettoyage des fichiers obsolètes
1. Supprimer les fichiers backup/consolidated
2. Supprimer les anciennes versions des secret managers
3. Supprimer les scripts redondants

### Phase 2 : Harmonisation des noms
1. Renommer les fichiers enhanced vers les noms finaux
2. Mettre à jour les imports dans le code
3. Vérifier les références dans la documentation

### Phase 3 : Validation
1. Exécuter les tests pour vérifier l'intégrité
2. Tester les scripts principaux
3. Mettre à jour la documentation

## Critères de décision

### À conserver :
- Version enhanced/optimized si elle est plus complète
- Fichiers actuellement utilisés par les scripts principaux
- Tests fonctionnels

### À supprimer :
- Fichiers backup/working
- Versions antérieures non utilisées
- Scripts redondants sans valeur ajoutée

### À renommer :
- Fichiers avec suffixes enhanced/optimized/improved vers noms standards
- Maintenir la cohérence avec les conventions PEP 8
