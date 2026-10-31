from fastapi import APIRouter
from ..models.api import (
    ParseTextRequest, ParseTextResponse,
    ChatRequest, ChatResponse,
    FormHelpRequest, FormHelpResponse
)
from ..services.gemini_service import gemini_service

router = APIRouter()

@router.post("/parse-text", response_model=ParseTextResponse)
async def parse_free_text(req: ParseTextRequest):
    """
    Parses citizen natural language description into permitted profile fields.
    AI extracts attributes, which MUST be presented to citizen for confirmation.
    """
    res = gemini_service.parse_citizen_description(req.text, req.language)
    return ParseTextResponse(**res)

@router.post("/chat", response_model=ChatResponse)
async def chat_assistant(req: ChatRequest):
    """
    Interactive assistant grounded in verified scheme rules and application guidance.
    Admits frankly if information is unavailable.
    """
    history_data = [h.model_dump() for h in req.history] if req.history else None
    res = gemini_service.chat_grounded_response(
        message=req.message,
        current_scheme_id=req.current_scheme_id,
        profile=req.profile,
        language=req.language,
        history=history_data
    )
    return ChatResponse(**res)

@router.post("/form-help", response_model=FormHelpResponse)
async def form_assistance(req: FormHelpRequest):
    """
    Explains complex government application form terminology and uploaded form fields.
    Does not permanently store photos or PII.
    """
    res = gemini_service.explain_form(
        field_text=req.field_text,
        image_base64=req.image_base64,
        language=req.language
    )
    return FormHelpResponse(**res)
