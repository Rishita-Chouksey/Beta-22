from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
<<<<<<< HEAD
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

=======

from ..services.local_translator_service import local_translator, SUPPORTED_LANGUAGES

router = APIRouter()

MAX_BATCH = 200
MAX_TEXT_LEN = 5000


class TranslationRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LEN, description="Text to translate")
    sourceLanguage: Optional[str] = Field("auto", description="'en', 'hi', 'bn' or 'auto'")
    targetLanguage: Optional[str] = Field("hi", description="'en', 'hi' or 'bn'")
    source_language: Optional[str] = Field(None, description="Alias for sourceLanguage")
    target_language: Optional[str] = Field(None, description="Alias for targetLanguage")


>>>>>>> shreya/main
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

<<<<<<< HEAD
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
=======
>>>>>>> shreya/main

class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., max_length=MAX_BATCH)
    source_language: Optional[str] = "auto"
    target_language: str = "hi"


class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    target_language: str


def _to_response(res: dict) -> TranslationResponse:
    return TranslationResponse(
        translated_text=res["translated_text"], translatedText=res["translated_text"],
        source_language=res["source_language"], sourceLanguage=res["source_language"],
        target_language=res["target_language"], targetLanguage=res["target_language"],
        cached=res["cached"], service=res["service"], success=res["success"], error=res["error"],
    )


def _check_target(target: str) -> str:
    target = (target or "hi").strip().lower()
    if target not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{target}'. Supported languages: {list(SUPPORTED_LANGUAGES)}",
        )
    return target

<<<<<<< HEAD
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
=======
>>>>>>> shreya/main

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """Translate text with the local offline engine (no external API)."""
    source = (req.source_language or req.sourceLanguage or "auto").strip().lower()
    target = _check_target(req.target_language or req.targetLanguage or "hi")
    return _to_response(local_translator.translate(req.text, source, target))


@router.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(req: BatchTranslationRequest):
    """Translate many dynamic strings in one round trip (used by the UI for live data)."""
    target = _check_target(req.target_language)
    source = (req.source_language or "auto").strip().lower()
    safe = [t[:MAX_TEXT_LEN] for t in req.texts]
    results = local_translator.translate_batch(safe, source, target)
    return BatchTranslationResponse(translations=[_to_response(r) for r in results], target_language=target)

<<<<<<< HEAD
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
=======

@router.get("/translate/status")
async def get_translator_status():
    """Engine/model availability. No secrets exist because no external API is used."""
    return local_translator.get_status()
>>>>>>> shreya/main
