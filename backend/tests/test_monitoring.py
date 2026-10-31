import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.monitoring.fingerprint import (
    sanitize_extracted_text,
    calculate_content_fingerprint,
    detect_meaningful_difference
)
from app.monitoring.crawler import OfficialSchemeCrawler
from app.monitoring.models import SourceDefinition, SourceCategory, SourceType, AccessibilityStatus
from app.monitoring.source_registry import SourceRegistry
from app.monitoring.monitor_service import monitor_service
from app.db.repository import MonitoringRepository
from app.engine.evaluator import evaluate_all_schemes
from app.models.profile import CitizenProfile
from app.services.scheme_service import scheme_service
from app.db.database import get_db_connection, seed_monitoring_sources, seed_monitoring_demo_data

client = TestClient(app)
VALID_ADMIN_KEY = getattr(settings, "ADMIN_API_KEY", "yojnasarthi-admin-secret-2026")

@pytest.fixture(autouse=True)
def setup_monitoring_db():
    conn = get_db_connection()
    seed_monitoring_sources(conn)
    seed_monitoring_demo_data(conn)

# 1. Sanitization & HTML Chrome Stripping Tests
def test_html_sanitization_removes_scripts_and_chrome():
    raw_html = """
    <html>
        <head><script>alert('csrf');</script><style>.body{color:red;}</style></head>
        <body>
            <nav><a href="/home">Home</a><a href="/login">Login</a></nav>
            <header><h1>Ministry Header</h1></header>
            <main>
                <h2>PM-KISAN Samman Nidhi</h2>
                <p>Eligible landholder farmers will receive ₹6,000 per year in 3 equal installments.</p>
                <span>Current time: 31/10/2026 14:30:22</span>
            </main>
            <footer><p>Copyright 2026</p></footer>
        </body>
    </html>
    """
    clean = sanitize_extracted_text(raw_html)
    assert "alert" not in clean
    assert "color:red" not in clean
    assert "Login" not in clean
    assert "PM-KISAN Samman Nidhi" in clean
    assert "₹6,000" in clean
    # Timestamp stripped
    assert "14:30:22" not in clean

def test_fingerprint_calculation_deterministic():
    text1 = "Landholding farmer entitlement: ₹6000 per year."
    text2 = "Landholding farmer entitlement: ₹6000 per year."
    h1 = calculate_content_fingerprint(text1)
    h2 = calculate_content_fingerprint(text2)
    assert h1 == h2
    assert len(h1) == 64

def test_insignificant_whitespace_ignored():
    old_text = "Eligibility criteria: Citizen must reside in Madhya Pradesh."
    new_text = "Eligibility criteria:   Citizen must reside in \n\n Madhya Pradesh.   "
    is_meaningful, reason = detect_meaningful_difference(old_text, new_text)
    assert is_meaningful is False
    assert "No meaningful" in reason

def test_meaningful_eligibility_change_detected():
    old_text = "Eligibility criteria: Family annual income must not exceed ₹2.5 Lakh. Age 21 to 60."
    new_text = "Eligibility criteria: Family annual income must not exceed ₹3.0 Lakh. Age 21 to 65."
    is_meaningful, summary = detect_meaningful_difference(old_text, new_text)
    assert is_meaningful is True
    assert "Meaningful content update" in summary

