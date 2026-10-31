import os
import re
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional
import httpx
from pydantic import BaseModel

from ..config import settings

# Civic and government scheme terms preserved during Indic translation
PROTECTED_TERMS = [
    ("Mukhyamantri Medhavi Vidyarthi Yojana", "मुख्यमंत्री मेधावी विद्यार्थी योजना"),
    ("MMVY", "एमएमवीवाई"),
    ("Mukhyamantri Ladli Behna Yojana", "मुख्यमंत्री लाड़ली बहना योजना"),
    ("Ladli Behna", "लाड़ली बहना"),
    ("PM-KISAN", "पीएम-किसान"),
    ("PM Kisan Samman Nidhi", "प्रधानमंत्री किसान सम्मान निधि"),
    ("Pradhan Mantri Awas Yojana - Gramin", "प्रधानमंत्री आवास योजना - ग्रामीण"),
    ("PMAY-G", "पीएमएवाई-जी"),
    ("Ayushman Bharat PM-JAY", "आयुष्मान भारत पीएम-जेएवाई"),
    ("PM-JAY", "पीएम-जेएवाई"),
    ("Sanjay Gandhi Niradhar Anudan Yojana", "संजय गांधी निराधार अनुदान योजना"),
    ("Indira Gandhi National Widow Pension Scheme", "इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना"),
    ("IGNWPS", "आईजीएनडब्ल्यूपीएस"),
    ("Direct Benefit Transfer", "प्रत्यक्ष लाभ अंतरण"),
    ("DBT", "डीबीटी"),
    ("Aadhaar", "आधार"),
    ("Samagra ID", "समग्र आईडी"),
    ("BPL", "बीपीएल"),
    ("NPCI", "एनपीसीआई"),
]

logger = logging.getLogger("sarvam_service")

# Mapping short ISO codes to Sarvam API locale codes
LANGUAGE_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "od": "od-IN",
}

# Reverse mapping
REVERSE_LANG_MAP = {v: k for k, v in LANGUAGE_MAP.items()}

