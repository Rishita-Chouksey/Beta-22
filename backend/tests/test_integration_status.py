import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_integration_status_endpoint():
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    
    # Check all active systems are reported
    assert "myscheme" in data
    assert "translator" in data
    assert "voice_engine" in data
    assert "eligibility_engine" in data
    assert "document_guide" in data

    # Check status values
<<<<<<< HEAD
    assert data["myscheme"]["status"] == "manual_catalog"
    assert data["myscheme"]["automated_scraping"] is False
    assert data["translator"]["is_external_api"] is False
    assert data["translator"]["status"] in ["active", "models_not_installed"]
=======
    assert data["myscheme"]["status"] in ["active", "configured_awaiting_credentials", "disabled", "failed"]
    assert data["azure_translator"]["status"] in ["active", "configured_awaiting_credentials"]
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
    assert data["voice_engine"]["status"] == "active"
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
