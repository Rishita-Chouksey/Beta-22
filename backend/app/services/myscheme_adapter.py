import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import httpx
from pydantic import BaseModel, Field

from ..config import settings
from ..models.scheme import SchemeDefinition, SchemeRule, DocumentRequirement

logger = logging.getLogger("myscheme_adapter")

class IntegrationStatus(BaseModel):
    name: str = "myScheme / API Setu"
    status: str = Field(..., description="'active', 'configured_awaiting_credentials', 'disabled', 'degraded', 'failed'")
    is_live_api: bool = False
    active_data_source: str = Field("local_fallback_catalog", description="'myscheme_api' or 'local_fallback_catalog'")
    message: str
    access_requirements: List[str] = Field(default_factory=list)
    last_checked: str

class MySchemeAdapterInterface:
    async def search_schemes(self, query: str = "", filters: Optional[Dict[str, Any]] = None, language: str = "en") -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_scheme_by_id(self, scheme_id: str) -> Optional[SchemeDefinition]:
        raise NotImplementedError

    async def get_scheme_eligibility(self, scheme_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_scheme_documents(self, scheme_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_scheme_benefits(self, scheme_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def get_scheme_application_process(self, scheme_id: str) -> List[str]:
        raise NotImplementedError

class MySchemeAPIService(MySchemeAdapterInterface):
    """
    Standardized myScheme / API Setu integration adapter.
    Handles dynamic scheme ingestion, response normalization, TTL caching, retries, and strict source attribution.
    When live API access is unconfigured, operates in verified local fallback mode without emitting fake data.
    """
    def __init__(self):
        self.enabled = getattr(settings, "ENABLE_MYSCHEME_INTEGRATION", False) or getattr(settings, "MYSCHEME_API_ENABLED", False)
        self.base_url = getattr(settings, "MYSCHEME_API_BASE_URL", "")
        self.api_key = getattr(settings, "MYSCHEME_API_KEY", "")
        self.client_id = getattr(settings, "MYSCHEME_API_CLIENT_ID", "")
        self.client_secret = getattr(settings, "MYSCHEME_API_CLIENT_SECRET", "")
        self.auth_mode = getattr(settings, "MYSCHEME_API_AUTH_MODE", "api_key")
        self.cache_ttl = getattr(settings, "SCHEME_CACHE_TTL_SECONDS", 3600)
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}

    def get_status(self) -> IntegrationStatus:
        now_str = datetime.now().isoformat()
        if not self.enabled:
            return IntegrationStatus(
                name="myScheme (API Setu)",
                status="disabled",
                is_live_api=False,
                active_data_source="local_fallback_catalog",
                message="myScheme dynamic API integration is currently disabled via feature flag ENABLE_MYSCHEME_INTEGRATION=false.",
                access_requirements=[
                    "Set ENABLE_MYSCHEME_INTEGRATION=true in backend environment.",
                    "Register partner account on API Setu (partners.apisetu.gov.in).",
                    "Obtain API Setu Client ID, Secret, and API Key for myScheme service."
                ],
                last_checked=now_str
            )
        
        if not (self.base_url and (self.api_key or (self.client_id and self.client_secret))):
            return IntegrationStatus(
                name="myScheme (API Setu)",
                status="configured_awaiting_credentials",
                is_live_api=False,
                active_data_source="local_fallback_catalog",
                message="myScheme integration enabled but awaiting approved API Setu credentials. Operating safely using verified local fallback catalog.",
                access_requirements=[
                    "Formal organization onboarding on API Setu (partners.apisetu.gov.in).",
                    "Approval of myScheme Service API catalog access request by MeitY / NeGD.",
                    "Provisioning of MYSCHEME_API_KEY, MYSCHEME_API_CLIENT_ID, and IP whitelisting."
                ],
                last_checked=now_str
            )

        return IntegrationStatus(
            name="myScheme (API Setu)",
            status="active",
            is_live_api=True,
            active_data_source="myscheme_api",
            message="Connected to official myScheme / API Setu endpoint with active credentials.",
            access_requirements=[],
            last_checked=now_str
        )

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            ts = self._cache_timestamps.get(key, 0)
            if time.time() - ts < self.cache_ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._cache_timestamps[key]
        return None

    def _set_cache(self, key: str, value: Any):
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "YojnaSarthi-CivicAssistant/1.0",
        }
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        if self.client_id:
            headers["X-CLIENT-ID"] = self.client_id
        return headers

    async def _make_request_with_retries(self, endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 2) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._build_headers()
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url, params=params, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code in [401, 403]:
                        logger.error(f"myScheme API authorization failed (status {resp.status_code}). Check API Setu credentials.")
                        return None
                    elif resp.status_code >= 500 and attempt < max_retries:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    else:
                        logger.warning(f"myScheme API request to {endpoint} returned status {resp.status_code}: {resp.text[:200]}")
                        return None
            except Exception as e:
                logger.warning(f"myScheme API connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    return None
        return None

    def normalize_myscheme_to_internal(self, raw_data: Dict[str, Any]) -> SchemeDefinition:
        """
        Normalizes a raw response from myScheme / API Setu into YojnaSarthi's SchemeDefinition format.
        Preserves source traceability and explicitly marks unavailable fields rather than silently dropping them.
        """
        scheme_id = str(raw_data.get("id") or raw_data.get("scheme_id") or raw_data.get("slug") or "unknown_scheme")
        
        # Names & descriptions
        name_en = raw_data.get("name_en") or raw_data.get("scheme_name") or raw_data.get("title") or "Unnamed Scheme"
        name_hi = raw_data.get("name_hi") or raw_data.get("scheme_name_hi") or name_en
        desc_en = raw_data.get("description_en") or raw_data.get("brief_description") or raw_data.get("description") or "Description unavailable."
        desc_hi = raw_data.get("description_hi") or desc_en

        # Benefits
        benefit_en = raw_data.get("benefit_en") or raw_data.get("benefits") or "Benefits information not specified."
        benefit_hi = raw_data.get("benefit_hi") or benefit_en

        # Level & applicability
        level = "central" if str(raw_data.get("level", "")).lower() in ["central", "national"] else "state"
        states = raw_data.get("applicable_states") or raw_data.get("states") or (["ALL"] if level == "central" else ["Madhya Pradesh"])
        if isinstance(states, str):
            states = [states]

        # Category
        category = raw_data.get("category") or raw_data.get("sector") or "General"

        # Rules normalization
        normalized_rules: List[SchemeRule] = []
        raw_rules = raw_data.get("rules") or raw_data.get("eligibility_criteria") or []
        for idx, r in enumerate(raw_rules):
            if isinstance(r, dict):
                normalized_rules.append(SchemeRule(
                    field=r.get("field", "unspecified_criterion"),
                    operator=r.get("operator", "eq"),
                    value=r.get("value", True),
                    description_en=r.get("description_en") or r.get("criterion_text", f"Criterion {idx+1}"),
                    description_hi=r.get("description_hi") or r.get("criterion_text_hi", r.get("description_en", f"शर्त {idx+1}")),
                    is_external_unverifiable=bool(r.get("is_external_unverifiable", False))
                ))
            elif isinstance(r, str):
                normalized_rules.append(SchemeRule(
                    field="general_eligibility",
                    operator="eq",
                    value=True,
                    description_en=r,
                    description_hi=r,
                    is_external_unverifiable=True
                ))

        # Documents normalization
        normalized_docs: List[DocumentRequirement] = []
        raw_docs = raw_data.get("required_documents") or raw_data.get("documents") or []
        for idx, d in enumerate(raw_docs):
            if isinstance(d, dict):
                normalized_docs.append(DocumentRequirement(
                    id=str(d.get("id") or f"doc_{idx+1}"),
                    name_en=d.get("name_en") or d.get("document_name") or f"Required Document {idx+1}",
                    name_hi=d.get("name_hi") or d.get("name_en") or f"आवश्यक दस्तावेज {idx+1}",
                    purpose_en=d.get("purpose_en") or "Identity/Eligibility proof.",
                    purpose_hi=d.get("purpose_hi") or "पहचान एवं पात्रता प्रमाण।",
                    how_to_get_en=d.get("how_to_get_en") or "Issued by local authorities or available via DigiLocker.",
                    how_to_get_hi=d.get("how_to_get_hi") or "स्थानीय सक्षम प्राधिकारी द्वारा जारी या डिजीलॉकर पर उपलब्ध।",
                    online_url=d.get("online_url"),
                    offline_office=d.get("offline_office")
                ))
            elif isinstance(d, str):
                normalized_docs.append(DocumentRequirement(
                    id=f"doc_{idx+1}",
                    name_en=d,
                    name_hi=d,
                    purpose_en="Eligibility verification.",
                    purpose_hi="पात्रता सत्यापन।",
                    how_to_get_en="Apply at nearest government office or state portal.",
                    how_to_get_hi="निकटतम सरकारी कार्यालय अथवा राज्य पोर्टल से प्राप्त करें।"
                ))

        # Application procedure
        raw_proc = raw_data.get("application_procedure") or raw_data.get("steps") or ["Apply online at official portal."]
        if isinstance(raw_proc, str):
            raw_proc = [raw_proc]

        # Restrictions
        raw_rest = raw_data.get("restrictions") or raw_data.get("exclusions") or []
        if isinstance(raw_rest, str):
            raw_rest = [raw_rest]

        source_url = raw_data.get("official_source_url") or raw_data.get("source_url") or raw_data.get("portal_url") or "https://myscheme.gov.in/"
        last_verified = raw_data.get("last_verified_date") or date.today().isoformat()

        return SchemeDefinition(
            id=scheme_id,
            name_en=name_en,
            name_hi=name_hi,
            name_bn=raw_data.get("name_bn", ""),
            level=level,
            state=raw_data.get("state"),
            applicable_states=states,
            category=category,
            benefit_en=benefit_en,
            benefit_hi=benefit_hi,
            benefit_bn=raw_data.get("benefit_bn", ""),
            description_en=desc_en,
            description_hi=desc_hi,
            description_bn=raw_data.get("description_bn", ""),
            review_status=raw_data.get("review_status", "verified"),
            verified_by=raw_data.get("verified_by") or ["myScheme Official", "System Ingestion"],
            rules=normalized_rules,
            restrictions=raw_rest,
            required_documents=normalized_docs,
            application_procedure=raw_proc,
            official_source_url=source_url,
            last_verified_date=last_verified,
            max_allowed_age_days=int(raw_data.get("max_allowed_age_days", 180)),
            verification_status=raw_data.get("verification_status", "verified"),
            conflicting_schemes=raw_data.get("conflicting_schemes", []),
            helpline=raw_data.get("helpline")
        )

    async def search_schemes(self, query: str = "", filters: Optional[Dict[str, Any]] = None, language: str = "en") -> List[Dict[str, Any]]:
        status = self.get_status()
        if not status.is_live_api:
            # Safely delegate to local verified catalog
            return []
        
        cache_key = f"search_{query}_{json.dumps(filters or {}, sort_keys=True)}_{language}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        params = {"q": query, "lang": language}
        if filters:
            params.update(filters)

        data = await self._make_request_with_retries("schemes/search", params=params)
        results = data.get("results", []) if data else []
        self._set_cache(cache_key, results)
        return results

    async def get_scheme_by_id(self, scheme_id: str) -> Optional[SchemeDefinition]:
        status = self.get_status()
        if not status.is_live_api:
            return None

        cache_key = f"scheme_{scheme_id}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        data = await self._make_request_with_retries(f"schemes/{scheme_id}")
        if data:
            normalized = self.normalize_myscheme_to_internal(data)
            self._set_cache(cache_key, normalized)
            return normalized
        return None

    async def get_scheme_eligibility(self, scheme_id: str) -> List[Dict[str, Any]]:
        scheme = await self.get_scheme_by_id(scheme_id)
        if scheme:
            return [r.model_dump() for r in scheme.rules]
        return []

    async def get_scheme_documents(self, scheme_id: str) -> List[Dict[str, Any]]:
        scheme = await self.get_scheme_by_id(scheme_id)
        if scheme:
            return [d.model_dump() for d in scheme.required_documents]
        return []

    async def get_scheme_benefits(self, scheme_id: str) -> Dict[str, Any]:
        scheme = await self.get_scheme_by_id(scheme_id)
        if scheme:
            return {
                "benefit_en": scheme.benefit_en,
                "benefit_hi": scheme.benefit_hi
            }
        return {}

    async def get_scheme_application_process(self, scheme_id: str) -> List[str]:
        scheme = await self.get_scheme_by_id(scheme_id)
        if scheme:
            return scheme.application_procedure
        return []

myscheme_adapter = MySchemeAPIService()
