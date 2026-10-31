from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..services.sarvam_service import sarvam_service
from ..services.azure_translator_service import azure_translator_service, SUPPORTED_LANGUAGES

router = APIRouter()

class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text content to translate")
    sourceLanguage: Optional[str] = Field("en", description="Source ISO code: 'en', 'hi', or 'bn' (or 'auto')")
    targetLanguage: Optional[str] = Field("hi", description="Target ISO code: 'hi', 'en', or 'bn'")
    source_language: Optional[str] = Field(None, description="Alias for sourceLanguage")
    target_language: Optional[str] = Field(None, description="Alias for targetLanguage")

class TranslationResponse(BaseModel):
    translated_text: str
    translatedText: str
    source_language: str
    sourceLanguage: str
    target_language: str
    targetLanguage: str
    cached: bool
    service: str
    success: bool
    error: Optional[str] = None

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """
    Translates text between English ('en'), Hindi ('hi'), and Bengali ('bn').
    Priority:
    1. Sarvam AI (Indic Language Engine - Mayura v1)
    2. Microsoft Azure Cognitive Services Translator
    """
    source = (req.source_language or req.sourceLanguage or "auto").strip().lower()
    target = (req.target_language or req.targetLanguage or "hi").strip().lower()

    if target not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{target}'. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
        )

    # 1. Primary Engine: Sarvam AI (when configured)
    if sarvam_service.is_configured():
        result = await sarvam_service.translate(
            text=req.text,
            source_lang=source,
            target_lang=target
        )
        if result.get("success", False):
            t_text = result.get("translated_text", req.text)
            s_lang = result.get("source_language", source)
            t_lang = result.get("target_language", target)
            return TranslationResponse(
                translated_text=t_text,
                translatedText=t_text,
                source_language=s_lang,
                sourceLanguage=s_lang,
                target_language=t_lang,
                targetLanguage=t_lang,
                cached=result.get("cached", False),
                service=result.get("service", "sarvam_ai_translate"),
                success=True,
                error=None
            )

    # 2. Azure Cognitive Services Translator
    result = await azure_translator_service.translate(
        text=req.text,
        source_lang=source,
        target_lang=target
    )

    t_text = result.get("translated_text", req.text)
    s_lang = result.get("source_language", source)
    t_lang = result.get("target_language", target)

    return TranslationResponse(
        translated_text=t_text,
        translatedText=t_text,
        source_language=s_lang,
        sourceLanguage=s_lang,
        target_language=t_lang,
        targetLanguage=t_lang,
        cached=result.get("cached", False),
        service=result.get("service", "azure_ai_translator"),
        success=result.get("success", True),
        error=result.get("error")
    )

@router.get("/translate/status")
async def get_translator_status():
    """
    Returns current status and capabilities of the translation integrations.
    Preserves top-level keys for backward-compatibility while exposing Sarvam AI.
    Never exposes API keys or secrets in the response.
    """
    azure_stat = azure_translator_service.get_status()
    sarvam_stat = sarvam_service.get_status()

    # Base response preserves Azure keys for backward-compatibility
    status_response = dict(azure_stat)
    
    # Enrich with Sarvam AI and active primary service details
    status_response["sarvam_ai"] = sarvam_stat
    status_response["active_primary_service"] = "sarvam_ai" if sarvam_stat["configured"] else ("azure_ai" if azure_stat["configured"] else "unconfigured")
    
    return status_response
