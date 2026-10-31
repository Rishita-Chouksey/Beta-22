import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SCHEMES_DIR = DATA_DIR / "schemes"
REPORTS_DIR = REPO_ROOT / "reports"
ALLOWED_DOMAINS_PATH = DATA_DIR / "allowed_domains.json"
SOURCE_REGISTRY_PATH = DATA_DIR / "source_registry.json"

PER_DOMAIN_DELAY_SECONDS = float(os.getenv("PER_DOMAIN_DELAY_SECONDS", "2.0"))
FETCH_TIMEOUT_SECONDS = float(os.getenv("FETCH_TIMEOUT_SECONDS", "20.0"))
MAX_PAGE_BYTES = int(os.getenv("MAX_PAGE_BYTES", "5000000"))
MAX_SCHEMES_PER_RUN = int(os.getenv("MAX_SCHEMES_PER_RUN", "300"))
MAX_AI_CALLS_PER_RUN = int(os.getenv("MAX_AI_CALLS_PER_RUN", "40"))
AUTO_APPLY_RULES = os.getenv("AUTO_APPLY_RULES", "true").lower() in ("true", "1", "yes")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY", "")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION", "global")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "")

USER_AGENT = os.getenv(
    "UPDATER_USER_AGENT",
    "YojnaSarthi-SchemeUpdater/2.1 (+https://github.com/org/yojnasarthi; bot@yojnasarthi.org)"
)
