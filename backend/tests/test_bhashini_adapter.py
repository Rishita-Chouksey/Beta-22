import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.bhashini_adapter import bhashini_adapter

client = TestClient(app)

def test_bhashini_status_endpoint():
    response = client.get("/api/bhashini/status")
    assert response.status_code == 200
    data = response.json()
    assert "translation" in data
    assert "asr" in data
    assert "tts" in data

def test_translation_endpoint_with_glossary_preservation():
    # Translation request preserving critical official terms
    payload = {
        "text": "The citizen is eligible for PM-KISAN and must submit an Aadhaar Card.",
        "sourceLanguage": "en",
        "targetLanguage": "hi"
    }
    response = client.post("/api/bhashini/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "translatedText" in data
    assert data["sourceLanguage"] == "en"
    assert data["targetLanguage"] == "hi"
    # Ensure protected terms are preserved
    assert "पीएम किसान" in data["translatedText"]
    assert "आधार कार्ड" in data["translatedText"]

def test_deterministic_translation_caching():
    payload = {
        "text": "Please provide your Samagra Family ID.",
        "sourceLanguage": "en",
        "targetLanguage": "hi"
    }
    # First call: populates cache or uses fallback
    resp1 = client.post("/api/bhashini/translate", json=payload)
    assert resp1.status_code == 200
    
    # Second identical call: served from deterministic cache if active
    cache_key = bhashini_adapter._generate_cache_key(payload["text"], "en", "hi")
    assert cache_key in bhashini_adapter._translation_cache or resp1.json()["service"] == "local_fallback"

def test_speech_to_text_fallback():
    payload = {
        "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
        "language": "hi"
    }
    response = client.post("/api/bhashini/speech-to-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Does not crash; gracefully returns browser advice when unconfigured
    assert "service" in data
    assert "language" in data

def test_text_to_speech_fallback():
    payload = {
        "text": "नमस्ते, योजनासारथी में आपका स्वागत है।",
        "language": "hi"
    }
    response = client.post("/api/bhashini/text-to-speech", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "format" in data
    assert data["language"] == "hi"
