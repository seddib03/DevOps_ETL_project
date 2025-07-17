from typing import Any, Dict, List, Optional
from datetime import datetime

def transform_pipelines(pipelines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme la liste des pipelines en un format standardisé.
    
    Args:
        pipelines: Liste de dictionnaires représentant les pipelines.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for pipeline in pipelines:
        transformed_pipeline = {
            "id": pipeline.get("id"),
            "status": pipeline.get("status"),
            "ref": pipeline.get("ref"),
            "sha": pipeline.get("sha"),
            "created_at": datetime.strptime(pipeline.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if pipeline.get("created_at") else None,
            "updated_at": datetime.strptime(pipeline.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if pipeline.get("updated_at") else None,
            "web_url": pipeline.get("web_url"),
            "user": pipeline.get("user", {}).get("name"),
            "duration": pipeline.get("duration")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_pipeline)
    return transformed