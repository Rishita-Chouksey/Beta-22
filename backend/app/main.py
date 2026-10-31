import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .routes import eligibility, schemes, checklist, ai, voice, documents, bhashini, admin_monitoring, translator
from .services.scheme_service import scheme_service
from .services.myscheme_adapter import myscheme_adapter
from .services.bhashini_adapter import bhashini_adapter
from .services.azure_translator_service import azure_translator_service
from .services.document_service import document_service
from .db.database import (
    init_db,
    seed_schemes_from_json,
    seed_monitoring_sources,
    seed_monitoring_demo_data,
    get_db_connection
)
from .db.repository import RateLimiterRepository, FeedbackRepository, MonitoringRepository
from .models.api import FeedbackRequest, FeedbackResponse
from .monitoring.scheduler import monitoring_scheduler

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
        seed_monitoring_sources()
        seed_monitoring_demo_data()
    except Exception as e:
        logger.warning(f"Database init warning: {e}")

    scheme_service.load_schemes()
    logger.info(f"Loaded {len(scheme_service.get_all_schemes())} schemes into catalog (data source: {scheme_service.get_data_source()}).")

    # Start background scheduler if enabled
    if getattr(settings, "ENABLE_AUTOMATIC_MONITORING", True):
        monitoring_scheduler.interval_seconds = getattr(settings, "MONITORING_INTERVAL_SECONDS", 86400)
        monitoring_scheduler.start()

    yield

    # Clean shutdown
    monitoring_scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-first, deterministic AI-assisted government scheme eligibility, Document Guide, and Scheme Intelligence platform for Indian citizens.",
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
app.include_router(voice.router, prefix=settings.API_PREFIX, tags=["Voice & Language (Legacy)"])
app.include_router(documents.router, prefix=settings.API_PREFIX, tags=["Document Guide"])
app.include_router(bhashini.router, prefix=settings.API_PREFIX, tags=["Bhashini Official Integration"])
app.include_router(translator.router, prefix=settings.API_PREFIX, tags=["Azure AI Translator"])
app.include_router(admin_monitoring.router, prefix=settings.API_PREFIX, tags=["Admin Scheme Monitoring"])

@app.get("/api/integrations/status", tags=["Integration Status"])
async def get_integrations_status():
    """
    Detailed status report of all system integrations:
    - myScheme / API Setu
    - Bhashini Translation
    - Bhashini ASR
    - Bhashini TTS
    - Python Eligibility Engine
    - Document Guide
    - Scheme Intelligence & Catalogue Monitoring
    - data.gov.in Public Catalog
    """
    myscheme_stat = myscheme_adapter.get_status()
    bhashini_stat = bhashini_adapter.get_status()
    azure_stat = azure_translator_service.get_status()
    monitoring_summary = MonitoringRepository.get_monitoring_summary()
    scheduler_status = monitoring_scheduler.get_status()

    return {
        "myscheme": {
            "name": "myScheme / API Setu",
            "status": myscheme_stat.status,
            "is_live_api": myscheme_stat.is_live_api,
            "active_data_source": myscheme_stat.active_data_source,
            "message": myscheme_stat.message,
            "access_requirements": myscheme_stat.access_requirements,
            "last_checked": myscheme_stat.last_checked
        },
        "scheme_monitoring": {
            "name": "Scheme Intelligence & Catalogue Monitoring",
            "status": "active" if monitoring_summary["total_sources_monitored"] > 0 else "idle",
            "monitoring_enabled": scheduler_status["is_running"],
            "total_sources_monitored": monitoring_summary["total_sources_monitored"],
            "healthy_sources": monitoring_summary["total_sources_monitored"] - monitoring_summary["outdated_or_unavailable_sources"],
            "unavailable_or_degraded_sources": monitoring_summary["outdated_or_unavailable_sources"],
            "updates_awaiting_review": monitoring_summary["updates_awaiting_review"],
            "last_run": monitoring_summary["last_monitoring_run"],
            "next_run": scheduler_status["next_run"],
            "mode": "Polite Official Public Crawler + Human-in-the-Loop Verification"
        },
        "data_gov_in": {
            "name": "Open Government Data (data.gov.in)",
            "status": "active",
            "is_live_api": False,
            "mode": "public_catalog_mode",
            "message": "Monitored as public discovery source; API Setu credentials optional."
        },
        "azure_translator": azure_stat,
        "bhashini_translation": {
            "name": "Bhashini NMT Text Translation",
            "status": bhashini_stat["translation"],
            "is_live_api": bhashini_stat["is_live_api"],
            "supported_pairs": ["English ↔ Hindi", "Indic Languages"],
            "caching": "Deterministic SHA-256 (24h TTL)",
            "message": bhashini_stat["message"],
            "last_checked": bhashini_stat["last_checked"]
        },
        "bhashini_asr": {
            "name": "Bhashini Automatic Speech Recognition",
            "status": bhashini_stat["asr"],
            "is_live_api": bhashini_stat["is_live_api"],
            "message": bhashini_stat["message"],
            "fallback": "Browser Web Speech API active",
            "last_checked": bhashini_stat["last_checked"]
        },
        "bhashini_tts": {
            "name": "Bhashini Text-To-Speech",
            "status": bhashini_stat["tts"],
            "is_live_api": bhashini_stat["is_live_api"],
            "message": bhashini_stat["message"],
            "fallback": "Browser SpeechSynthesis active",
            "last_checked": bhashini_stat["last_checked"]
        },
        "eligibility_engine": {
            "name": "Deterministic Python Rule Engine",
            "status": "active",
            "rules_count": sum(len(s.rules) for s in scheme_service.get_all_schemes()),
            "schemes_evaluated": len(scheme_service.get_all_schemes()),
            "ai_isolation": "100% Deterministic (LLM cannot decide or alter eligibility rules)"
        },
        "document_guide": {
            "name": "Document Guide & Procurement Catalog",
            "status": "active",
            "documents_cataloged": len(document_service.get_all_documents()),
            "interactive_samples": True,
            "official_portals_linked": True
        }
    }

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

    monitoring_summary = MonitoringRepository.get_monitoring_summary()

    return {
        "status": "healthy",
        "service": "YojnaSarthi API",
        "version": settings.VERSION,
        "database": db_status,
        "schemes_loaded": len(scheme_service.get_all_schemes()),
        "active_data_source": scheme_service.get_data_source(),
        "document_guide_items": len(document_service.get_all_documents()),
        "monitoring": {
            "sources_tracked": monitoring_summary["total_sources_monitored"],
            "pending_approvals": monitoring_summary["updates_awaiting_review"]
        },
        "privacy": "Zero-PII-logged memory-only mode active"
    }
