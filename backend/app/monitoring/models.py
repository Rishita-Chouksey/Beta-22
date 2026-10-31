from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceCategory(str, Enum):
    CENTRAL = "central"
    MADHYA_PRADESH = "madhya_pradesh"
    OTHER = "other"

class SourceType(str, Enum):
    HTML = "HTML"
    PDF = "PDF"
    RSS = "RSS"
    API = "API"
    JSON = "JSON"
    CSV = "CSV"

class MonitoringFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

class AccessibilityStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"

class SchemeReviewStatus(str, Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    UPDATE_DETECTED = "UPDATE_DETECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    OUTDATED = "OUTDATED"
    INACTIVE = "INACTIVE"

class ChangeType(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    CONTENT_MODIFIED = "CONTENT_MODIFIED"
    NEW_NOTIFICATION = "NEW_NOTIFICATION"
    NEW_PDF_PUBLISHED = "NEW_PDF_PUBLISHED"
    PDF_REPLACED = "PDF_REPLACED"
    APPLICATION_LINK_CHANGED = "APPLICATION_LINK_CHANGED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    MONITORING_FAILED = "MONITORING_FAILED"

class SourceDefinition(BaseModel):
    source_id: str
    name: str
    category: SourceCategory
    official_url: str
    source_type: SourceType = SourceType.HTML
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.DAILY
    target_scheme_ids: List[str] = Field(default_factory=list)
    automated_monitoring_permitted: bool = True
    last_successful_check: Optional[str] = None
    last_detected_change: Optional[str] = None
    accessibility_status: AccessibilityStatus = AccessibilityStatus.PENDING
    error_details: Optional[str] = None
    content_hash: Optional[str] = None

class PendingUpdate(BaseModel):
    update_id: str
    scheme_id: str
    scheme_name_en: str
    scheme_name_hi: str
    source_id: str
    source_url: str
    detected_at: str
    change_type: ChangeType
    old_version_id: Optional[int] = None
    old_content_snippet: Optional[str] = None
    new_content_snippet: Optional[str] = None
    proposed_changes: Dict[str, Any] = Field(default_factory=dict)
    ai_analysis_summary: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    decision_reason: Optional[str] = None
    decision_by: Optional[str] = None
    decision_at: Optional[str] = None
    is_demo: bool = False

class SchemeVersionRecord(BaseModel):
    version_id: int
    scheme_id: str
    version_number: int
    review_status: str
    scheme_data: Dict[str, Any]
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    change_summary: Optional[str] = None
    created_at: str

class MonitoringSummary(BaseModel):
    total_schemes_monitored: int
    total_sources_monitored: int
    changes_detected_count: int
    updates_awaiting_review: int
    verified_schemes_count: int
    outdated_or_unavailable_sources: int
    last_monitoring_run: Optional[str] = None
    next_scheduled_run: Optional[str] = None
    is_scheduler_running: bool = False