# 2. RSS / Atom Feed Parsing
def test_rss_feed_parsing():
    sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>National Schemes Feed</title>
            <item>
                <title>PM-KISAN 17th Installment Released</title>
                <description>Government transfers ₹20,000 crore to 9.26 crore farmers.</description>
                <link>https://pmkisan.gov.in/news/17</link>
                <pubDate>Wed, 18 Jun 2026 09:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """
    extracted = OfficialSchemeCrawler._extract_rss_text(sample_rss)
    assert "PM-KISAN 17th Installment Released" in extracted
    assert "₹20,000 crore" in extracted

# 3. Source Isolation on Unavailability
@pytest.mark.anyio
async def test_crawler_handles_unavailability_gracefully():
    dummy_source = SourceDefinition(
        source_id="dummy_broken_portal",
        name="Broken Department Portal",
        category=SourceCategory.OTHER,
        official_url="http://127.0.0.1:59999/non-existent-portal",
        source_type=SourceType.HTML
    )
    text, h, status, error = await OfficialSchemeCrawler.fetch_source_content(dummy_source)
    assert status == AccessibilityStatus.UNAVAILABLE
    assert text is None
    assert error is not None

# 4. Administrative Endpoint Security Protection
def test_admin_endpoints_require_authorization():
    # Missing header -> 401
    resp = client.get("/api/admin/monitoring/summary")
    assert resp.status_code == 401
    assert "Unauthorized" in resp.json()["detail"]

    # Wrong header -> 401
    resp2 = client.get("/api/admin/monitoring/summary", headers={"X-Admin-Key": "wrong-key"})
    assert resp2.status_code == 401

    # Valid key -> 200
    resp3 = client.get("/api/admin/monitoring/summary", headers={"X-Admin-Key": VALID_ADMIN_KEY})
    assert resp3.status_code == 200
    data = resp3.json()
    assert "total_schemes_monitored" in data
    assert "total_sources_monitored" in data
    assert data["total_sources_monitored"] >= 10

def test_admin_list_sources_and_pending_updates():
    headers = {"X-Admin-Key": VALID_ADMIN_KEY}

    sources_resp = client.get("/api/admin/monitoring/sources", headers=headers)
    assert sources_resp.status_code == 200
    sources = sources_resp.json()
    assert len(sources) >= 10
    assert any(s["source_id"] == "src_mp_ladlibehna" for s in sources)
    assert any(s["source_id"] == "src_central_pmkisan" for s in sources)

    updates_resp = client.get("/api/admin/monitoring/pending-updates?include_demo=true", headers=headers)
    assert updates_resp.status_code == 200
    updates = updates_resp.json()
    assert len(updates) >= 1
    demo_upd = next((u for u in updates if u["is_demo"]), None)
    assert demo_upd is not None
    assert demo_upd["status"] in ["PENDING", "APPROVED", "REJECTED"]

# 5. Approval & Rejection Workflow Tests
def test_approve_and_reject_pending_update():
    headers = {"X-Admin-Key": VALID_ADMIN_KEY}

    # Test Rejection
    reject_payload = {
        "reviewer_name": "Audit Officer Sharma",
        "reason": "Clarification: Proposal already covered under existing DBT circular."
    }
    rej_resp = client.post(
        "/api/admin/monitoring/updates/demo_upd_ladlibehna_01/reject",
        json=reject_payload,
        headers=headers
    )
    assert rej_resp.status_code == 200
    assert "Successfully rejected" in rej_resp.json()["message"]

    # Test Approval
    approve_payload = {
        "reviewer_name": "Chief Policy Reviewer Verma",
        "reason": "Verified against Gazette notification No. 442/2026."
    }
    appr_resp = client.post(
        "/api/admin/monitoring/updates/demo_upd_ladlibehna_01/approve",
        json=approve_payload,
        headers=headers
    )
    assert appr_resp.status_code == 200
    assert "Successfully approved" in appr_resp.json()["message"]

def test_scheme_version_history_and_rollback():
    headers = {"X-Admin-Key": VALID_ADMIN_KEY}

    hist_resp = client.get("/api/admin/monitoring/schemes/ladli_behna_mp/history", headers=headers)
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert len(hist["versions"]) >= 1

    first_ver_id = hist["versions"][0]["version_id"]

    # Test Rollback
    rb_payload = {
        "target_version_id": first_ver_id,
        "reviewer_name": "Supervisor Officer Patel"
    }
    rb_resp = client.post(
        "/api/admin/monitoring/schemes/ladli_behna_mp/rollback",
        json=rb_payload,
        headers=headers
    )
    assert rb_resp.status_code == 200
    assert "Successfully rolled back" in rb_resp.json()["message"]

# 6. CRITICAL INVARIANT: Unapproved Updates NEVER Alter Eligibility Evaluation
def test_unapproved_updates_do_not_alter_eligibility_engine():
    """
    Guarantees that pending or unapproved monitoring updates never affect
    the deterministic Python rule evaluator.
    """
    # 29-year-old female in MP with income ₹1.5L and DBT passbook
    profile = CitizenProfile(
        age=29,
        gender="female",
        state="Madhya Pradesh",
        marital_status="married",
        annual_income=150000,
        holds_constitutional_post=False,
        landholding_hectares=0.0,
        has_bank_passbook=True
    )
    resp = evaluate_all_schemes(scheme_service.get_all_schemes(), profile)
    all_results = resp.eligible + resp.not_sure + resp.not_eligible
    ladli_result = next((r for r in all_results if r.scheme_id == "ladli_behna_mp"), None)
    
    assert ladli_result is not None
    # Must remain ELIGIBLE based on approved rule catalogue
    assert ladli_result.status == "ELIGIBLE"
    # Rule reasons are purely from deterministic evaluated rules
    assert any("21 से 60" in c or "21 and 60" in c for c in ladli_result.satisfied_conditions + ladli_result.satisfied_conditions_hi)

# 7. Integration Status & Health Check Reporting
def test_integration_status_includes_monitoring():
    resp = client.get("/api/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "scheme_monitoring" in data
    assert data["scheme_monitoring"]["status"] == "active"
    assert data["scheme_monitoring"]["total_sources_monitored"] >= 10
    assert "data_gov_in" in data
    assert data["data_gov_in"]["mode"] == "public_catalog_mode"

def test_health_check_includes_monitoring():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "monitoring" in data
    assert data["monitoring"]["sources_tracked"] >= 10
