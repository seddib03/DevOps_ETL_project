from typing import Any, Dict, List, Optional
from datetime import datetime
def transform_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme la liste des utilisateurs en un format standardisé.
    
    Args:
        users: Liste de dictionnaires représentant les utilisateurs.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for user in users:
        transformed_user = {
            "id": user.get("id"),
            "name": user.get("name"),
            "username": user.get("username"),
            "email": user.get("email"),
            "is_admin": user.get("is_admin", False),
            "state": user.get("state"),
            "created_at": datetime.strptime(user.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if user.get("created_at") else None,
            "last_activity_on": user.get("last_activity_on"),
            "web_url": user.get("web_url")
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_user)
    return transformed