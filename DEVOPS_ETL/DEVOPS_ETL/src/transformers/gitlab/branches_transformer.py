from typing import Any, Dict, List, Optional
from datetime import datetime

def transform_branches(branches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme la liste des branches en un format standardisé.
    
    Args:
        branches: Liste de dictionnaires représentant les branches.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for branch in branches:
        transformed_branch = {
            "name": branch.get("name"),
            "commit_id": branch.get("commit", {}).get("id"),
            "commit_message": branch.get("commit", {}).get("message"),
            "created_at": datetime.strptime(branch.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if branch.get("created_at") else None,
            "web_url": branch.get("web_url")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_branch)
    return transformed