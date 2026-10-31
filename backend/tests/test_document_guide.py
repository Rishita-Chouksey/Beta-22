import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service

client = TestClient(app)

def test_list_all_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 11
    
    doc_ids = [d["id"] for d in docs]
    assert "income_certificate" in doc_ids
    assert "domicile_certificate" in doc_ids
    assert "caste_certificate" in doc_ids
    assert "aadhaar" in doc_ids
    assert "bank_passbook" in doc_ids
    assert "birth_certificate" in doc_ids
    assert "ration_card" in doc_ids
    assert "land_record" in doc_ids
    assert "death_certificate" in doc_ids
    assert "disability_certificate" in doc_ids
    assert "samagra_id" in doc_ids

def test_search_and_filter_documents():
    # Search by keyword
    response = client.get("/api/documents?query=income")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("Income Certificate" in d["name_en"] for d in results)

    # Search in Hindi
    response_hi = client.get("/api/documents?query=आय")
    assert response_hi.status_code == 200
    results_hi = response_hi.json()
    assert len(results_hi) >= 1

    # Filter by category
    response_cat = client.get("/api/documents?category=Identity")
    assert response_cat.status_code == 200
    results_cat = response_cat.json()
    assert len(results_cat) >= 1
    for d in results_cat:
        assert d["category"].lower() == "identity"

def test_get_document_details_and_synthetic_sample():
    response = client.get("/api/documents/income_certificate")
    assert response.status_code == 200
    doc = response.json()
    
    assert doc["id"] == "income_certificate"
    assert "आय प्रमाण पत्र" in doc["name_hi"]
    assert doc["why_schemes_ask_en"]
    assert doc["why_schemes_ask_hi"]
    assert doc["issuer_en"]
    assert len(doc["contents_en"]) > 0
    assert len(doc["required_for_application_en"]) > 0
    assert len(doc["application_steps_en"]) > 0
    assert doc["apply_url"] == "https://mpedistrict.gov.in/"
    
    # Verify synthetic sample requirements
    sample = doc["sample_preview"]
    assert sample["holder_name"] == "JOHN DOE"
    assert "ILLUSTRATIVE SAMPLE — NOT AN OFFICIAL DOCUMENT" in sample["watermark_text"]
    assert "disclaimer_en" in sample
    assert "disclaimer_hi" in sample

def test_alias_resolution_from_scheme_checklists():
    # mp_domicile should resolve to domicile_certificate
    resp_mp = client.get("/api/documents/mp_domicile")
    assert resp_mp.status_code == 200
    assert resp_mp.json()["id"] == "domicile_certificate"

    # income_cert should resolve to income_certificate
    resp_inc = client.get("/api/documents/income_cert")
    assert resp_inc.status_code == 200
    assert resp_inc.json()["id"] == "income_certificate"

    # death_certificate_husband should resolve to death_certificate
    resp_dth = client.get("/api/documents/death_certificate_husband")
    assert resp_dth.status_code == 200
    assert resp_dth.json()["id"] == "death_certificate"

def test_unknown_document_returns_404():
    response = client.get("/api/documents/non_existent_fake_doc")
    assert response.status_code == 404
