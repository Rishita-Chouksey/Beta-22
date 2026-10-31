import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .routes import eligibility, schemes, checklist, ai, voice
from .services.scheme_service import scheme_service
from .db.database import init_db, seed_schemes_from_json, get_db_connection
from .db.repository import RateLimiterRepository, FeedbackRepository
from .models.api import FeedbackRequest, FeedbackResponse

# Privacy Protection: Configure logging to exclude personal citizen data
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("yojnasarthi")

class SecurityAndPrivacyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # 1. Privacy logging (exclude personal citizen payloads)
        if not path.startswith("/api/speech-to-text"):
            logger.info(f"Incoming request: {method} {path}")

        # 2. Rate limiting on sensitive AI endpoints to prevent quota depletion and abuse
        if path in ["/api/chat", "/api/parse-text", "/api/form-help"] and method == "POST":
            client_ip = request.client.host if request.client else "127.0.0.1"
            # 40 requests per minute per client IP
            if RateLimiterRepository.is_rate_limited(client_ip, path, max_requests=40, window_seconds=60):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please wait a moment before sending another message."}
                )

        response = await call_next(request)

        # 3. Security hardening headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and sync verified schemes
    try:
        init_db()
        seed_schemes_from_json()
    except Exception as e:
        logger.warning(f"Database init warning: {e}")

    scheme_service.load_schemes()
    logger.info(f"Loaded {len(scheme_service.get_all_schemes())} government schemes into catalog.")
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

app.add_middleware(SecurityAndPrivacyMiddleware)

# Include Routers
app.include_router(eligibility.router, prefix=settings.API_PREFIX, tags=["Eligibility"])
app.include_router(schemes.router, prefix=settings.API_PREFIX, tags=["Schemes"])
app.include_router(checklist.router, prefix=settings.API_PREFIX, tags=["Checklist"])
app.include_router(ai.router, prefix=settings.API_PREFIX, tags=["AI Assistance"])
app.include_router(voice.router, prefix=settings.API_PREFIX, tags=["Voice & Language"])

@app.post("/api/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(req: FeedbackRequest):
    """Stores citizen feedback anonymously in the database."""
    success = FeedbackRepository.save_feedback(
        scheme_id=req.scheme_id,
        rating=req.rating,
        is_helpful=req.is_helpful,
        comment=req.comment,
        language=req.language
    )
    if success:
        return FeedbackResponse(
            success=True,
            message="धन्यवाद! आपकी प्रतिक्रिया सुरक्षित रूप से दर्ज कर ली गई है।" if req.language == "hi" else "Thank you! Your feedback has been recorded."
        )
    return FeedbackResponse(
        success=False,
        message="Could not save feedback at this time."
    )

@app.get("/")
@app.get("/health")
async def health_check():
    db_status = "connected"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"unavailable: {e}"

    return {
        "status": "healthy",
        "service": "YojnaSarthi API",
        "version": settings.VERSION,
        "database": db_status,
        "schemes_loaded": len(scheme_service.get_all_schemes()),
        "privacy": "Zero-PII-logged memory-only mode active"
    }
