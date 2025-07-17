# Plan d'harmonisation et nettoyage des fichiers

## 1. Analyse de l'existant

### Gestionnaires de secrets
- `secret_manager.py` (8,9 KB) - Version de base, utilisée par défaut via `__init__.py`
- `secret_manager_optimized.py` (14,0 KB) - Version améliorée, mentionnée dans la documentation
- `secret_manager_enhanced.py` (21,2 KB) - Version la plus complète avec validation avancée

### Clients GitLab
- `gitlab_client.py` - Version principale, hérite de BaseExtractor, utilisée par la plupart des scripts
- `gitlab_client_improved.py` - Version améliorée avec nomenclature moderne
- `gitlab_client_backup.py` - Sauvegarde de l'ancienne version
- `gitlab_client_consolidated.py` - Version de travail pour la consolidation

### Scripts d'export
- `export_gitlab_users.py` - Script standard
- `export_gitlab_users_hex.py` - Version hexagonale (architecture ports/adapters)
- `export_gitlab_users_improved.py` - Version avec nomenclature améliorée
- `gitlab_users_export.py` - Script original
- `gitlab_users_export_optimized.py` - Version optimisée

## 2. Plan d'action

### Phase 1: Nettoyage des fichiers obsolètes
1. **Supprimer les fichiers de sauvegarde et de travail**
   - `gitlab_client_backup.py`
   - `gitlab_client_consolidated.py`

2. **Supprimer la version dupliquée du client GitLab**
   - `gitlab_client_improved.py` (ses améliorations ont été intégrées dans le fichier principal)

### Phase 2: Harmonisation des gestionnaires de secrets
1. **Conserver uniquement la version enhanced**
   - Renommer `secret_manager_enhanced.py` → `secret_manager.py` (remplacer l'existant)
   - Mettre à jour `__init__.py` pour qu'il importe de la nouvelle version

2. **Supprimer les versions obsolètes**
   - `secret_manager_optimized.py`

### Phase 3: Harmonisation des scripts
1. **Conserver les versions uniques ou spécialisées**
   - `export_gitlab_users.py` - Version principale consolidée
   - `export_gitlab_users_hex.py` - Version hexagonale (architecture différente)

2. **Supprimer les versions redondantes**
   - `export_gitlab_users_improved.py` - Fusionné dans la version principale
   - `gitlab_users_export.py` - Ancien format
   - `gitlab_users_export_optimized.py` - Version intermédiaire

### Phase 4: Mise à jour de la documentation
1. **Mettre à jour les références dans le code**
   - Modifier les imports qui référencent les fichiers renommés/supprimés
   - Mettre à jour les tests unitaires

2. **Mettre à jour la documentation**
   - Modifier les guides et références dans `/docs`

## 3. Tests de validation
- Exécuter les tests unitaires après chaque phase
- Vérifier le bon fonctionnement des scripts d'export
- S'assurer que la gestion des secrets continue de fonctionner

## 4. Feuille de route d'exécution

1. ✅ Créer des sauvegardes des fichiers importants
2. ✅ Mettre à jour le gestionnaire de secrets
3. ✅ Nettoyer les fichiers de client GitLab
4. ✅ Harmoniser les scripts d'export
5. ✅ Mettre à jour la documentation
6. ✅ Exécuter les tests de validation
