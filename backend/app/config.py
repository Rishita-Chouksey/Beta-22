import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseModel):
    PROJECT_NAME: str = "YojnaSarthi Backend"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    
    # AI Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # myScheme / API Setu Configuration
    MYSCHEME_API_ENABLED: bool = os.getenv("MYSCHEME_API_ENABLED", "false").lower() == "true"
    MYSCHEME_API_BASE_URL: str = os.getenv("MYSCHEME_API_BASE_URL", "https://apisetu.gov.in/api/v1/myscheme")
    MYSCHEME_API_KEY: str = os.getenv("MYSCHEME_API_KEY", "")
    MYSCHEME_API_CLIENT_ID: str = os.getenv("MYSCHEME_API_CLIENT_ID", "")
    MYSCHEME_API_CLIENT_SECRET: str = os.getenv("MYSCHEME_API_CLIENT_SECRET", "")
    MYSCHEME_API_AUTH_MODE: str = os.getenv("MYSCHEME_API_AUTH_MODE", "api_key")
    ENABLE_MYSCHEME_INTEGRATION: bool = os.getenv("ENABLE_MYSCHEME_INTEGRATION", "false").lower() == "true"
    
    # Bhashini Configuration
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
