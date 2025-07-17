from typing import List, Dict, Any
from datetime import datetime
def transform_groups(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme la liste des groupes en un format standardisé.
    
    Args:
        groups: Liste de dictionnaires représentant les groupes.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for group in groups:
        transformed_group = {
            "id": group.get("id"),
            "name": group.get("name"),
            "path": group.get("path"),
            "description": group.get("description"),
            "visibility": group.get("visibility"),
            "created_at": datetime.strptime(group.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if group.get("created_at") else None,
            "web_url": group.get("web_url"),
            "avatar_url": group.get("avatar_url")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_group)
    return transformed