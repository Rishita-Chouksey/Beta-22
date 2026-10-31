import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_integration_status_endpoint():
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    
    # Check all systems are reported
    assert "myscheme" in data
    assert "azure_translator" in data
    assert "bhashini_asr" in data
    assert "bhashini_tts" in data
    assert "eligibility_engine" in data
    assert "document_guide" in data

    # Check status values
    assert data["myscheme"]["status"] in ["active", "configured_awaiting_credentials", "disabled", "failed"]
    assert data["azure_translator"]["status"] in ["active", "configured_awaiting_credentials"]
    assert data["eligibility_engine"]["status"] == "active"
    assert data["document_guide"]["status"] == "active"
    assert data["document_guide"]["documents_cataloged"] >= 11

def test_health_check_reflects_data_source_and_documents():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_data_source" in data
    assert data["document_guide_items"] >= 11
