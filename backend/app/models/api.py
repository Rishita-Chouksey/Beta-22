from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from .profile import CitizenProfile
from .evaluation import OverallEvaluationResponse

class QuestionOption(BaseModel):
    label_en: str
    label_hi: str
    label_bn: Optional[str] = ""
    value: Any
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    description_bn: Optional[str] = None
    spoken: Optional[List[str]] = None

class NextQuestion(BaseModel):
    field: str
    title_en: str
    title_hi: str
    title_bn: Optional[str] = ""
    subtitle_en: Optional[str] = None
    subtitle_hi: Optional[str] = None
    subtitle_bn: Optional[str] = None
    explanation_en: Optional[str] = None
    explanation_hi: Optional[str] = None
    explanation_bn: Optional[str] = None
    examples_en: Optional[str] = None
    examples_hi: Optional[str] = None
    examples_bn: Optional[str] = None
    type: str = Field(..., description="'single_choice', 'number', 'boolean', 'range', 'searchable_picker'")
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
    resolved_message_bn: Optional[str] = None

class EvaluateRequest(BaseModel):
    profile: CitizenProfile

class ChecklistRequest(BaseModel):
    scheme_ids: List[str]

class ChecklistDocumentItem(BaseModel):
    document_id: str
    name_en: str
    name_hi: str
    name_bn: Optional[str] = ""
    schemes_required_for: List[str]
    purpose_en: str
    purpose_hi: str
    purpose_bn: Optional[str] = ""
    how_to_get_en: str
    how_to_get_hi: str
    how_to_get_bn: Optional[str] = ""
    online_url: Optional[str] = None
    offline_office: Optional[str] = None

class ChecklistResponse(BaseModel):
    documents: List[ChecklistDocumentItem]
    total_documents: int
    schemes_covered: List[str] = Field(default_factory=list)

class ParseTextRequest(BaseModel):
    text: str
    language: str = "hi"

class ParseTextResponse(BaseModel):
    extracted_profile: Dict[str, Any]
    detected_language: Optional[str] = "hi"
    summary_en: Optional[str] = ""
    summary_hi: Optional[str] = ""
    summary_bn: Optional[str] = ""
    recognized_intent: Optional[str] = None
    confidence_score: float = 1.0

class ChatMessageItem(BaseModel):
    role: str = "user"
    text: str

class ChatRequest(BaseModel):
    message: str
    language: str = "hi"
    current_scheme_id: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    history: Optional[List[ChatMessageItem]] = None
    active_profile: Optional[CitizenProfile] = None

class ChatResponse(BaseModel):
    reply: str
    referenced_schemes: List[str] = Field(default_factory=list)
    grounded_sources: List[str] = Field(default_factory=list)
    action_suggestion: Optional[str] = None
    disclaimer: Optional[str] = "Official verification required"

class FormHelpRequest(BaseModel):
    field_text: Optional[str] = None
    field_name: Optional[str] = None
    image_base64: Optional[str] = None
    language: str = "hi"
    scheme_context: Optional[str] = None

class FormFieldExplanation(BaseModel):
    field_name: str
    field_name_hi: Optional[str] = None
    field_name_mr: Optional[str] = None
    field_name_bn: Optional[str] = None
    explanation: str
    example: str

class FormHelpResponse(BaseModel):
    field_name: Optional[str] = None
    simplified_explanation: Optional[str] = None
    common_mistakes_to_avoid: Optional[str] = None
    where_to_find_value: Optional[str] = None
    example_value: Optional[str] = None
    explanations: List[FormFieldExplanation] = Field(default_factory=list)
    general_guidance: Optional[str] = ""
    disclaimer: Optional[str] = ""

class RulesStatusResponse(BaseModel):
    total_schemes: int
    verified_schemes: int
    stale_schemes: int
    unverified_schemes: int
    auto_updated_schemes: int = 0
    schemes_summary: List[Dict[str, Any]] = Field(default_factory=list)

class FeedbackRequest(BaseModel):
    scheme_id: Optional[str] = None
    rating: int = Field(5, ge=1, le=5)
    is_helpful: bool = True
    comment: Optional[str] = None
    feedback_text: Optional[str] = None
    screen: Optional[str] = None
    language: str = "hi"

class FeedbackResponse(BaseModel):
    success: bool
    status: Optional[str] = "success"
    message: str
