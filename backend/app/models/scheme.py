from typing import List, Optional, Any, Union, Dict, Literal
from pydantic import BaseModel, Field, model_validator

class TrackedRule(BaseModel):
    rule_id: str = Field(..., description="Target rule ID to watch")
    extractor: str = Field(..., description="Extractor name in rules checker")
    kind: Literal[
        "amount_inr",
        "age_min",
        "age_max",
        "age_range",
        "area_ha",
        "deadline_date",
        "status_open_closed"
    ] = Field(..., description="Data kind for validation and normalization")

class AutoUpdateChange(BaseModel):
    rule_id: str
    field: str
    old: Any
    new: Any
    evidence_url: str
    evidence_snippet: str

class AutoUpdateRecord(BaseModel):
    applied_at: str = Field(..., description="ISO timestamp when update was applied")
    run_id: str = Field(..., description="Workflow run ID or bot run ID")
    changes: List[AutoUpdateChange] = Field(default_factory=list)
    checkers_agreed: bool = Field(True, description="Must be true for auto-applied changes")

class SchemeRule(BaseModel):
    field: str = Field(..., description="Profile field key to evaluate against")
    operator: str = Field(..., description="Rule operator: eq, ne, in, not_in, lte, gte, between, or")
    value: Any = Field(..., description="Expected value, threshold or [min, max] range")
    rule_id: Optional[str] = Field(None, description="Identifier for updater tracking")
    description_en: str = Field(..., description="Human-readable rule explanation in English")
    description_hi: str = Field(..., description="Human-readable rule explanation in Hindi")
    description_bn: Optional[str] = Field("", description="Human-readable rule explanation in Bengali")
    description_mr: Optional[str] = Field("", description="Human-readable rule explanation in Marathi")
    why_template: Optional[Dict[str, str]] = Field(
        default=None,
        description="Bilingual templates with {value} placeholder: {en, hi, bn}"
    )
    is_external_unverifiable: bool = Field(False, description="Flag for rules requiring offline/external verification")
    or_rules: Optional[List['SchemeRule']] = Field(default=None, description="Optional sub-rules where any passing satisfies the condition")

class DocumentRequirement(BaseModel):
    id: str = Field(..., description="Unique document ID (e.g. aadhaar, income_cert)")
    name_en: str = Field(..., description="Document title in English")
    name_hi: str = Field(..., description="Document title in Hindi")
    name_bn: Optional[str] = Field("", description="Document title in Bengali")
    name_mr: Optional[str] = Field("", description="Document title in Marathi")
    purpose_en: str = Field(..., description="Why this document is required")
    purpose_hi: str = Field(..., description="दस्तावेज़ की आवश्यकता का कारण")
    purpose_bn: Optional[str] = Field("", description="প্রয়োজনীয়তার উদ্দেশ্য")
    purpose_mr: Optional[str] = Field("", description="कागदपत्रांची आवश्यकता")
    how_to_get_en: str = Field(..., description="Procurement steps in English")
    how_to_get_hi: str = Field(..., description="दस्तावेज़ प्राप्त करने की प्रक्रिया")
    how_to_get_bn: Optional[str] = Field("", description="পাওয়ার উপায়")
    how_to_get_mr: Optional[str] = Field("", description="कागदपत्र मिळवण्याची प्रक्रिया")
    online_url: Optional[str] = Field(None, description="Official portal link to apply online")
    offline_office: Optional[str] = Field(None, description="Physical authority/office to visit if offline")

