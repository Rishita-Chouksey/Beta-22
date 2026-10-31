from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    HTML = "HTML"
    PDF = "PDF"
    DATASET = "DATASET"
    PORTAL = "PORTAL"
    API = "API"

class SourceStatus(str, Enum):
    DISCOVERED = "discovered"
    CRAWLED = "crawled"
    FAILED = "failed"
    DEGRADED = "degraded"

class ChangeDetectionStatus(str, Enum):
    NEW_SOURCE = "NEW_SOURCE"
    CONTENT_CHANGED = "CONTENT_CHANGED"
    NO_CHANGE = "NO_CHANGE"
    SOURCE_REMOVED = "SOURCE_REMOVED"
    FETCH_FAILED = "FETCH_FAILED"

class ChangeType(str, Enum):
    NEW_SCHEME = "NEW_SCHEME"
    ELIGIBILITY_CHANGE = "ELIGIBILITY_CHANGE"
    BENEFIT_CHANGE = "BENEFIT_CHANGE"
    DOCUMENT_CHANGE = "DOCUMENT_CHANGE"
    DEADLINE_CHANGE = "DEADLINE_CHANGE"
    APPLICATION_PROCESS_CHANGE = "APPLICATION_PROCESS_CHANGE"
    GUIDELINE_UPDATE = "GUIDELINE_UPDATE"
    MINOR_CONTENT_CHANGE = "MINOR_CONTENT_CHANGE"
    UNRELATED_CHANGE = "UNRELATED_CHANGE"
    UNCERTAIN_CHANGE = "UNCERTAIN_CHANGE"

class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SourceItem(BaseModel):
    id: str
    url: str
    domain: str
    source_type: SourceType = SourceType.HTML
    discovered_from: Optional[str] = None
    status: SourceStatus = SourceStatus.DISCOVERED
    last_checked_at: Optional[str] = None
    last_successful_fetch_at: Optional[str] = None
    created_at: Optional[str] = None

class SourceSnapshot(BaseModel):
    id: str
    source_id: str
    content_hash: str
    extracted_content: str
    retrieved_at: Optional[str] = None
    document_type: str = "HTML"
    previous_snapshot_id: Optional[str] = None

class DiscoveredScheme(BaseModel):
    id: str
    scheme_name: str
    department: Optional[str] = None
    state: Optional[str] = None
    source_id: str
    source_url: str
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "unverified"
    first_discovered_at: Optional[str] = None
    last_updated_at: Optional[str] = None

class ProposedUpdate(BaseModel):
    id: str
    scheme_id: str
    change_type: ChangeType
    old_value: Optional[str] = None
    proposed_value: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    source_url: str
    confidence: float = 0.85
    review_status: ReviewStatus = ReviewStatus.PENDING
    created_at: Optional[str] = None
    reviewed_at: Optional[str] = None

class SchemeVersion(BaseModel):
    id: Optional[int] = None
    scheme_id: str
    version_number: int
    scheme_data: Dict[str, Any]
    source_url: Optional[str] = None
    approval_status: str = "APPROVED"
    created_at: Optional[str] = None

class AgentRunRecord(BaseModel):
    id: str
    agent_name: str
    status: AgentStatus = AgentStatus.IDLE
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class ExtractedSchemeData(BaseModel):
    scheme_name: str
    department: Optional[str] = None
    classification: str = "central"  # central or state
    state: Optional[str] = None
    description: Optional[str] = None
    intended_beneficiaries: Optional[str] = None
    eligibility_conditions: Dict[str, Any] = Field(default_factory=dict)
    age_criteria: Optional[str] = None
    income_criteria: Optional[str] = None
    gender_category_criteria: Optional[str] = None
    benefits: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    application_process: List[str] = Field(default_factory=list)
    deadline: Optional[str] = None
    official_application_url: Optional[str] = None
    official_guideline_url: Optional[str] = None
    source_publication_date: Optional[str] = None
    extraction_timestamp: str
    evidence_excerpts: Dict[str, str] = Field(default_factory=dict)
    confidence: float = 0.85
