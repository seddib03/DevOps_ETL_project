from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class UsersTransformer(BaseTransformer):
    """
    Transformateur pour les utilisateurs GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def parse_date(date_str, fmt):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                return None

        transformed = []
        for user in data:
            created_at = parse_date(user.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(user.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            transformed_user = {
                "id": user.get("id"),
                "name": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False),
                "state": user.get("state"),
                "created_at": created_at,
                "last_activity_on": user.get("last_activity_on"),
                "web_url": user.get("web_url")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_user)
        return transformed

    def apply_scd_type2(self, existing_records: List[Dict[str, Any]], new_records: List[Dict[str, Any]], key_fields: List[str], scd_field: str, valid_from_field: str = "valid_from", valid_to_field: str = "valid_to") -> List[Dict[str, Any]]:
        """
        Applique la logique SCD Type 2 pour historiser les changements de statut (ou autre champ SCD).
        Args:
            existing_records: Liste des anciens enregistrements (déjà historisés)
            new_records: Liste des nouveaux enregistrements (après extraction/transformation)
            key_fields: Liste des champs clés pour identifier un utilisateur (ex: ["id"])
            scd_field: Champ à historiser (ex: "state")
            valid_from_field: Nom du champ date de début de validité
            valid_to_field: Nom du champ date de fin de validité
        Returns:
            Liste d'enregistrements historisés (SCD Type 2)
        """
        from datetime import datetime
        historized = []
        now = datetime.utcnow().isoformat()
        existing_lookup = {tuple(r[k] for k in key_fields): r for r in existing_records}
        for new in new_records:
            key = tuple(new[k] for k in key_fields)
            old = existing_lookup.get(key)
            if not old or old.get(scd_field) != new.get(scd_field):
                # Clôturer l'ancien enregistrement si changement
                if old:
                    old[valid_to_field] = now
                    historized.append(old)
                # Ajouter le nouveau avec valid_from
                new[valid_from_field] = now
                new[valid_to_field] = None
                historized.append(new)
        return historized