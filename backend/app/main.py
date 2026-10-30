import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .routes import eligibility, schemes, checklist, ai, voice
from .services.scheme_service import scheme_service

# Privacy Protection: Configure logging to exclude personal citizen data
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("yojnasarthi")

class PrivacyPreservingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We deliberately do not log query params or request payloads to preserve privacy
        path = request.url.path
        method = request.method
        if not path.startswith("/api/speech-to-text"):
            logger.info(f"Incoming request: {method} {path}")
        response = await call_next(request)
        return response

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheme_service.load_schemes()
    logger.info(f"Loaded {len(scheme_service.get_all_schemes())} government schemes.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-first, deterministic AI-assisted government scheme eligibility engine for Indian citizens.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrivacyPreservingMiddleware)

# Include Routers
app.include_router(eligibility.router, prefix=settings.API_PREFIX, tags=["Eligibility"])
app.include_router(schemes.router, prefix=settings.API_PREFIX, tags=["Schemes"])
app.include_router(checklist.router, prefix=settings.API_PREFIX, tags=["Checklist"])
app.include_router(ai.router, prefix=settings.API_PREFIX, tags=["AI Assistance"])
app.include_router(voice.router, prefix=settings.API_PREFIX, tags=["Voice & Language"])

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "YojnaSarthi API",
        "version": settings.VERSION,
        "schemes_loaded": len(scheme_service.get_all_schemes()),
        "privacy": "Zero-PII-logged memory-only mode active"
    }
