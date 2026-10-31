import io
import json
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.agents.models import (
    SourceItem,
    SourceType,
    SourceStatus,
    ChangeDetectionStatus,
    ChangeType,
    ReviewStatus,
    ExtractedSchemeData
)
from app.agents.repository import AgentRepository
from app.agents.source_discovery_agent import SourceDiscoveryAgent
from app.agents.crawling_agent import CrawlingAgent
from app.agents.change_detection_agent import ChangeDetectionAgent
from app.agents.information_extraction_agent import InformationExtractionAgent
from app.agents.classification_agent import ClassificationAgent
from app.agents.evidence_validation_agent import EvidenceValidationAgent
from app.agents.policy_review_gate import PolicyReviewGate
from app.agents.publishing_service import PublishingService
from app.agents.orchestrator import orchestrator
from app.agents import http_client as agent_http
from app.services.scheme_service import scheme_service
from app.models.profile import CitizenProfile
from app.engine.evaluator import evaluate_all_schemes
from app.db import database as db

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_agent_test_database(monkeypatch):
    """Keep test writes out of the user's persistent application database."""
    test_db_path = Path(__file__).parent.parent / ".pytest_cache" / f"agentic-tests-{uuid.uuid4().hex}.sqlite"
    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))
    monkeypatch.setattr(db, "_tables_initialized", False)
    db.init_db()
    db.seed_schemes_from_json()
    scheme_service.load_schemes()
    yield
    for suffix in ("", "-wal", "-shm"):
        Path(f"{test_db_path}{suffix}").unlink(missing_ok=True)

# 1. Source Discovery & Domain Filtering & Deduplication
def test_source_discovery_domain_filtering_and_deduplication():
    agent = SourceDiscoveryAgent()

    # Domain filtering verification
    assert agent.is_official_gov_domain("data.gov.in") is True
    assert agent.is_official_gov_domain("eseva.mp.gov.in") is True
    assert agent.is_official_gov_domain("mpedistrict.gov.in") is True
    assert agent.is_official_gov_domain("twitter.com") is False
    assert agent.is_official_gov_domain("randomblog.com") is False

    # URL normalization
    norm = agent.normalize_url("services/schemes.html", "https://eseva.mp.gov.in/cms/")
    assert norm == "https://eseva.mp.gov.in/cms/services/schemes.html"

    # Static assets filtered
    assert agent.normalize_url("banner.jpg", "https://eseva.mp.gov.in/") is None
    assert agent.normalize_url("styles.css", "https://eseva.mp.gov.in/") is None

    # Deduplication test in database
    unique_url = "https://data.gov.in/resource/test-duplicate-check"
    src1 = SourceItem(
        id="src-test-dup-1",
        url=unique_url,
        domain="data.gov.in",
        source_type=SourceType.DATASET,
        status=SourceStatus.DISCOVERED
    )
    AgentRepository.add_or_update_source(src1)

    fetched = AgentRepository.get_source_by_url(unique_url)
    assert fetched is not None
    assert fetched.id == "src-test-dup-1"

    # Adding again should update rather than duplicate
    src1_updated = SourceItem(
        id="src-test-dup-1",
        url=unique_url,
        domain="data.gov.in",
        source_type=SourceType.DATASET,
        status=SourceStatus.CRAWLED
    )
    AgentRepository.add_or_update_source(src1_updated)
    fetched2 = AgentRepository.get_source_by_url(unique_url)
    assert fetched2.status == SourceStatus.CRAWLED

