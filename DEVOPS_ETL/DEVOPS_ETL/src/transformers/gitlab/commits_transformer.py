from typing import Any, Dict, List, Optional
from datetime import datetime
def transform_commits(commits: List[Dict]) -> List[Dict]:
    """
    Transforme la liste des commits en un format standardisé.
    
    Args:
        commits: Liste de dictionnaires représentant les commits.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for commit in commits:
        transformed_commit = {
            "id": commit.get("id"),
            "short_id": commit.get("short_id"),
            "title": commit.get("title"),
            "author_name": commit.get("author_name"),
            "author_email": commit.get("author_email"),
            "created_at": datetime.strptime(commit.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if commit.get("created_at") else None,
            "message": commit.get("message"),
            "web_url": commit.get("web_url")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_commit)
    return transformed