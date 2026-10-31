import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.services.azure_translator_service import AzureTranslatorService, azure_translator_service

client = TestClient(app)

def test_azure_translator_status_unconfigured():
    """Verify translator status endpoint masks keys and reports unconfigured state accurately."""
    response = client.get("/api/translate/status")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Microsoft Azure AI Translator"
    assert "supported_languages" in data
    lang_codes = [l["code"] for l in data["supported_languages"]]
    assert "en" in lang_codes
    assert "hi" in lang_codes
    assert "bn" in lang_codes
    # Secret protection: verify raw key is never exposed
    assert "YOUR_AZURE_TRANSLATOR_KEY" not in str(data.get("key_status", ""))

def test_azure_translator_identity_translation():
    """Identity translation (source == target) returns immediately without remote API calls."""
    payload = {
        "text": "Pradhan Mantri Awas Yojana",
        "sourceLanguage": "en",
        "targetLanguage": "en"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["translated_text"] == "Pradhan Mantri Awas Yojana"
    assert data["translatedText"] == "Pradhan Mantri Awas Yojana"
    assert data["source_language"] == "en"
    assert data["target_language"] == "en"
    assert data["success"] is True

def test_azure_translator_empty_text():
    """Empty string returns empty string safely."""
    payload = {
        "text": "",
        "sourceLanguage": "en",
        "targetLanguage": "hi"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["translated_text"] == ""
    assert data["success"] is True

def test_azure_translator_unsupported_language_rejection():
    """Unsupported target language raises HTTP 400 Bad Request."""
    payload = {
        "text": "Hello world",
        "sourceLanguage": "en",
        "targetLanguage": "es"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 400
    assert "Unsupported target language 'es'" in response.json()["detail"]

@pytest.mark.parametrize("src,tgt,input_text,expected_translation", [
    ("en", "hi", "You qualify for government schemes.", "आप सरकारी योजनाओं के लिए पात्र हैं।"),
    ("en", "bn", "Official Scheme Eligibility Guide.", "অফিসিয়াল যোজনা যোগ্যতা নির্দেশিকা।"),
    ("hi", "en", "पीएम किसान सम्मान निधि योजना।", "PM Kisan Samman Nidhi Scheme."),
    ("bn", "en", "নাগরিক কল্যাণ ও জনসহায়তা পোর্টাল।", "Citizen Welfare and Public Assistance Portal."),
    ("hi", "bn", "अपनी समग्र परिवार आईडी दर्ज करें।", "আপনার সামগ্র পরিবার আইডি লিখুন।"),
    ("bn", "hi", "প্রয়োজনীয় নথিপত্রের তালিকা।", "आवश्यक दस्तावेजों की सूची।"),
])
def test_azure_translator_all_six_language_pairs(src, tgt, input_text, expected_translation):
    """
    Test all 6 language pairs across English ('en'), Hindi ('hi'), and Bengali ('bn')
    using simulated Azure Cognitive Services REST API v3.0 responses.
    """
    mock_service = AzureTranslatorService()
    mock_service.key = "fake_test_key_azure_12345"
    mock_service.region = "centralindia"
    mock_service.endpoint = "https://api.cognitive.microsofttranslator.com"

    mock_response = httpx.Response(
        status_code=200,
        json=[{
            "detectedLanguage": {"language": src, "score": 1.0},
            "translations": [{"text": expected_translation, "to": tgt}]
        }],
        request=httpx.Request("POST", "https://api.cognitive.microsofttranslator.com/translate")
    )

    with patch.object(azure_translator_service, "key", "fake_test_key_azure_12345"), \
         patch.object(azure_translator_service, "region", "centralindia"), \
         patch.object(azure_translator_service, "endpoint", "https://api.cognitive.microsofttranslator.com"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        
        mock_post.return_value = mock_response

        payload = {
            "text": input_text,
            "sourceLanguage": src,
            "targetLanguage": tgt
        }
        response = client.post("/api/translate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == expected_translation
        assert data["translatedText"] == expected_translation
        assert data["source_language"] == src
        assert data["target_language"] == tgt
        assert data["success"] is True

        # Verify Azure REST API parameters & headers
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["params"]["api-version"] == "3.0"
        assert call_kwargs["params"]["to"] == tgt
        assert call_kwargs["params"]["from"] == src
        assert call_kwargs["headers"]["Ocp-Apim-Subscription-Key"] == "fake_test_key_azure_12345"
        assert call_kwargs["headers"]["Ocp-Apim-Subscription-Region"] == "centralindia"
        assert "X-ClientTraceId" in call_kwargs["headers"]
        assert call_kwargs["json"] == [{"Text": input_text}]

def test_azure_translator_deterministic_caching():
    """Subsequent identical requests are served from the SHA-256 cache."""
    mock_response = httpx.Response(
        status_code=200,
        json=[{"translations": [{"text": "ক্যাশিং পরীক্ষা", "to": "bn"}]}],
        request=httpx.Request("POST", "https://api.cognitive.microsofttranslator.com/translate")
    )

    with patch.object(azure_translator_service, "key", "fake_test_key_azure_12345"), \
         patch.object(azure_translator_service, "region", "centralindia"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        
        mock_post.return_value = mock_response

        payload = {
            "text": "Deterministic Caching Test Query",
            "sourceLanguage": "en",
            "targetLanguage": "bn"
        }
        
        # Call 1: Fetches from mock Azure API
        resp1 = client.post("/api/translate", json=payload)
        assert resp1.status_code == 200
        assert resp1.json()["cached"] is False
        assert mock_post.call_count == 1

        # Call 2: Served directly from cache without hitting external API
        resp2 = client.post("/api/translate", json=payload)
        assert resp2.status_code == 200
        assert resp2.json()["cached"] is True
        assert resp2.json()["service"] == "azure_ai_translator_cache"
        assert resp2.json()["translated_text"] == "ক্যাশিং পরীক্ষা"
        assert mock_post.call_count == 1 # API was not called again!

def test_azure_translator_unconfigured_graceful_handling():
    """When credentials are not configured, system returns clear instructions without crashing."""
    with patch.object(azure_translator_service, "key", ""):
        payload = {
            "text": "Unconfigured state test",
            "sourceLanguage": "en",
            "targetLanguage": "hi"
        }
        response = client.post("/api/translate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "AZURE_TRANSLATOR_KEY" in data["error"]
        assert data["translated_text"] == "Unconfigured state test" # Fallback to original text

def test_azure_translator_auth_error_handling():
    """Simulates HTTP 401 unauthorized and ensures user receives actionable guidance."""
    mock_401 = httpx.Response(
        status_code=401,
        text="Access denied due to invalid subscription key or region.",
        request=httpx.Request("POST", "https://api.cognitive.microsofttranslator.com/translate")
    )
    with patch.object(azure_translator_service, "key", "invalid_key"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_401

        payload = {
            "text": "Authorization failure test",
            "sourceLanguage": "en",
            "targetLanguage": "hi"
        }
        response = client.post("/api/translate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "authorization failed" in data["error"]

def test_integrations_status_includes_azure_translator():
    """Verify /api/integrations/status includes Azure AI Translator status."""
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    assert "azure_translator" in data
    assert data["azure_translator"]["name"] == "Microsoft Azure AI Translator"
    assert "supported_languages" in data["azure_translator"]
