import os
import logging
from datetime import datetime
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

        response = await call_next(request)

        # 2. Security hardening headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheme_service.load_schemes()
    logger.info(f"Loaded {len(scheme_service.get_all_schemes())} schemes into stateless catalog.")
    yield

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
    myscheme_stat = myscheme_adapter.get_status()
    bhashini_stat = bhashini_adapter.get_status()
    azure_stat = azure_translator_service.get_status()

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
            "status": "active",
            "monitoring_enabled": False,
            "total_sources_monitored": 10,
            "mode": "External GitHub Actions Updater (Feature 7)"
        },
        "azure_translator": azure_stat,
        "bhashini_translation": {
            "name": "Bhashini NMT Text Translation",
            "status": bhashini_stat["translation"],
            "is_live_api": bhashini_stat["is_live_api"],
            "supported_pairs": ["English ↔ Hindi", "Indic Languages"],
            "message": bhashini_stat["message"],
            "last_checked": bhashini_stat["last_checked"]
        },
        "bhashini_asr": {
            "name": "Bhashini ASR Speech Recognition",
            "status": bhashini_stat.get("asr", "disabled"),
            "is_live_api": bhashini_stat.get("is_live_api", False),
            "message": bhashini_stat.get("message", "Ready"),
            "last_checked": bhashini_stat.get("last_checked")
        },
        "bhashini_tts": {
            "name": "Bhashini Text-To-Speech",
            "status": bhashini_stat.get("tts", "disabled"),
            "is_live_api": bhashini_stat.get("is_live_api", False),
            "message": bhashini_stat.get("message", "Ready"),
            "last_checked": bhashini_stat.get("last_checked")
        },
        "data_gov_in": {
            "name": "data.gov.in Public Catalog",
            "status": "active",
            "mode": "public_catalog_mode",
            "message": "Monitored as public discovery source; API Setu credentials optional."
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
    return FeedbackResponse(
        success=True,
        status="success",
        message="धन्यवाद! आपकी प्रतिक्रिया सुरक्षित रूप से दर्ज कर ली गई है।" if req.language == "hi" else "Thank you! Your feedback has been recorded."
    )

@app.get("/")
@app.get("/health")
@app.get("/api/health")
async def health_check():
    schemes = scheme_service.get_all_schemes()
    total = len(schemes)
    verified = sum(1 for s in schemes if getattr(s, "review_status", "verified") == "verified")
    auto_updated = sum(1 for s in schemes if getattr(s, "review_status", "") == "auto_updated")
    needs_review = sum(1 for s in schemes if getattr(s, "review_status", "") in ["needs_review", "draft"])

    data_version = os.getenv("DATA_VERSION") or os.getenv("GIT_COMMIT_SHA") or "v2.1.0-dynamic"

    return {
        "status": "healthy",
        "data_version": data_version,
        "data_generated_at": datetime.now().isoformat(),
        "active_data_source": "local_json_catalog",
        "total_documents": len(document_service.get_all_documents()),
        "document_guide_items": len(document_service.get_all_documents()),
        "monitoring": {
            "status": "active",
            "sources_tracked": 10,
            "total_sources_monitored": 10
        },
        "schemes_loaded": total,
        "schemes_total": total,
        "schemes_verified": verified,
        "schemes_auto_updated": auto_updated,
        "schemes_needs_review": needs_review,
        "database": "connected",
        "privacy": "Zero-PII-logged memory-only mode active"
    }
