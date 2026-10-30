import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["schemes_loaded"] >= 5

def test_list_schemes_endpoint():
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 5
    scheme_ids = [s["id"] for s in schemes]
    assert "pm_kisan" in scheme_ids
    assert "mmvy_scholarship" in scheme_ids

def test_single_scheme_endpoint():
    response = client.get("/api/schemes/pm_kisan")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "pm_kisan"
    assert len(data["required_documents"]) >= 3

def test_rules_status_endpoint():
    response = client.get("/api/rules-status")
    assert response.status_code == 200
    data = response.json()
    assert data["total_schemes"] >= 5
    assert data["verified_schemes"] >= 5

def test_next_question_api():
    payload = {
        "profile": {
            "occupation": "farmer"
        }
    }
    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "has_more" in data
    assert data["has_more"] is True
    assert data["question"] is not None

def test_evaluate_api():
    payload = {
        "profile": {
            "age": 48,
            "gender": "male",
            "occupation": "farmer",
            "state": "Madhya Pradesh",
            "landholding_hectares": 1.2,
            "annual_income": 65000.0,
            "is_institutional_landholder": False,
            "holds_constitutional_post": False,
            "has_pucca_house": False,
            "bpl_card_holder": True
        }
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    eligible_ids = [s["scheme_id"] for s in data["eligible"]]
    assert "pm_kisan" in eligible_ids

def test_checklist_api():
    payload = {
        "scheme_ids": ["pm_kisan", "pm_awas_yojana_gramin"]
    }
    response = client.post("/api/checklist", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 3
    # Aadhaar is required by both schemes, verify deduplication
    doc_ids = [d["document_id"] for d in data["documents"]]
    assert len(doc_ids) == len(set(doc_ids)) # No duplicate document IDs!

def test_parse_text_api():
    payload = {
        "text": "मैं 48 साल का किसान हूँ, मध्य प्रदेश में रहता हूँ और मेरे पास 1.5 हेक्टेयर जमीन है।",
        "language": "hi"
    }
    response = client.post("/api/parse-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    extracted = data["extracted_profile"]
    assert extracted.get("occupation") == "farmer"
    assert extracted.get("age") == 48
    assert extracted.get("state") == "Madhya Pradesh"
    assert extracted.get("landholding_hectares") == 1.5
