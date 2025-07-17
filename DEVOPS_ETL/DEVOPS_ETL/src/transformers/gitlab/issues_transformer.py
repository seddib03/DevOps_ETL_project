from typing import Any, Dict, List, Optional
from datetime import datetime

def transform_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme la liste des issues en un format standardisé.
    
    Args:
        issues: Liste de dictionnaires représentant les issues.
        
    Returns:
        Liste de dictionnaires transformés avec les champs standardisés.
    """
    transformed = []
    for issue in issues:
        transformed_issue = {
            "id": issue.get("id"),
            "title": issue.get("title"),
            "state": issue.get("state"),
            "created_at": datetime.strptime(issue.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if issue.get("created_at") else None,
            "updated_at": datetime.strptime(issue.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") if issue.get("updated_at") else None,
            "author": issue.get("author", {}).get("name"),
            "web_url": issue.get("web_url"),
            "labels": issue.get("labels", []),
            "assignees": [assignee.get("name") for assignee in issue.get("assignees", [])],
            "due_date": datetime.strptime(issue.get("due_date"), "%Y-%m-%d") if issue.get("due_date") else None,
            "confidential": issue.get("confidential", False)
        }
        # Ajouter d'autres champs si nécessaire
        transformed.append(transformed_issue)
    return transformed