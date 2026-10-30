from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from .profile import CitizenProfile
from .evaluation import OverallEvaluationResponse

class QuestionOption(BaseModel):
    label_en: str
    label_hi: str
    value: Any

class NextQuestion(BaseModel):
    field: str
    title_en: str
    title_hi: str
    subtitle_en: Optional[str] = None
    subtitle_hi: Optional[str] = None
    type: str = Field(..., description="'single_choice', 'number', 'boolean', 'range'")
    options: Optional[List[QuestionOption]] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    unit: Optional[str] = None
    progress_index: int = 1
    total_estimated: int = 8

class NextQuestionRequest(BaseModel):
    profile: CitizenProfile

class NextQuestionResponse(BaseModel):
    has_more: bool
    question: Optional[NextQuestion] = None
    resolved_message_en: Optional[str] = None
    resolved_message_hi: Optional[str] = None

class EvaluateRequest(BaseModel):
    profile: CitizenProfile

class ChecklistRequest(BaseModel):
    scheme_ids: List[str]

class ChecklistDocumentItem(BaseModel):
    document_id: str
    name_en: str
    name_hi: str
    schemes_required_for: List[str]
    purpose_en: str
    purpose_hi: str
    how_to_get_en: str
    how_to_get_hi: str
    online_url: Optional[str] = None
    offline_office: Optional[str] = None

class ChecklistResponse(BaseModel):
    documents: List[ChecklistDocumentItem]
    total_documents: int
    schemes_covered: List[str]

class ParseTextRequest(BaseModel):
    text: str
    language: str = "hi"

class ParseTextResponse(BaseModel):
    extracted_profile: Dict[str, Any]
    detected_language: str
    summary_en: str
    summary_hi: str

class ChatRequest(BaseModel):
    message: str
    language: str = "hi"
    current_scheme_id: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    reply: str
    grounded_sources: List[str] = Field(default_factory=list)
    disclaimer: str

class FormHelpRequest(BaseModel):
    field_text: Optional[str] = None
    image_base64: Optional[str] = None
    language: str = "hi"

class FormFieldExplanation(BaseModel):
    field_name: str
    field_name_hi: Optional[str] = None
    explanation: str
    example: str

class FormHelpResponse(BaseModel):
    explanations: List[FormFieldExplanation]
    general_guidance: str
    disclaimer: str

class RulesStatusResponse(BaseModel):
    total_schemes: int
    verified_schemes: int
    stale_schemes: int
    unverified_schemes: int
    schemes_summary: List[Dict[str, Any]]
