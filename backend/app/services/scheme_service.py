import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..models.scheme import SchemeDefinition
from ..config import settings

logger = logging.getLogger("scheme_service")

class SchemeService:
    def __init__(self, schemes_dir: Optional[Path] = None):
        self.schemes_dir = schemes_dir or settings.SCHEMES_DIR
        self._cache: Dict[str, SchemeDefinition] = {}
        self.load_schemes()

    def load_schemes(self) -> None:
        """Reads and validates all .json files in the schemes directory."""
        self._cache.clear()
        if not self.schemes_dir.exists():
            logger.warning(f"Schemes directory {self.schemes_dir} does not exist.")
            return

        for file_path in self.schemes_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    scheme = SchemeDefinition(**data)
                    self._cache[scheme.id] = scheme
            except Exception as e:
                logger.error(f"Failed to load scheme file {file_path}: {e}")

    def get_all_schemes(self) -> List[SchemeDefinition]:
        """Returns all loaded schemes."""
        if not self._cache:
            self.load_schemes()
        return list(self._cache.values())

    def get_scheme_by_id(self, scheme_id: str) -> Optional[SchemeDefinition]:
        """Returns single scheme definition or None."""
        if not self._cache:
            self.load_schemes()
        return self._cache.get(scheme_id)

    def get_rules_status(self) -> Dict[str, Any]:
        """Returns audit status of all scheme rules in library."""
        schemes = self.get_all_schemes()
        today = date.today()
        
        verified_count = 0
        stale_count = 0
        unverified_count = 0
        summary_list = []

        for s in schemes:
            try:
                v_date = datetime.strptime(s.last_verified_date, "%Y-%m-%d").date()
                age = (today - v_date).days
                is_stale = age > s.max_allowed_age_days
            except Exception:
                age = 999
                is_stale = True

            if s.verification_status != "verified":
                status = "unverified"
                unverified_count += 1
            elif is_stale:
                status = "stale"
                stale_count += 1
            else:
                status = "verified"
                verified_count += 1

            summary_list.append({
                "id": s.id,
                "name_en": s.name_en,
                "name_hi": s.name_hi,
                "level": s.level,
                "status": status,
                "last_verified_date": s.last_verified_date,
                "age_days": age,
                "rules_count": len(s.rules),
                "official_source_url": s.official_source_url
            })

        return {
            "total_schemes": len(schemes),
            "verified_schemes": verified_count,
            "stale_schemes": stale_count,
            "unverified_schemes": unverified_count,
            "schemes_summary": summary_list
        }

scheme_service = SchemeService()