class SchemeDefinition(BaseModel):
    id: str = Field(..., description="Unique scheme identifier (e.g. pm_kisan)")
    name_en: str = Field(..., description="Official scheme name in English")
    name_hi: str = Field(..., description="Official scheme name in Hindi")
    name_bn: Optional[str] = Field("", description="Official scheme name in Bengali")
    name_mr: Optional[str] = Field("", description="Official scheme name in Marathi")
    level: Literal["central", "state"] = Field("central", description="'central' or 'state'")
    state: Optional[str] = Field(None, description="Two-letter ISO 3166-2:IN state code (e.g., MP, MH, WB), null for central")
    applicable_states: List[str] = Field(default_factory=lambda: ["ALL"], description="States where applicable or ['ALL']")
    category: str = Field("General", description="Sector (e.g. Agriculture, Education, Women, Housing, Health)")
    category_hi: Optional[str] = None
    category_bn: Optional[str] = None
    category_mr: Optional[str] = None
    personas: List[str] = Field(default_factory=list, description="Target personas: farmer, widow, student")
    benefit_en: str = Field(..., description="Key financial or material entitlement in English")
    benefit_hi: str = Field(..., description="मुख्य लाभ विवरण (हिंदी)")
    benefit_bn: Optional[str] = Field("", description="প্রধান সুবিধা বিবরণ (বাংলা)")
    benefit_mr: Optional[str] = Field("", description="मुख्य लाभ तपशील (मराठी)")
    description_en: str = Field(..., description="Overview in English")
    description_hi: str = Field(..., description="Overview in Hindi")
    description_bn: Optional[str] = Field("", description="Overview in Bengali")
    description_mr: Optional[str] = Field("", description="Overview in Marathi")
    rules: List[SchemeRule] = Field(default_factory=list, description="List of deterministic eligibility criteria")
    restrictions: List[str] = Field(default_factory=list, description="Important disqualification restrictions")
    required_documents: List[DocumentRequirement] = Field(default_factory=list, description="Document checklist items")
    application_procedure: List[str] = Field(default_factory=list, description="Step-by-step application process")
    official_source_url: str = Field(..., description="Official portal URL")
    last_verified_date: str = Field(..., description="ISO date YYYY-MM-DD of last manual verification")
    max_allowed_age_days: int = Field(180, description="Verification staleness threshold in days")
    verification_status: str = Field("verified", description="Legacy status: 'verified', 'unverified', or 'stale'")
    review_status: Literal["draft", "verified", "auto_updated", "needs_review"] = Field(
        "verified",
        description="Current review status for dynamic updater"
    )
    verified_by: List[str] = Field(
        default_factory=list,
        description="List of reviewer names; at least 2 required if review_status is 'verified'"
    )
    auto_update: Optional[AutoUpdateRecord] = Field(
        None,
        description="Required when review_status is 'auto_updated'"
    )
    machine_translated: Dict[str, bool] = Field(
        default_factory=lambda: {"hi": False, "bn": False},
        description="Machine translated flags per language"
    )
    tracked: List[TrackedRule] = Field(
        default_factory=list,
        description="Rules tracked by the automatic updater"
    )
    source_fingerprint: Optional[str] = Field(None, description="SHA256 hash of cleaned source text")
    last_checked: Optional[str] = Field(None, description="ISO timestamp of last crawler check")
    conflicting_schemes: List[str] = Field(default_factory=list, description="Scheme IDs that cannot be co-benefited")
    helpline: Optional[str] = Field(None, description="Toll-free helpline or helpdesk contact")

    @model_validator(mode="after")
    def validate_scheme_integrity(self) -> 'SchemeDefinition':
        if self.review_status == "verified":
            if len(self.verified_by) < 2:
                raise ValueError(
                    f"Scheme '{self.id}' with review_status 'verified' must have at least 2 names in verified_by, found: {self.verified_by}"
                )
        elif self.review_status == "auto_updated":
            if not self.auto_update:
                raise ValueError(
                    f"Scheme '{self.id}' with review_status 'auto_updated' requires an auto_update block"
                )
            if not self.auto_update.checkers_agreed:
                raise ValueError(
                    f"Scheme '{self.id}' auto_update must have checkers_agreed=True"
                )
        if self.level == "state":
            if not self.state or len(self.state) != 2:
                raise ValueError(
                    f"State-level scheme '{self.id}' must specify a 2-letter state code in 'state', got: '{self.state}'"
                )
        elif self.level == "central":
            if self.state is not None:
                raise ValueError(
                    f"Central scheme '{self.id}' must have state=null, got: '{self.state}'"
                )
        return self
