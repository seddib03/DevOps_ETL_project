from typing import Any, Dict, List, Optional
from datetime import datetime
def transform_projects(projects: List[Dict]) -> List[Dict]:
    """
    Transforme la liste des projets en un format standardisé.
    
    Args:
        projects: Liste de dictionnaires représentant les projets.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for project in projects:
        transformed_project = {
            "id": project.get("id"),
            "name": project.get("name"),
            "description": project.get("description"),
            "created_at": datetime.strptime(project.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if project.get("created_at") else None,
            "web_url": project.get("web_url"),
            "namespace": project.get("namespace", {}).get("name"),
            "visibility": project.get("visibility"),
            "default_branch": project.get("default_branch")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_project)
    return transformed