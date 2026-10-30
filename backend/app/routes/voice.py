from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.bhashini_service import bhashini_service

router = APIRouter()

class STTRequest(BaseModel):
    audio_base64: str
    language: str = "hi"

class TTSRequest(BaseModel):
    text: str
    language: str = "hi"

@router.post("/speech-to-text")
async def speech_to_text(req: STTRequest):
    """
    Transcribes citizen voice into text via Bhashini or provides browser fallback instructions.
    Voice audio is never stored on disk.
    """
    return await bhashini_service.speech_to_text(req.audio_base64, req.language)

@router.post("/text-to-speech")
async def text_to_speech(req: TTSRequest):
    """
    Synthesizes speech audio for read-aloud functionality via Bhashini or provides browser speech hints.
    """
    return await bhashini_service.text_to_speech(req.text, req.language)
