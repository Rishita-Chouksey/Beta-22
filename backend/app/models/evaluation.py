from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class RuleEvaluationResult(BaseModel):
    field: str
    operator: str
    expected_value: Any
    actual_value: Any
    outcome: str = Field(..., description="'PASS', 'FAIL', 'UNKNOWN'")
    reason_en: str
    reason_hi: str
    is_external_unverifiable: bool = False

class SchemeEvaluationResult(BaseModel):
    scheme_id: str
    scheme_name_en: str
    scheme_name_hi: str
    level: str
    category: str
    benefit_en: str
    benefit_hi: str
    status: str = Field(..., description="'ELIGIBLE', 'NOT ELIGIBLE', 'NOT SURE', 'NO CURRENT RULES'")
    deciding_reason_en: str
    deciding_reason_hi: str
    rule_results: List[RuleEvaluationResult] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    last_verified_date: str
    is_stale: bool = False
    official_source_url: str
    conflicting_with: List[str] = Field(default_factory=list)

class OverallEvaluationResponse(BaseModel):
    eligible: List[SchemeEvaluationResult] = Field(default_factory=list)
    not_sure: List[SchemeEvaluationResult] = Field(default_factory=list)
    not_eligible: List[SchemeEvaluationResult] = Field(default_factory=list)
    no_rules: List[SchemeEvaluationResult] = Field(default_factory=list)
    total_evaluated: int = 0
    active_profile_summary: Dict[str, Any] = Field(default_factory=dict)
