import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.sarvam_service import sarvam_service

client = TestClient(app)

def test_sarvam_status():
    stat = sarvam_service.get_status()
    assert "name" in stat
    assert "Sarvam AI" in stat["name"]
    assert "status" in stat
    assert "supported_languages" in stat
    assert any(lang["code"] == "hi" for lang in stat["supported_languages"])
    assert any(lang["code"] == "bn" for lang in stat["supported_languages"])

def test_translate_status_endpoint():
    response = client.get("/api/translate/status")
    assert response.status_code == 200
    data = response.json()
    assert "sarvam_ai" in data
    assert "active_primary_service" in data
    assert "supported_languages" in data

def test_translation_endpoint_fallback():
    payload = {
        "text": "The citizen is eligible for PM-KISAN and must submit an Aadhaar Card.",
        "sourceLanguage": "en",
        "targetLanguage": "hi"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert data["source_language"] == "en"
    assert data["target_language"] == "hi"

def test_translation_bengali():
    payload = {
        "text": "Hello, welcome to YojnaSarthi.",
        "sourceLanguage": "en",
        "targetLanguage": "bn"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_language"] == "bn"

def test_integrations_status_includes_sarvam():
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    assert "sarvam_ai" in data
    assert data["sarvam_ai"]["name"] == "Sarvam AI (Indic Language Engine)"

@pytest.mark.anyio
async def test_sarvam_caching():
    test_text = "Checking in-memory cache functionality"
    cache_key = sarvam_service._generate_cache_key(test_text, "en", "hi")
    
    # Pre-populate cache
    sarvam_service._cache[cache_key] = {
        "target": "परीक्षण अनुवाद परिणाम",
        "timestamp": 9999999999.0
    }
    
    res = await sarvam_service.translate(test_text, "en", "hi")
    assert res["cached"] is True
    assert res["translated_text"] == "परीक्षण अनुवाद परिणाम"
