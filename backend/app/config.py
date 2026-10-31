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
    
    # Microsoft Azure AI Translator Configuration
    AZURE_TRANSLATOR_KEY: str = os.getenv("AZURE_TRANSLATOR_KEY", "")
    AZURE_TRANSLATOR_REGION: str = os.getenv("AZURE_TRANSLATOR_REGION", "")
    AZURE_TRANSLATOR_ENDPOINT: str = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
    
    # Administrative Security & Monitoring
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "yojnasarthi-admin-secret-2026")
    ENABLE_AUTOMATIC_MONITORING: bool = os.getenv("ENABLE_AUTOMATIC_MONITORING", "false").lower() == "true"
    MONITORING_INTERVAL_SECONDS: int = int(os.getenv("MONITORING_INTERVAL_SECONDS", "86400"))

    # Gemini AI API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # myScheme / API Setu Configuration
    MYSCHEME_API_ENABLED: bool = os.getenv("MYSCHEME_API_ENABLED", "false").lower() == "true"
    MYSCHEME_API_BASE_URL: str = os.getenv("MYSCHEME_API_BASE_URL", "https://apisetu.gov.in/api/v1/myscheme")
    MYSCHEME_API_KEY: str = os.getenv("MYSCHEME_API_KEY", "")
    MYSCHEME_API_CLIENT_ID: str = os.getenv("MYSCHEME_API_CLIENT_ID", "")
    MYSCHEME_API_CLIENT_SECRET: str = os.getenv("MYSCHEME_API_CLIENT_SECRET", "")
    MYSCHEME_API_AUTH_MODE: str = os.getenv("MYSCHEME_API_AUTH_MODE", "api_key")
    ENABLE_MYSCHEME_INTEGRATION: bool = os.getenv("ENABLE_MYSCHEME_INTEGRATION", "false").lower() == "true"
    
    # Bhashini Configuration (Legacy/Fallback)
    BHASHINI_API_ENABLED: bool = os.getenv("BHASHINI_API_ENABLED", "false").lower() == "true"
    BHASHINI_API_KEY: str = os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_INFERENCE_API_KEY: str = os.getenv("BHASHINI_INFERENCE_API_KEY", "") or os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_API_URL: str = os.getenv("BHASHINI_API_URL", "https://dhruva-api.bhashini.gov.in/services/inference/pipeline")
    BHASHINI_USER_ID: str = os.getenv("BHASHINI_USER_ID", "")
    BHASHINI_PIPELINE_ID: str = os.getenv("BHASHINI_PIPELINE_ID", "")
    BHASHINI_TRANSLATION_SERVICE_ID: str = os.getenv("BHASHINI_TRANSLATION_SERVICE_ID", "")
    BHASHINI_ASR_SERVICE_ID: str = os.getenv("BHASHINI_ASR_SERVICE_ID", "")
    BHASHINI_TTS_SERVICE_ID: str = os.getenv("BHASHINI_TTS_SERVICE_ID", "")
    ENABLE_BHASHINI_TRANSLATION: bool = os.getenv("ENABLE_BHASHINI_TRANSLATION", "false").lower() == "true"
    ENABLE_BHASHINI_ASR: bool = os.getenv("ENABLE_BHASHINI_ASR", "false").lower() == "true"
    ENABLE_BHASHINI_TTS: bool = os.getenv("ENABLE_BHASHINI_TTS", "false").lower() == "true"

    # Caching TTL
    TRANSLATION_CACHE_TTL_SECONDS: int = int(os.getenv("TRANSLATION_CACHE_TTL_SECONDS", "86400"))
    SCHEME_CACHE_TTL_SECONDS: int = int(os.getenv("SCHEME_CACHE_TTL_SECONDS", "3600"))
    
    # Schemes data directory
    SCHEMES_DIR: Path = Path(__file__).resolve().parent.parent / "data" / "schemes"
    
    # Verification tolerance (e.g., maximum scheme verification age in days)
    MAX_SCHEME_VERIFICATION_AGE_DAYS: int = 180

settings = Settings()
