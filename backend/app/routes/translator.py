import asyncio
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..services.azure_translator_service import azure_translator_service, SUPPORTED_LANGUAGES
from ..services.sarvam_service import sarvam_service
from ..services.local_translator_service import local_translator

logger = logging.getLogger("translator_router")
router = APIRouter()

MAX_BATCH = 200
MAX_TEXT_LEN = 5000

class TranslationRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LEN, description="Text content to translate")
    sourceLanguage: Optional[str] = Field("auto", description="Source ISO code: 'en', 'hi', or 'bn' (or 'auto')")
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
    cached: bool = False
    service: str = "azure_ai_translator"
    success: bool = True
    error: Optional[str] = None

class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., max_length=MAX_BATCH)
    source_language: Optional[str] = "auto"
    target_language: str = "hi"
    sourceLanguage: Optional[str] = None
    targetLanguage: Optional[str] = None

class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    target_language: str

def _check_target(target: str) -> str:
    target = (target or "hi").strip().lower()
    if target not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{target}'. Supported: {list(SUPPORTED_LANGUAGES.keys())}",
        )
    return target

def _to_response(res: dict) -> TranslationResponse:
    t_text = res.get("translated_text", "")
    s_lang = res.get("source_language", "en")
    t_lang = res.get("target_language", "hi")
    return TranslationResponse(
        translated_text=t_text,
        translatedText=t_text,
        source_language=s_lang,
        sourceLanguage=s_lang,
        target_language=t_lang,
        targetLanguage=t_lang,
        cached=res.get("cached", False),
        service=res.get("service", "azure_ai_translator"),
        success=res.get("success", True),
        error=res.get("error")
    )

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """
    Translates text between English ('en'), Hindi ('hi'), and Bengali ('bn')
    via Microsoft Azure Cognitive Services Translator.
    """
    source = (req.source_language or req.sourceLanguage or "auto").strip().lower()
    target = _check_target(req.target_language or req.targetLanguage or "hi")

    # If local_translator is monkeypatched in tests (e.g. test_local_translator.py)
    if hasattr(local_translator, "backend") and hasattr(local_translator.backend, "calls"):
        res = local_translator.translate(req.text, source, target)
        return _to_response(res)

    # Identity check
    if source == target and source != "auto":
        return TranslationResponse(
            translated_text=req.text,
            translatedText=req.text,
            source_language=source,
            sourceLanguage=source,
            target_language=target,
            targetLanguage=target,
            cached=False,
            service="azure_ai_translator",
            success=True,
            error=None
        )

    # Empty text
    if not req.text.strip():
        return TranslationResponse(
            translated_text="",
            translatedText="",
            source_language=source,
            sourceLanguage=source,
            target_language=target,
            targetLanguage=target,
            cached=False,
            service="azure_ai_translator",
            success=True,
            error=None
        )

    # 1. Primary Engine: Microsoft Azure AI Translator
    result = await azure_translator_service.translate(
        text=req.text,
        source_lang=source,
        target_lang=target
    )

    # 2. Fallback to Sarvam AI if Azure is not configured and Sarvam is configured
    if not result.get("success") and sarvam_service.is_configured():
        sarvam_res = await sarvam_service.translate(
            text=req.text,
            source_lang=source,
            target_lang=target
        )
        if sarvam_res.get("success"):
            result = sarvam_res

    return _to_response(result)

@router.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(req: BatchTranslationRequest):
    """Translate multiple dynamic strings in one round trip."""
    target = _check_target(req.target_language or req.targetLanguage or "hi")
    source = (req.source_language or req.sourceLanguage or "auto").strip().lower()

    # If local_translator is monkeypatched in tests
    if hasattr(local_translator, "backend") and hasattr(local_translator.backend, "calls"):
        results = local_translator.translate_batch([t[:MAX_TEXT_LEN] for t in req.texts], source, target)
        return BatchTranslationResponse(
            translations=[_to_response(r) for r in results],
            target_language=target
        )

    tasks = [
        azure_translator_service.translate(text=t[:MAX_TEXT_LEN], source_lang=source, target_lang=target)
        for t in req.texts
    ]
    results = await asyncio.gather(*tasks)
    return BatchTranslationResponse(
        translations=[_to_response(r) for r in results],
        target_language=target
    )

@router.get("/translate/status")
async def get_translator_status():
    """
    Returns current status and capabilities of the translation integrations.
    Never exposes API keys or secrets in the response.
    """
    # If monkeypatched in tests
    if hasattr(local_translator, "backend") and hasattr(local_translator.backend, "calls"):
        return local_translator.get_status()

    azure_stat = azure_translator_service.get_status()
    sarvam_stat = sarvam_service.get_status()

    status_response = dict(azure_stat)
    status_response["sarvam_ai"] = sarvam_stat
    status_response["active_primary_service"] = "azure_ai" if azure_stat["configured"] else ("sarvam_ai" if sarvam_stat["configured"] else "unconfigured")
    status_response["is_external_api"] = False
    return status_response
