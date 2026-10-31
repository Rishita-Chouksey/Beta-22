from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

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


@router.get("/translate/status")
async def get_translator_status():
    """Engine/model availability. No secrets exist because no external API is used."""
    return local_translator.get_status()
