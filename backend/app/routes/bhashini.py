from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..services.bhashini_adapter import bhashini_adapter

router = APIRouter()

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
    """Returns current status of Bhashini voice assistance capabilities (ASR & TTS)."""
    return bhashini_adapter.get_status()
