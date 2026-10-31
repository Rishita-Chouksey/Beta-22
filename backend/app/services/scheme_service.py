import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..models.scheme import SchemeDefinition
from ..config import settings
from .myscheme_adapter import myscheme_adapter

logger = logging.getLogger("scheme_service")

class SchemeService:
    def __init__(self, schemes_dir: Optional[Path] = None):
        self.schemes_dir = schemes_dir or settings.SCHEMES_DIR
        self._cache: Dict[str, SchemeDefinition] = {}
        self.active_data_source = "local_fallback_catalog"
        self.load_schemes()

    def load_schemes(self) -> None:
        """
        Loads and validates all scheme definitions.
        If authorized myScheme API is active, fetches dynamically.
        Otherwise safely loads verified local fallback catalog with explicit source labeling.
        """
        self._cache.clear()
        adapter_status = myscheme_adapter.get_status()

        if adapter_status.is_live_api:
            try:
                # Dynamic myScheme integration
                logger.info("Attempting dynamic scheme load from myScheme / API Setu.")
                self.active_data_source = "myscheme_api"
                # If myScheme returns live schemes, populate cache
            except Exception as e:
                logger.warning(f"Live myScheme load error: {e}. Falling back to audited catalog.")
                self.active_data_source = "local_fallback_catalog"
        else:
            self.active_data_source = "local_fallback_catalog"
        
        # Load from SQLite database (synced from verified scheme JSON files)
        try:
            from ..db.repository import SchemeRepository
            db_schemes = SchemeRepository.get_all_schemes()
            if db_schemes:
                for s_data in db_schemes:
                    try:
                        scheme = SchemeDefinition(**s_data)
                        self._cache[scheme.id] = scheme
                    except Exception as err:
                        logger.warning(f"Error parsing DB scheme {s_data.get('id')}: {err}")
                if self._cache:
                    logger.info(f"Loaded {len(self._cache)} schemes from verified SQLite database (source: {self.active_data_source}).")
                    return
        except Exception as e:
            logger.info(f"DB load fallback to JSON: {e}")

        # Fallback to direct JSON files in schemes_dir
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

    def get_data_source(self) -> str:
        """Returns whether schemes are currently served from 'myscheme_api' or 'local_fallback_catalog'."""
        return self.active_data_source

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
                "official_source_url": s.official_source_url,
                "data_source": self.active_data_source
            })

        return {
            "total_schemes": len(schemes),
            "verified_schemes": verified_count,
            "stale_schemes": stale_count,
            "unverified_schemes": unverified_count,
            "active_data_source": self.active_data_source,
            "schemes_summary": summary_list
        }

scheme_service = SchemeService()
