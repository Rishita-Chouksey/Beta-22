from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field

class SchemeRule(BaseModel):
    field: str = Field(..., description="Profile field key to evaluate against")
    operator: str = Field(..., description="Rule operator: eq, ne, in, not_in, lte, gte, between, or")
    value: Any = Field(..., description="Expected value, threshold or [min, max] range")
    description_en: str = Field(..., description="Human-readable rule explanation in English")
    description_hi: str = Field(..., description="Human-readable rule explanation in Hindi")
    is_external_unverifiable: bool = Field(False, description="Flag for rules requiring offline/external verification")
    or_rules: Optional[List['SchemeRule']] = Field(default=None, description="Optional sub-rules where any passing satisfies the condition")

class DocumentRequirement(BaseModel):
    id: str = Field(..., description="Unique document ID (e.g. aadhaar, income_cert)")
    name_en: str = Field(..., description="Document title in English")
    name_hi: str = Field(..., description="Document title in Hindi")
    purpose_en: str = Field(..., description="Why this document is required")
    purpose_hi: str = Field(..., description="दस्तावेज़ की आवश्यकता का कारण")
    how_to_get_en: str = Field(..., description="Procurement steps in English")
    how_to_get_hi: str = Field(..., description="दस्तावेज़ प्राप्त करने की प्रक्रिया")
    online_url: Optional[str] = Field(None, description="Official portal link to apply online")
    offline_office: Optional[str] = Field(None, description="Physical authority/office to visit if offline")

class SchemeDefinition(BaseModel):
    id: str = Field(..., description="Unique scheme identifier (e.g. pm_kisan)")
    name_en: str = Field(..., description="Official scheme name in English")
    name_hi: str = Field(..., description="Official scheme name in Hindi")
    level: str = Field("central", description="'central' or 'state'")
    applicable_states: List[str] = Field(default_factory=lambda: ["ALL"], description="States where applicable or ['ALL']")
    category: str = Field("General", description="Sector (e.g. Agriculture, Education, Women, Housing, Health)")
    benefit_en: str = Field(..., description="Key financial or material entitlement")
    benefit_hi: str = Field(..., description="मुख्य लाभ विवरण")
    description_en: str = Field(..., description="Overview in English")
    description_hi: str = Field(..., description="Overview in Hindi")
    rules: List[SchemeRule] = Field(default_factory=list, description="List of deterministic eligibility criteria")
    restrictions: List[str] = Field(default_factory=list, description="Important disqualification restrictions")
    required_documents: List[DocumentRequirement] = Field(default_factory=list, description="Document checklist items")
    application_procedure: List[str] = Field(default_factory=list, description="Step-by-step application process")
    official_source_url: str = Field(..., description="Official portal URL")
    last_verified_date: str = Field(..., description="ISO date YYYY-MM-DD of last manual verification")
    max_allowed_age_days: int = Field(180, description="Verification staleness threshold in days")
    verification_status: str = Field("verified", description="'verified', 'unverified', or 'stale'")
    conflicting_schemes: List[str] = Field(default_factory=list, description="Scheme IDs that cannot be co-benefited")
    helpline: Optional[str] = Field(None, description="Toll-free helpline or helpdesk contact")
