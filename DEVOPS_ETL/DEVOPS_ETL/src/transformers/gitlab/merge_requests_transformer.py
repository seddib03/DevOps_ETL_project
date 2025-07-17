"""
Module de transformation des merge requests GitLab.
"""
from typing import List, Dict
from datetime import datetime

def transform_merge_requests(merge_requests: List[Dict]) -> List[Dict]:
    """
    Transforme la liste des merge requests en un format standardisé.
    
    Args:
        merge_requests: Liste de dictionnaires représentant les merge requests.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for mr in merge_requests:
        transformed_mr = {
            "id": mr.get("id"),
            "title": mr.get("title"),
            "state": mr.get("state"),
            "created_at": datetime.strptime(mr.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if mr.get("created_at") else None,
            "updated_at": datetime.strptime(mr.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if mr.get("updated_at") else None,
            "author": mr.get("author", {}).get("name"),
            "web_url": mr.get("web_url"),
            "source_branch": mr.get("source_branch"),
            "target_branch": mr.get("target_branch")
        }
        # Ajouter d'autres champs si nécessaire
        if transformed_mr["state"] == "merged":
            transformed_mr["merged_at"] = datetime.strptime(mr.get("merged_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if mr.get("merged_at") else None