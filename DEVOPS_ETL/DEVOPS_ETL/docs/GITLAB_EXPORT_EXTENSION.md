# Extension du système d'export GitLab

Ce document décrit comment étendre le système d'export GitLab pour inclure d'autres entités.

## Structure actuelle

Le système est actuellement organisé avec la structure suivante :
```
data/
  output/
    gitlab/
      README.md       # Documentation de la structure
      users/          # Exports des utilisateurs
        gitlab_users_JJ-MM-AAAA--HHMM.xlsx
      projects/       # (à implémenter)
      groups/         # (à implémenter)
      merge_requests/ # (à implémenter)
```

## Comment ajouter une nouvelle entité

Pour ajouter l'export d'une nouvelle entité (ex: projets, groupes, etc.), suivez ces étapes :

1. **Créer un nouveau script** en utilisant le modèle existant :
   ```python
   # Exemple pour les projets
   def get_export_directory(entity_type: str) -> Path:
       """Réutiliser la fonction du script gitlab_users_export.py"""
       pass
   
   def export_projects_to_excel(projects: List, output_path: str) -> bool:
       """Adapter la fonction export_users_to_excel pour les projets"""
       pass
   
   def main():
       # ...
       # Utiliser l'API python-gitlab pour récupérer les projets
       projects = gl.projects.list(all=True)
       
       # Obtenir le répertoire d'export pour les projets
       output_dir = get_export_directory("projects")
       
       # Générer le nom du fichier
       timestamp = datetime.now().strftime("%d-%m-%Y--%H%M")
       output_file = output_dir / f"gitlab_projects_{timestamp}.xlsx"
       # ...
   ```

2. **Adapter les fonctions d'analyse** selon les besoins spécifiques de l'entité

3. **Structurer l'export Excel** de manière cohérente :
   - Feuille principale avec les données
   - Feuille "Metadata" avec des informations sur l'export
   - Feuille "Metrics" avec des statistiques

4. **Mettre à jour le README.md** dans le dossier de sortie

## Bonnes pratiques

1. **Nommage cohérent** : Utiliser le même format pour tous les exports
   - Fichiers : `gitlab_[entity]_JJ-MM-AAAA--HHMM.xlsx`
   - Fonctions : `export_[entity]_to_excel()`

2. **Documentation** : Documenter la structure et les champs exportés

3. **Statistiques** : Inclure des statistiques pertinentes pour chaque entité

4. **Tests** : Créer des tests unitaires pour valider les exports

## Exemples d'implémentation future

### Export des projets
```python
# Dans un fichier gitlab_projects_export.py
projects = gl.projects.list(all=True)
output_dir = get_export_directory("projects")
timestamp = datetime.now().strftime("%d-%m-%Y--%H%M")
output_file = output_dir / f"gitlab_projects_{timestamp}.xlsx"
```

### Export des groupes
```python
# Dans un fichier gitlab_groups_export.py
groups = gl.groups.list(all=True)
output_dir = get_export_directory("groups")
timestamp = datetime.now().strftime("%d-%m-%Y--%H%M")
output_file = output_dir / f"gitlab_groups_{timestamp}.xlsx"
```