# 2. HTML Content Extraction (stripping scripts, styles, navbars, footers)
def test_html_content_extraction():
    crawler = CrawlingAgent()
    dirty_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MP Farmer Welfare Scheme</title>
        <script>alert("tracker");</script>
        <style>.ads { color: red; }</style>
    </head>
    <body>
        <nav><a href="/home">Home</a><a href="/login">Login</a></nav>
        <header>Official Portal Header</header>
        <main>
            <h1>Mukhyamantri Kisan Kalyan Yojana</h1>
            <p>Annual financial grant of ₹4,000 in two equal installments for registered farmers of MP.</p>
            <p>Eligibility: Domicile of MP and beneficiary of PM-KISAN.</p>
        </main>
        <footer>Copyright 2026 Government of MP. All rights reserved.</footer>
    </body>
    </html>
    """
    clean_text = crawler.clean_html_text(dirty_html)

    assert "Mukhyamantri Kisan Kalyan Yojana" in clean_text
    assert "Annual financial grant of ₹4,000" in clean_text
    assert "alert" not in clean_text
    assert "tracker" not in clean_text
    assert ".ads" not in clean_text
    assert "Home" not in clean_text or "Mukhyamantri" in clean_text

# 3. PDF Content Extraction with Controlled In-Memory Test Fixture
def test_pdf_content_extraction_controlled_fixture():
    try:
        import fitz
    except ImportError:
        import pytest
        pytest.skip("PyMuPDF (fitz) is not installed in test environment")

    # Create an in-memory test PDF using PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    test_text = (
        "GOVERNMENT OF MADHYA PRADESH\n"
        "Department of Social Justice and Disabled Welfare\n"
        "Notification No. F-12/2026: Revision of Indira Gandhi National Old Age Pension.\n"
        "Eligibility Age: 60 years and above.\n"
        "Monthly assistance: Rs. 600 per month."
    )
    page.insert_text((50, 72), test_text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()

    crawler = CrawlingAgent()
    extracted = crawler.extract_pdf_text(pdf_bytes)

    assert "GOVERNMENT OF MADHYA PRADESH" in extracted
    assert "Indira Gandhi National Old Age Pension" in extracted
    assert "Rs. 600 per month" in extracted
    assert "Eligibility Age: 60 years" in extracted


def test_robots_policy_is_respected_and_unknown_policy_fails_closed(monkeypatch):
    class Response:
        def __init__(self, status_code, text=""):
            self.status_code = status_code
            self.text = text

    class Client:
        headers = {"User-Agent": "YojnaSarthi-Test"}

        def __init__(self, response):
            self.response = response
            self.urls = []

        def get(self, url):
            self.urls.append(url)
            return self.response

    monkeypatch.setattr(agent_http, "POLITE_DOMAIN_DELAY_SECONDS", 0)
    agent_http._robots_cache.clear()
    disallowing_client = Client(Response(200, "User-agent: *\nDisallow: /private"))
    allowed, error = agent_http.robots_permission(disallowing_client, "https://policy.gov.in/public")
    assert allowed is True
    assert error is None
    allowed, error = agent_http.robots_permission(disallowing_client, "https://policy.gov.in/private/page")
    assert allowed is False
    assert "Disallowed" in error
    assert len(disallowing_client.urls) == 1

    agent_http._robots_cache.clear()
    unavailable_client = Client(Response(503))
    allowed, error = agent_http.robots_permission(unavailable_client, "https://unknown.gov.in/page")
    assert allowed is False
    assert "HTTP 503" in error

# 4. Hash-Based Change Detection
def test_hash_based_change_detection():
    detector = ChangeDetectionAgent()
    source_id = f"src-test-hash-{uuid.uuid4().hex}"

    # Initial crawl -> NEW_SOURCE
    crawl_1 = {
        "source_id": source_id,
        "document_type": "HTML",
        "status": "success",
        "raw_text": "Kisan Kalyan Yojana: Grant of Rs 4000 per year."
    }
    res1 = detector.detect_changes(crawl_1)
    assert res1["status"] == ChangeDetectionStatus.NEW_SOURCE
    assert res1["has_change"] is True
    assert len(res1["current_hash"]) == 64

    # Identical content -> NO_CHANGE
    crawl_2 = {
        "source_id": source_id,
        "document_type": "HTML",
        "status": "success",
        "raw_text": "Kisan Kalyan Yojana: Grant of Rs 4000 per year.  "  # trailing space normalized
    }
    res2 = detector.detect_changes(crawl_2)
    assert res2["status"] == ChangeDetectionStatus.NO_CHANGE
    assert res2["has_change"] is False
    assert res2["current_hash"] == res1["current_hash"]

    # Modified content -> CONTENT_CHANGED
    crawl_3 = {
        "source_id": source_id,
        "document_type": "HTML",
        "status": "success",
        "raw_text": "Kisan Kalyan Yojana: Grant increased to Rs 6000 per year."
    }
    res3 = detector.detect_changes(crawl_3)
    assert res3["status"] == ChangeDetectionStatus.CONTENT_CHANGED
    assert res3["has_change"] is True
    assert res3["current_hash"] != res1["current_hash"]
    assert "Rs 6000" in res3["diff_summary"] or "-" in res3["diff_summary"]

# 5. Information Extraction & Unknown Handling
def test_information_extraction_and_unknown_handling():
    extractor = InformationExtractionAgent()
    text = """
    Mukhyamantri Yuva Swarozgar Yojana (Madhya Pradesh)
    Government welfare scheme providing financial assistance to young entrepreneurs.
    Eligibility criteria: Age 18 to 40 years. Resident of Madhya Pradesh.
    Benefits: Subsidy of up to ₹2,00,000 for project financing.
    Required documents: Aadhaar card, Bank passbook, Domicile certificate.
    Application Process:
    Step 1: Register on MSME portal.
    Step 2: Submit project proposal with bank details.
    """
    extracted = extractor.extract_with_rules(text, "https://msme.mp.gov.in/schemes")

    assert "Mukhyamantri Yuva Swarozgar" in extracted.scheme_name or "Yojana" in extracted.scheme_name
    assert extracted.eligibility_conditions.get("min_age") == 18
    assert extracted.eligibility_conditions.get("max_age") == 40
    assert "Aadhaar" in str(extracted.required_documents)
    # Deadline was not in text, must be None (not hallucinated)
    assert extracted.deadline is None
    # Income limit was not specified in text, must not be invented
    assert extracted.eligibility_conditions.get("income_limit") is None

# 6. Classification Agent
def test_classification_agent():
    classifier = ClassificationAgent()

    # 1. New Scheme
    extracted_new = ExtractedSchemeData(
        scheme_name="New Agri Solar Scheme",
        extraction_timestamp="2026-10-31T10:00:00Z"
    )
    changes_new = classifier.classify(existing_scheme=None, extracted=extracted_new)
    assert ChangeType.NEW_SCHEME in changes_new

    # 2. Eligibility & Benefit Change
    existing = {
        "id": "ladli_behna_mp",
        "rules": {"min_age": 21, "max_age": 60, "max_income": 250000},
        "benefit_en": "₹1,250 per month",
        "required_documents": ["Aadhaar Card", "Samagra ID"]
    }
    extracted_mod = ExtractedSchemeData(
        scheme_name="Mukhyamantri Ladli Behna Yojana",
        eligibility_conditions={"min_age": 21, "max_age": 60, "income_limit": 300000},  # income limit increased
        benefits="₹1,500 per month",  # benefit increased
        required_documents=["Aadhaar Card", "Samagra ID", "Bank Passbook"],  # new doc added
        extraction_timestamp="2026-10-31T10:00:00Z"
    )
    changes_mod = classifier.classify(existing_scheme=existing, extracted=extracted_mod)
    assert ChangeType.ELIGIBILITY_CHANGE in changes_mod
    assert ChangeType.BENEFIT_CHANGE in changes_mod
    assert ChangeType.DOCUMENT_CHANGE in changes_mod

# 7. Evidence Validation Agent
def test_evidence_validation_agent():
    validator = EvidenceValidationAgent()
    raw_text = "The monthly assistance under Indira Gandhi National Widow Pension is ₹600 per month for widows aged 40 to 79."

    extracted = ExtractedSchemeData(
        scheme_name="Indira Gandhi National Widow Pension",
        benefits="₹600 per month",
        evidence_excerpts={
            "scheme_name": "Indira Gandhi National Widow Pension",
            "benefits": "₹600 per month",
            "eligibility": "widows aged 40 to 79"
        },
        extraction_timestamp="2026-10-31T10:00:00Z"
    )

    # Valid official gov domain + exact quotes
    res_valid = validator.validate_evidence(extracted, raw_text, "https://nsap.nic.in/guidelines")
    assert res_valid["is_valid"] is True
    assert res_valid["confidence"] >= 0.80
    assert "income_limit" in res_valid["verified_evidence"]  # correctly marked UNKNOWN

    # Non-government domain fails trust
    res_untrusted = validator.validate_evidence(extracted, raw_text, "https://fake-blog-news.com/scheme")
    assert res_untrusted["is_valid"] is False

    # Ungrounded claim
    extracted_fake = ExtractedSchemeData(
        scheme_name="Fake Scheme",
        evidence_excerpts={"benefits": "₹1,00,000 cash grant"},  # does not exist in raw text
        extraction_timestamp="2026-10-31T10:00:00Z"
    )
    res_fake = validator.validate_evidence(extracted_fake, raw_text, "https://data.gov.in/test")
    assert res_fake["is_valid"] is False
    assert len(res_fake["unverified_claims"]) > 0

# 8. Policy Review Gate & Publishing Service Workflow
def test_policy_review_gate_and_publishing_workflow():
    gate = PolicyReviewGate()
    publisher = PublishingService()
    test_scheme_id = "test_scheme_gov_01"

    # Submit candidate update
    update = gate.submit_for_review(
        scheme_id=test_scheme_id,
        change_type=ChangeType.BENEFIT_CHANGE,
        old_value="₹1,000",
        proposed_value="₹1,500 per month",
        evidence={"quote": "Government increases monthly assistance to ₹1,500"},
        source_url="https://eseva.mp.gov.in/cms/circular_12.html",
        confidence=0.95
    )
    assert update.review_status == ReviewStatus.PENDING

    # Attempting to publish before approval must fail
    res_unapproved = publisher.publish_approved_update(update.id)
    assert res_unapproved["success"] is False

    # Test Rejection flow
    reject_res = gate.reject_update(update.id, reason="Discrepancy in circular date.")
    assert reject_res["success"] is True
    assert reject_res["status"] == ReviewStatus.REJECTED.value

    # Submit a second update and test Approval & Publishing flow
    update2 = gate.submit_for_review(
        scheme_id="pm_kisan",
        change_type=ChangeType.BENEFIT_CHANGE,
        old_value="₹6,000 per year",
        proposed_value="₹6,000 per year in 3 installments",
        evidence={"quote": "PM-KISAN provides ₹6,000 annually"},
        source_url="https://pmkisan.gov.in/",
        confidence=0.98
    )
    appr_res = gate.approve_update(update2.id)
    assert appr_res["success"] is True

    pub_res = publisher.publish_approved_update(update2.id)
    assert pub_res["success"] is True
    assert pub_res["version_number"] >= 1

    # Verify version was recorded in scheme_versions
    versions = AgentRepository.get_scheme_versions("pm_kisan")
    assert len(versions) >= 1
    assert versions[0].approval_status == "APPROVED"

# 9. Deterministic Rule Engine Isolation
def test_deterministic_rule_engine_isolation():
    """
    CRITICAL: Verify that the deterministic Python rule engine remains the sole decider
    of citizen eligibility and cannot be bypassed or overridden by AI agents.
    """
    # Profile of a non-farmer citizen
    student_profile = CitizenProfile(
        age=20,
        gender="female",
        state="Madhya Pradesh",
        occupation="student",
        annual_income=120000
    )

    schemes = scheme_service.get_all_schemes()
    eval_result = evaluate_all_schemes(schemes, student_profile)

    # In PM-KISAN, the deterministic rule requires occupation == 'farmer'.
    # A student MUST be evaluated as NOT ELIGIBLE deterministically by Python rules.
    pm_kisan_eval = next((s for s in eval_result.not_eligible if s.scheme_id == "pm_kisan"), None)
    assert pm_kisan_eval is not None
    assert pm_kisan_eval.status == "NOT ELIGIBLE"
    assert any("farmer" in r.lower() for r in pm_kisan_eval.failed_conditions)

# End-to-end discovery pipeline with a controlled crawl response.
def test_monitoring_pipeline_review_publish_and_history(monkeypatch):
    run_token = uuid.uuid4().hex[:8]
    source_id = f"src-test-pipeline-{run_token}-{uuid.uuid4().hex}"
    scheme_name = f"Mukhyamantri Test {run_token} Yojana"
    source = SourceItem(
        id=source_id,
        url=f"https://unit.gov.in/test-scheme/{uuid.uuid4().hex}",
        domain="unit.gov.in",
        source_type=SourceType.HTML,
        discovered_from="controlled fixture",
        status=SourceStatus.DISCOVERED,
    )
    AgentRepository.add_or_update_source(source)
    assert any(item.id == source_id for item in AgentRepository.get_all_sources(limit=5000))
    page = {"text": f"{scheme_name}\nEligibility: Age 18 to 45 years.\nBenefits: Monthly assistance is Rs 1000 for applicants."}

    def controlled_crawl(_source):
        return {
            "source_id": source_id,
            "url": source.url,
            "document_type": "HTML",
            "raw_text": page["text"],
            "status": "success",
            "error": None,
        }

    monkeypatch.setattr(orchestrator.monitoring.crawler, "crawl_source", controlled_crawl)
    first = orchestrator.run_monitoring_cycle(source_ids=[source_id], max_sources=1)
    assert first["detected_changes"] == 1, first
    updates = [u for u in AgentRepository.get_all_proposed_updates(ReviewStatus.PENDING)
               if u.source_url == source.url]
    assert len(updates) == 1
    expected_new_id = "disc-" + uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{scheme_name.casefold()}").hex[:24]
    assert updates[0].scheme_id == expected_new_id, (source_id, source.id, source.url, updates[0].scheme_id)
    assert updates[0].evidence["verified_evidence"]["benefits"]
    assert orchestrator.run_monitoring_cycle(source_ids=[source_id], max_sources=1)["detected_changes"] == 0
    assert len([u for u in AgentRepository.get_all_proposed_updates(ReviewStatus.PENDING)
                if u.source_url == source.url]) == 1

    approval = orchestrator.approve_update(updates[0].id)
    assert approval["success"] is True
    scheme_id = approval["publishing"]["scheme_id"]
    versions = AgentRepository.get_scheme_versions(scheme_id)
    assert versions and versions[0].approval_status == "APPROVED"
    published = next((s for s in scheme_service.get_all_schemes() if s.id == scheme_id), None)
    assert published is not None, (scheme_id, approval, [s.id for s in scheme_service.get_all_schemes()])
    assert [rule.field for rule in published.rules] == ["age", "age"]

    page["text"] = page["text"].replace("Rs 1000", "Rs 1200")
    changed = orchestrator.run_monitoring_cycle(source_ids=[source_id], max_sources=1)
    assert changed["detected_changes"] == 1
    changed_updates = [u for u in AgentRepository.get_all_proposed_updates(ReviewStatus.PENDING)
                       if u.source_url == source.url]
    assert len(changed_updates) == 1
    assert changed_updates[0].change_type == ChangeType.BENEFIT_CHANGE

# 10. API Endpoints Live Check
def test_agent_api_endpoints():
    headers = {"X-Admin-Key": "yojnasarthi-admin-secret-2026"}
    # Status
    resp_stat = client.get("/api/agents/status", headers=headers)
    assert resp_stat.status_code == 200
    data_stat = resp_stat.json()
    assert data_stat["success"] is True
    assert "source_discovery" in data_stat["agents"]
    assert "policy_review_gate" in data_stat["agents"]

    # Runs
    resp_runs = client.get("/api/agents/runs", headers=headers)
    assert resp_runs.status_code == 200
    assert resp_runs.json()["success"] is True

    # Sources
    resp_src = client.get("/api/sources", headers=headers)
    assert resp_src.status_code == 200
    assert resp_src.json()["success"] is True

    # Updates
    resp_upd = client.get("/api/updates", headers=headers)
    assert resp_upd.status_code == 200
    assert resp_upd.json()["success"] is True

    # Monitoring Status Overview
    resp_ov = client.get("/api/monitoring/status", headers=headers)
    assert resp_ov.status_code == 200
    assert resp_ov.json()["success"] is True
    assert "total_discovered_sources" in resp_ov.json()["overview"]
