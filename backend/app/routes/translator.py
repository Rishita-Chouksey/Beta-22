from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..services.azure_translator_service import azure_translator_service, SUPPORTED_LANGUAGES

router = APIRouter()

class AzureTranslationRequest(BaseModel):
    text: str = Field(..., description="Text content to translate")
    sourceLanguage: Optional[str] = Field("en", description="Source ISO code: 'en', 'hi', or 'bn' (or 'auto')")
    targetLanguage: Optional[str] = Field("hi", description="Target ISO code: 'hi', 'en', or 'bn'")
    source_language: Optional[str] = Field(None, description="Alias for sourceLanguage")
    target_language: Optional[str] = Field(None, description="Alias for targetLanguage")

class AzureTranslationResponse(BaseModel):
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

@router.post("/translate", response_model=AzureTranslationResponse)
async def translate_text(req: AzureTranslationRequest):
    """
    Translates text between English ('en'), Hindi ('hi'), and Bengali ('bn')
    using official Microsoft Azure Cognitive Services Translator REST API v3.0.
    """
    source = (req.source_language or req.sourceLanguage or "auto").strip().lower()
    target = (req.target_language or req.targetLanguage or "hi").strip().lower()

    if target not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{target}'. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
        )

    result = await azure_translator_service.translate(
        text=req.text,
        source_lang=source,
        target_lang=target
    )

    t_text = result.get("translated_text", req.text)
    s_lang = result.get("source_language", source)
    t_lang = result.get("target_language", target)

    return AzureTranslationResponse(
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
    Returns current status and capabilities of the Microsoft Azure AI Translator integration.
    Never exposes API keys or secrets in the response.
    """
    return azure_translator_service.get_status()
