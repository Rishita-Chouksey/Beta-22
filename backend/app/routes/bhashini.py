from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..services.bhashini_adapter import bhashini_adapter
from ..services.azure_translator_service import azure_translator_service
from ..services.sarvam_service import sarvam_service

router = APIRouter()

class TranslationRequest(BaseModel):
    text: str
    sourceLanguage: str = Field("en", description="Source ISO code: 'en', 'hi', etc.")
    targetLanguage: str = Field("hi", description="Target ISO code: 'hi', 'en', etc.")

class TranslationResponse(BaseModel):
    translatedText: str
    sourceLanguage: str
    targetLanguage: str
    cached: bool
    service: str
    note: Optional[str] = None

class ASRRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio stream/file")
    language: str = Field("hi", description="Spoken language: 'hi', 'en', etc.")

class ASRResponse(BaseModel):
    text: str
    language: str
    service: str
    confidence: Optional[float] = None
    success: bool
    message: Optional[str] = None

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize into audio")
    language: str = Field("hi", description="Language of text: 'hi', 'en', etc.")

class TTSResponse(BaseModel):
    audio_base64: Optional[str] = None
    format: str = "wav"
    service: str
    text: Optional[str] = None
    language: str
    success: bool

@router.post("/bhashini/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """
    Translates text between supported Indic and English languages.
    Priority: Sarvam AI -> Microsoft Azure -> Bhashini ULCA -> Local Glossary
    """
    if sarvam_service.is_configured():
        res = await sarvam_service.translate(
            text=req.text,
            source_lang=req.sourceLanguage,
            target_lang=req.targetLanguage
        )
        if res.get("success", False):
            return TranslationResponse(
                translatedText=res.get("translated_text", req.text),
                sourceLanguage=res.get("source_language", req.sourceLanguage),
                targetLanguage=res.get("target_language", req.targetLanguage),
                cached=res.get("cached", False),
                service=res.get("service", "sarvam_ai_translate"),
                note="Routed via Sarvam AI Mayura Translation Engine"
            )

    if azure_translator_service.is_configured():
        res = await azure_translator_service.translate(
            text=req.text,
            source_lang=req.sourceLanguage,
            target_lang=req.targetLanguage
        )
        if res.get("success", False):
            return TranslationResponse(
                translatedText=res.get("translated_text", req.text),
                sourceLanguage=res.get("source_language", req.sourceLanguage),
                targetLanguage=res.get("target_language", req.targetLanguage),
                cached=res.get("cached", False),
                service=res.get("service", "azure_ai_translator"),
                note="Routed via Microsoft Azure AI Translator"
            )

    res = await bhashini_adapter.translate(
        text=req.text,
        source_lang=req.sourceLanguage,
        target_lang=req.targetLanguage
    )
    return TranslationResponse(
        translatedText=res.get("translated_text", req.text),
        sourceLanguage=req.sourceLanguage,
        targetLanguage=req.targetLanguage,
        cached=res.get("cached", False),
        service=res.get("service", "unknown"),
        note=res.get("note")
    )

@router.post("/bhashini/speech-to-text", response_model=ASRResponse)
async def speech_to_text(req: ASRRequest):
    """
    Transcribes audio into text via Bhashini ASR.
    Does not auto-submit forms after transcription.
    Never stores audio recordings permanently.
    """
    res = await bhashini_adapter.speech_to_text(req.audio_base64, req.language)
    return ASRResponse(
        text=res.get("text", ""),
        language=res.get("language", req.language),
        service=res.get("service", "browser_fallback"),
        confidence=res.get("confidence"),
        success=res.get("success", False),
        message=res.get("message")
    )

@router.post("/bhashini/text-to-speech", response_model=TTSResponse)
async def text_to_speech(req: TTSRequest):
    """
    Converts text to speech audio via Bhashini TTS.
    Returns base64 audio or browser speech synthesis instructions.
    """
    res = await bhashini_adapter.text_to_speech(req.text, req.language)
    return TTSResponse(
        audio_base64=res.get("audio_base64"),
        format=res.get("format", "wav"),
        service=res.get("service", "browser_fallback"),
        text=res.get("text", req.text),
        language=req.language,
        success=res.get("success", False)
    )

@router.get("/bhashini/status")
async def get_bhashini_status():
    """Returns current status of Bhashini integration and available capabilities."""
    return bhashini_adapter.get_status()
