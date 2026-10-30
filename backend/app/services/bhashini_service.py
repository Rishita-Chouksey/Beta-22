import logging
import httpx
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger("bhashini_service")

class BhashiniService:
    def __init__(self):
        self.user_id = settings.BHASHINI_USER_ID
        self.api_key = settings.BHASHINI_API_KEY
        self.pipeline_id = settings.BHASHINI_PIPELINE_ID
        self.is_configured = bool(self.user_id and self.api_key and self.pipeline_id)

    async def speech_to_text(self, audio_base64: str, language: str = "hi") -> Dict[str, Any]:
        """
        Converts citizen spoken audio into text.
        Falls back gracefully with browser Web Speech API advice if Bhashini is unconfigured.
        Never permanently saves voice files.
        """
        if self.is_configured:
            try:
                # Real Bhashini ULCA / Pipeline invocation
                url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.api_key
                }
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "asr",
                            "config": {
                                "language": {"sourceLanguage": language}
                            }
                        }
                    ],
                    "inputData": {
                        "audio": [{"audioContent": audio_base64}]
                    }
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["pipelineResponse"][0]["output"][0]["source"]
                        return {
                            "text": text,
                            "language": language,
                            "service": "bhashini",
                            "success": True
                        }
            except Exception as e:
                logger.warning(f"Bhashini STT failed: {e}. Falling back.")

        # Graceful fallback response instructing frontend to use Web Speech Recognition
        return {
            "text": "",
            "language": language,
            "service": "browser_fallback",
            "message": "Bhashini service fallback active; browser native Web Speech API enabled for live audio recognition.",
            "success": False
        }

    async def text_to_speech(self, text: str, language: str = "hi") -> Dict[str, Any]:
        """
        Generates spoken audio from text for read-aloud feature.
        Provides browser speechSynthesis fallback compatibility.
        """
        if self.is_configured:
            try:
                url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.api_key
                }
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "tts",
                            "config": {
                                "language": {"sourceLanguage": language},
                                "gender": "female"
                            }
                        }
                    ],
                    "inputData": {
                        "input": [{"source": text}]
                    }
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        audio_content = data["pipelineResponse"][0]["audio"][0]["audioContent"]
                        return {
                            "audio_base64": audio_content,
                            "format": "wav",
                            "service": "bhashini",
                            "success": True
                        }
            except Exception as e:
                logger.warning(f"Bhashini TTS failed: {e}. Falling back.")

        return {
            "audio_base64": None,
            "format": "browser_speech_synthesis",
            "service": "browser_fallback",
            "text": text,
            "language": language,
            "success": False
        }

bhashini_service = BhashiniService()
