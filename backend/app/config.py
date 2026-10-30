import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseModel):
    PROJECT_NAME: str = "YojnaSarthi Backend"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # AI Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Bhashini Keys
    BHASHINI_USER_ID: str = os.getenv("BHASHINI_USER_ID", "")
    BHASHINI_API_KEY: str = os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_PIPELINE_ID: str = os.getenv("BHASHINI_PIPELINE_ID", "")
    
    # Schemes data directory
    SCHEMES_DIR: Path = Path(__file__).resolve().parent.parent / "data" / "schemes"
    
    # Verification tolerance (e.g., maximum scheme verification age in days)
    MAX_SCHEME_VERIFICATION_AGE_DAYS: int = 180

settings = Settings()
