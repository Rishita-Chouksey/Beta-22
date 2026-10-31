import pytest
from tests.test_client import ApiTestClient
from app.main import app

client = ApiTestClient(app)

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

def test_chat_helpdesk_direct_scheme_query():
    # User asks "What is MMVY?" - must not return generic welcome message
    payload = {
        "message": "What is MMVY?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "Mukhyamantri Medhavi Vidyarthi Yojana" in reply or "MMVY" in reply
    assert "Welcome to YojnaSarthi! How can I help you today?" not in reply

def test_chat_helpdesk_follow_up_with_history():
    # User asks a follow-up referring to previous context
    history = [
        {"role": "user", "text": "What is MMVY?"},
        {"role": "assistant", "text": "Mukhyamantri Medhavi Vidyarthi Yojana (MMVY) is a flagship scholarship in Madhya Pradesh."}
    ]
    payload = {
        "message": "What documents are required for it?",
        "language": "en",
        "history": history
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert ("marksheet" in reply.lower() or "samagra" in reply.lower() or "aadhaar" in reply.lower() or "domicile" in reply.lower() or "document" in reply.lower())

def test_chat_helpdesk_profile_eligibility_query():
    # User asks "I am 29 years old and a widow. Which schemes can I apply for?"
    payload = {
        "message": "I am 29 years old and a widow. Which schemes can I apply for?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "Ladli Behna" in reply or "Sanjay Gandhi" in reply or "pension" in reply.lower()
    # Must note MMVY ineligibility
    assert "MMVY" in reply

def test_chat_helpdesk_widow_schemes_discovery():
    # User asks "Are there any government schemes for widows?"
    payload = {
        "message": "Are there any government schemes for widows?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "Ladli Behna" in reply or "Widow" in reply or "Sanjay Gandhi" in reply

def test_chat_helpdesk_student_financial_assistance():
    # User asks "I am a college student. What financial assistance can I get?"
    payload = {
        "message": "I am a college student. What financial assistance can I get?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "MMVY" in reply or "scholarship" in reply.lower()

def test_chat_helpdesk_farmer_schemes_discovery():
    # User asks "Which schemes are available for farmers?"
    payload = {
        "message": "Which schemes are available for farmers?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "PM-KISAN" in reply or "PMAY" in reply or "farmer" in reply.lower()

def test_chat_helpdesk_income_limit_query():
    # User asks "Can I apply if my family income is ₹3 lakh?"
    payload = {
        "message": "Can I apply if my family income is ₹3 lakh?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "MMVY" in reply and "6,00,000" in reply

def test_chat_helpdesk_dual_scholarship_restriction():
    # User asks "Can I receive two scholarships simultaneously?"
    payload = {
        "message": "Can I receive two scholarships simultaneously?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "NO" in reply or "not draw" in reply.lower() or "cannot" in reply.lower()

def test_chat_helpdesk_income_certificate_document():
    # User asks "How can I get an income certificate?"
    payload = {
        "message": "How can I get an income certificate?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "Income Certificate" in reply or "mpedistrict" in reply or "Tehsildar" in reply

def test_chat_helpdesk_bank_passbook_compulsory():
    # User asks "Is a bank passbook compulsory?"
    payload = {
        "message": "Is a bank passbook compulsory?",
        "language": "en",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "Passbook" in reply or "DBT" in reply or "NPCI" in reply

def test_chat_helpdesk_hindi_manual_question():
    # User asks in Hindi "क्या दो छात्रवृत्ति एक साथ मिल सकती हैं?"
    payload = {
        "message": "क्या दो छात्रवृत्ति एक साथ मिल सकती हैं?",
        "language": "hi",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    reply = data["reply"]
    assert "नहीं" in reply and "छात्रवृत्ति" in reply

def test_feedback_api():
    # Citizen submits anonymous feedback
    payload = {
        "scheme_id": "mmvy_scholarship",
        "rating": 5,
        "is_helpful": True,
        "comment": "Very clear and helpful guidance on MMVY.",
        "language": "en"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_security_headers_and_database_status():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"


