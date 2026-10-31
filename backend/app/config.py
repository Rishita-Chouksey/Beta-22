import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present (check backend/.env then root .env)
env_path = Path(__file__).resolve().parent.parent / ".env"
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "YojnaSarthi Backend"
    VERSION: str = "2.1.0"
    API_PREFIX: str = "/api"
    
<<<<<<< HEAD
    # Sarvam AI Indic Language Integration Configuration
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    ENABLE_SARVAM_TRANSLATION: bool = os.getenv("ENABLE_SARVAM_TRANSLATION", "true").lower() == "true"
    SARVAM_TRANSLATE_URL: str = os.getenv("SARVAM_TRANSLATE_URL", "https://api.sarvam.ai/translate")
    SARVAM_TTS_URL: str = os.getenv("SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")
    SARVAM_STT_URL: str = os.getenv("SARVAM_STT_URL", "https://api.sarvam.ai/speech-to-text")

    # Microsoft Azure AI Translator Configuration
    AZURE_TRANSLATOR_KEY: str = os.getenv("AZURE_TRANSLATOR_KEY", "")
    AZURE_TRANSLATOR_REGION: str = os.getenv("AZURE_TRANSLATOR_REGION", "")
    AZURE_TRANSLATOR_ENDPOINT: str = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
=======
    # Translation is fully offline (Argos Translate) - no API keys required.
    TRANSLATION_ENABLED: bool = os.getenv("TRANSLATION_ENABLED", "true").lower() == "true"

>>>>>>> shreya/main
    
    # Administrative Security & Monitoring
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "yojnasarthi-admin-secret-2026")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "")
    ADMIN_PASSWORD_HASH: str = os.getenv("ADMIN_PASSWORD_HASH", "")
    ADMIN_SESSION_SECRET: str = os.getenv("ADMIN_SESSION_SECRET", "")
    ADMIN_SESSION_TTL_SECONDS: int = int(os.getenv("ADMIN_SESSION_TTL_SECONDS", "1800"))
    ADMIN_COOKIE_SECURE: bool = os.getenv("ADMIN_COOKIE_SECURE", "false").lower() == "true"
    ADMIN_COOKIE_SAMESITE: str = os.getenv("ADMIN_COOKIE_SAMESITE", "strict").lower()
    ENABLE_MONITORING_DEMO_DATA: bool = os.getenv("ENABLE_MONITORING_DEMO_DATA", "true").lower() == "true"
    ENABLE_AUTOMATIC_MONITORING: bool = os.getenv("ENABLE_AUTOMATIC_MONITORING", "false").lower() == "true"
    MONITORING_INTERVAL_SECONDS: int = int(os.getenv("MONITORING_INTERVAL_SECONDS", "86400"))

    # Gemini AI API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    
    # myScheme / API Setu Configuration
    MYSCHEME_API_ENABLED: bool = os.getenv("MYSCHEME_API_ENABLED", "false").lower() == "true"
    MYSCHEME_API_BASE_URL: str = os.getenv("MYSCHEME_API_BASE_URL", "https://apisetu.gov.in/api/v1/myscheme")
    MYSCHEME_API_KEY: str = os.getenv("MYSCHEME_API_KEY", "")
    MYSCHEME_API_CLIENT_ID: str = os.getenv("MYSCHEME_API_CLIENT_ID", "")
    MYSCHEME_API_CLIENT_SECRET: str = os.getenv("MYSCHEME_API_CLIENT_SECRET", "")
    MYSCHEME_API_AUTH_MODE: str = os.getenv("MYSCHEME_API_AUTH_MODE", "api_key")
    ENABLE_MYSCHEME_INTEGRATION: bool = os.getenv("ENABLE_MYSCHEME_INTEGRATION", "false").lower() == "true"
    
    # Caching TTL
    SCHEME_CACHE_TTL_SECONDS: int = int(os.getenv("SCHEME_CACHE_TTL_SECONDS", "3600"))
    
    # Schemes data directory
    SCHEMES_DIR: Path = Path(__file__).resolve().parent.parent / "data" / "schemes"
    
    # Verification tolerance (e.g., maximum scheme verification age in days)
    MAX_SCHEME_VERIFICATION_AGE_DAYS: int = 180

settings = Settings()