class SarvamService:
    """
    Sarvam AI Indic Language Service.
    Official REST API client for Sarvam AI (https://dashboard.sarvam.ai):
    - Text Translation (Mayura v1 / Sarvam Translate)
    - Speech-to-Text (Saaras v1)
    - Text-to-Speech (Bulbul v1)
    
    Includes in-memory SHA-256 caching, protected civic terms glossary,
    and automatic graceful fallback.
    """

    def __init__(self):
        self.api_key = getattr(settings, "SARVAM_API_KEY", "").strip()
        self.translate_url = getattr(settings, "SARVAM_TRANSLATE_URL", "https://api.sarvam.ai/translate").strip()
        self.tts_url = getattr(settings, "SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech").strip()
        self.stt_url = getattr(settings, "SARVAM_STT_URL", "https://api.sarvam.ai/speech-to-text").strip()
        self.cache_ttl = getattr(settings, "TRANSLATION_CACHE_TTL_SECONDS", 86400)
        
        # In-memory deterministic translation cache: {hash_key: {"target": str, "timestamp": float}}
        self._cache: Dict[str, Dict[str, Any]] = {}

    def is_configured(self) -> bool:
        """Returns True if a valid Sarvam API key is configured."""
        return bool(self.api_key and self.api_key not in ["YOUR_SARVAM_API_KEY", "your_sarvam_api_key_here", ""])

    def get_status(self) -> Dict[str, Any]:
        """Returns the live status of the Sarvam AI integration without exposing the secret key."""
        configured = self.is_configured()
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if (configured and len(self.api_key) >= 8) else ("Configured" if configured else "Not Set")

        return {
            "name": "Sarvam AI (Indic Language Engine)",
            "configured": configured,
            "status": "active" if configured else "configured_awaiting_credentials",
            "is_live_api": configured,
            "model": "mayura:v1",
            "endpoint": self.translate_url,
            "key_status": masked_key if configured else "Missing SARVAM_API_KEY in backend/.env",
            "supported_languages": [
                {"code": "hi", "name": "Hindi (हिन्दी)", "locale": "hi-IN"},
                {"code": "en", "name": "English", "locale": "en-IN"},
                {"code": "bn", "name": "Bengali (বাংলা)", "locale": "bn-IN"},
                {"code": "mr", "name": "Marathi (मराठी)", "locale": "mr-IN"}
            ],
            "message": "Connected to Sarvam AI Mayura Translation Engine" if configured else "Awaiting approved Sarvam API key in backend/.env"
        }

    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        raw_key = f"sarvam:{source_lang}:{target_lang}:{text.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def _apply_glossary_masking(self, text: str, source_lang: str) -> tuple[str, dict]:
        """Prevents official civic and scheme terms from being mistranslated."""
        masked_text = text
        replacements = {}
        idx = 0

        for en_term, hi_term in PROTECTED_TERMS:
            # Check source term based on input language
            term = en_term if source_lang.startswith("en") else hi_term
            if term.lower() in masked_text.lower():
                token = f"__GOV_TERM_{idx}__"
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                masked_text = pattern.sub(token, masked_text)
                replacements[token] = term
                idx += 1

        return masked_text, replacements

    def _restore_glossary_tokens(self, text: str, replacements: dict) -> str:
        """Restores protected civic terms into the translated text."""
        restored = text
        for token, original_term in replacements.items():
            restored = restored.replace(token, original_term)
        return restored

    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> Dict[str, Any]:
        """
        Translates text using Sarvam AI Mayura REST API.
        Supports English ('en'), Hindi ('hi'), and Bengali ('bn').
        """
        clean_text = text.strip() if text else ""
        if not clean_text:
            return {
                "translated_text": "",
                "source_language": source_lang,
                "target_language": target_lang,
                "cached": False,
                "service": "sarvam_ai_translate",
                "success": True,
                "error": None
            }

        # Normalize language codes to short ISO
        s_short = source_lang.split("-")[0].lower()
        t_short = target_lang.split("-")[0].lower()

        # Map to Sarvam locale codes
        src_locale = LANGUAGE_MAP.get(s_short, "en-IN")
        tgt_locale = LANGUAGE_MAP.get(t_short, "hi-IN")

        # Identity translation
        if s_short == t_short:
            return {
                "translated_text": clean_text,
                "source_language": s_short,
                "target_language": t_short,
                "cached": False,
                "service": "sarvam_ai_translate",
                "success": True,
                "error": None
            }

        # Check in-memory cache
        cache_key = self._generate_cache_key(clean_text, s_short, t_short)
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return {
                    "translated_text": entry["target"],
                    "source_language": s_short,
                    "target_language": t_short,
                    "cached": True,
                    "service": "sarvam_cache",
                    "success": True,
                    "error": None
                }

        # If not configured, report gracefully
        if not self.is_configured():
            logger.info("Sarvam AI not configured; will fall back to secondary translation engines.")
            return {
                "translated_text": clean_text,
                "source_language": s_short,
                "target_language": t_short,
                "cached": False,
                "service": "sarvam_ai_translate",
                "success": False,
                "error": "Sarvam API key not configured. Set SARVAM_API_KEY in backend/.env"
            }

        # Mask protected civic terms
        masked_text, replacements = self._apply_glossary_masking(clean_text, s_short)

        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": self.api_key
        }

        payload = {
            "input": masked_text,
            "source_language_code": src_locale,
            "target_language_code": tgt_locale,
            "speaker_gender": "Male",
            "mode": "formal",
            "model": "mayura:v1",
            "enable_preprocessing": False
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(self.translate_url, json=payload, headers=headers)

                if resp.status_code == 200:
                    data = resp.json()
                    raw_translated = data.get("translated_text", "")
                    
                    # Restore protected civic terms
                    final_translated = self._restore_glossary_tokens(raw_translated, replacements) if replacements else raw_translated
                    
                    # Store in cache
                    self._cache[cache_key] = {
                        "target": final_translated,
                        "timestamp": time.time()
                    }

                    return {
                        "translated_text": final_translated,
                        "source_language": s_short,
                        "target_language": t_short,
                        "cached": False,
                        "service": "sarvam_ai_translate",
                        "success": True,
                        "error": None
                    }
                else:
                    err_msg = f"Sarvam AI API returned HTTP {resp.status_code}: {resp.text[:150]}"
                    logger.warning(err_msg)
                    return {
                        "translated_text": clean_text,
                        "source_language": s_short,
                        "target_language": t_short,
                        "cached": False,
                        "service": "sarvam_ai_translate",
                        "success": False,
                        "error": err_msg
                    }

        except httpx.TimeoutException:
            err_msg = "Sarvam AI request timed out after 8.0 seconds."
            logger.warning(err_msg)
            return {
                "translated_text": clean_text,
                "source_language": s_short,
                "target_language": t_short,
                "cached": False,
                "service": "sarvam_ai_translate",
                "success": False,
                "error": err_msg
            }
        except Exception as e:
            err_msg = f"Sarvam AI translation connection error: {str(e)[:150]}"
            logger.error(err_msg)
            return {
                "translated_text": clean_text,
                "source_language": s_short,
                "target_language": t_short,
                "cached": False,
                "service": "sarvam_ai_translate",
                "success": False,
                "error": err_msg
            }

sarvam_service = SarvamService()
