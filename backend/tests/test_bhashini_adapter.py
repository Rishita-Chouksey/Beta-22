import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_bhashini_status_endpoint():
    """Verify Bhashini voice assistance endpoint reports ASR and TTS."""
    response = client.get("/api/bhashini/status")
    assert response.status_code == 200
    data = response.json()
    assert "asr" in data
    assert "tts" in data
    # Translation is exclusively handled by Azure AI Translator
    assert "translation" not in data

def test_speech_to_text_fallback():
    """Verify speech-to-text fallback when Bhashini is unconfigured."""
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
    """Verify text-to-speech fallback when Bhashini is unconfigured."""
    payload = {
        "text": "नमस्ते, योजनासारथी में आपका स्वागत है।",
        "language": "hi"
    }
    response = client.post("/api/bhashini/text-to-speech", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "format" in data
    assert data["language"] == "hi"
