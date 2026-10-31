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
        # Prefer repo root data/schemes if exists, else fallback to backend/data/schemes
        root_data_schemes = Path(__file__).resolve().parent.parent.parent.parent / "data" / "schemes"
        if root_data_schemes.exists():
            self.schemes_dir = root_data_schemes
        else:
            self.schemes_dir = schemes_dir or settings.SCHEMES_DIR
            
        self._cache: Dict[str, SchemeDefinition] = {}
        self.active_data_source = "local_json_catalog"
        self.load_schemes()

    def load_schemes(self) -> None:
        """
        Loads and validates all scheme definitions directly from the JSON files.
        Stateless, deterministic, no database required.
        """
        self._cache.clear()
        
        if not self.schemes_dir.exists():
            # Try fallback directory
            fallback_dir = Path(__file__).resolve().parent.parent / "data" / "schemes"
            if fallback_dir.exists():
                self.schemes_dir = fallback_dir
            else:
                logger.warning(f"Schemes directory {self.schemes_dir} does not exist.")
                return

        for json_file in sorted(self.schemes_dir.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                scheme = SchemeDefinition(**data)
                self._cache[scheme.id] = scheme
            except Exception as e:
                logger.error(f"Error loading scheme from {json_file.name}: {e}")

        logger.info(f"Loaded {len(self._cache)} verified scheme definitions from {self.schemes_dir}.")

    def get_all_schemes(self) -> List[SchemeDefinition]:
        return list(self._cache.values())

    def get_scheme_by_id(self, scheme_id: str) -> Optional[SchemeDefinition]:
        return self._cache.get(scheme_id)

    def get_schemes_by_persona(self, persona: str) -> List[SchemeDefinition]:
        return [s for s in self._cache.values() if persona in getattr(s, "personas", [])]

    def get_rules_status(self) -> Dict[str, Any]:
        report_file = Path(__file__).resolve().parent.parent.parent.parent / "reports" / "rules-status.json"
        if report_file.exists():
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading {report_file}: {e}")

        schemes = self.get_all_schemes()
        total = len(schemes)
        verified = sum(1 for s in schemes if getattr(s, "review_status", "verified") == "verified")
        auto_updated = sum(1 for s in schemes if getattr(s, "review_status", "") == "auto_updated")
        unverified = sum(1 for s in schemes if getattr(s, "review_status", "") in ["draft", "needs_review"])
        stale = sum(1 for s in schemes if getattr(s, "is_stale", False))

        summary = []
        for s in schemes:
            summary.append({
                "id": s.id,
                "name": s.name_en,
                "review_status": getattr(s, "review_status", "verified"),
                "last_verified_date": getattr(s, "last_verified_date", None),
                "is_stale": getattr(s, "is_stale", False),
                "tracked_count": len(getattr(s, "tracked", []))
            })

        return {
            "total_schemes": total,
            "verified_schemes": verified,
            "stale_schemes": stale,
            "unverified_schemes": unverified,
            "auto_updated_schemes": auto_updated,
            "schemes_summary": summary
        }

scheme_service = SchemeService()
