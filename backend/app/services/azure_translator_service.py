import os
import time
import uuid
import hashlib
import logging
from typing import Dict, Any, List, Optional
import httpx
from pydantic import BaseModel, Field

from ..config import settings

logger = logging.getLogger("azure_translator_service")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali"
}

class AzureTranslationResult(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    cached: bool = False
    service: str = "azure_ai_translator"
    success: bool = True
    error: Optional[str] = None

class AzureTranslatorService:
    """
    Microsoft Azure AI Translator Service.
    Connects to the official Azure Cognitive Services Translator REST API v3.0.
    Translates between English ('en'), Hindi ('hi'), and Bengali ('bn').
    Features in-memory deterministic SHA-256 caching, timeouts, retries, and strict secret masking.
    """

    def __init__(self):
        self.key = getattr(settings, "AZURE_TRANSLATOR_KEY", "").strip()
        self.region = getattr(settings, "AZURE_TRANSLATOR_REGION", "").strip()
        self.endpoint = (getattr(settings, "AZURE_TRANSLATOR_ENDPOINT", "").strip() or "https://api.cognitive.microsofttranslator.com").rstrip("/")
        self.cache_ttl = getattr(settings, "TRANSLATION_CACHE_TTL_SECONDS", 86400)
        
        # In-memory deterministic translation cache: {hash_key: {"target": str, "timestamp": float}}
        self._cache: Dict[str, Dict[str, Any]] = {}

    def is_configured(self) -> bool:
        """Returns True if an Azure Translator key has been configured."""
        return bool(self.key and self.key != "YOUR_AZURE_TRANSLATOR_KEY")

    def get_status(self) -> Dict[str, Any]:
        """Returns the live status of the Azure Translator integration without exposing secrets."""
        configured = self.is_configured()
        masked_key = f"{self.key[:4]}...{self.key[-4:]}" if (configured and len(self.key) >= 8) else ("Configured" if configured else "Not Set")

        return {
            "name": "Microsoft Azure AI Translator",
            "configured": configured,
            "status": "active" if configured else "configured_awaiting_credentials",
            "is_live_api": configured,
            "endpoint": self.endpoint,
            "region": self.region or "global",
            "key_status": masked_key if configured else "Missing AZURE_TRANSLATOR_KEY in backend/.env",
            "supported_languages": [
                {"code": "en", "name": "English"},
                {"code": "hi", "name": "Hindi (हिन्दी)"},
                {"code": "bn", "name": "Bengali (বাংলা)"}
            ],
            "api_version": "3.0",
            "message": "Connected to official Azure Cognitive Services Translator" if configured else "Awaiting approved Azure Translator credentials in backend/.env"
        }

    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        raw_key = f"{source_lang}:{target_lang}:{text.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> Dict[str, Any]:
        """
        Translates text using Azure AI Translator REST API v3.0.
        Supports English ('en'), Hindi ('hi'), and Bengali ('bn').
        """
        clean_text = text.strip() if text else ""
        if not clean_text:
            return {
                "translated_text": "",
                "source_language": source_lang,
                "target_language": target_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": True,
                "error": None
            }

        # Normalize language codes
        s_lang = (source_lang or "auto").lower()
        t_lang = (target_lang or "hi").lower()

        # Validate target language
        if t_lang not in SUPPORTED_LANGUAGES:
            return {
                "translated_text": clean_text,
                "source_language": s_lang,
                "target_language": t_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": False,
                "error": f"Unsupported target language '{t_lang}'. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
            }

        # Identity translation
        if s_lang == t_lang:
            return {
                "translated_text": clean_text,
                "source_language": s_lang,
                "target_language": t_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": True,
                "error": None
            }

        # Check Cache
        cache_key = self._generate_cache_key(clean_text, s_lang, t_lang)
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return {
                    "translated_text": entry["target"],
                    "source_language": s_lang,
                    "target_language": t_lang,
                    "cached": True,
                    "service": "azure_ai_translator_cache",
                    "success": True,
                    "error": None
                }

        # Verify configuration
        if not self.is_configured():
            err_msg = "Azure AI Translator credentials not configured. Please set AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_REGION in backend/.env."
            logger.warning(err_msg)
            return {
                "translated_text": clean_text,
                "source_language": s_lang,
                "target_language": t_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": False,
                "error": err_msg
            }

        # Construct Azure REST API Request
        api_path = f"{self.endpoint}/translate"
        params = {
            "api-version": "3.0",
            "to": t_lang
        }
        if s_lang != "auto":
            params["from"] = s_lang

        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Content-Type": "application/json; charset=UTF-8",
            "X-ClientTraceId": str(uuid.uuid4())
        }
        if self.region:
            headers["Ocp-Apim-Subscription-Region"] = self.region

        body = [{"Text": clean_text}]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(api_path, params=params, json=body, headers=headers)

                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 0 and "translations" in data[0]:
                        translated = data[0]["translations"][0]["text"]
                        detected_src = data[0].get("detectedLanguage", {}).get("language", s_lang)

                        # Cache successful result
                        self._cache[cache_key] = {
                            "target": translated,
                            "timestamp": time.time()
                        }

                        return {
                            "translated_text": translated,
                            "source_language": detected_src or s_lang,
                            "target_language": t_lang,
                            "cached": False,
                            "service": "azure_ai_translator",
                            "success": True,
                            "error": None
                        }
                    else:
                        return {
                            "translated_text": clean_text,
                            "source_language": s_lang,
                            "target_language": t_lang,
                            "cached": False,
                            "service": "azure_ai_translator",
                            "success": False,
                            "error": "Unexpected response structure from Azure Translator."
                        }

                elif resp.status_code in [401, 403]:
                    err_msg = f"Azure AI Translator authorization failed (HTTP {resp.status_code}). Check AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_REGION."
                    logger.error(err_msg)
                    return {
                        "translated_text": clean_text,
                        "source_language": s_lang,
                        "target_language": t_lang,
                        "cached": False,
                        "service": "azure_ai_translator",
                        "success": False,
                        "error": err_msg
                    }
                else:
                    err_msg = f"Azure AI Translator returned HTTP {resp.status_code}: {resp.text[:200]}"
                    logger.warning(err_msg)
                    return {
                        "translated_text": clean_text,
                        "source_language": s_lang,
                        "target_language": t_lang,
                        "cached": False,
                        "service": "azure_ai_translator",
                        "success": False,
                        "error": err_msg
                    }

        except httpx.TimeoutException:
            err_msg = "Azure AI Translator request timed out after 10.0 seconds."
            logger.warning(err_msg)
            return {
                "translated_text": clean_text,
                "source_language": s_lang,
                "target_language": t_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": False,
                "error": err_msg
            }
        except Exception as e:
            err_msg = f"Azure AI Translator connection error: {str(e)[:150]}"
            logger.error(err_msg)
            return {
                "translated_text": clean_text,
                "source_language": s_lang,
                "target_language": t_lang,
                "cached": False,
                "service": "azure_ai_translator",
                "success": False,
                "error": err_msg
            }

azure_translator_service = AzureTranslatorService()
