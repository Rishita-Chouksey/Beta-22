import pytest
from app.services.myscheme_adapter import myscheme_adapter, MySchemeAPIService

def test_myscheme_adapter_unconfigured_state():
    adapter = MySchemeAPIService()
    status = adapter.get_status()
    # Live credentials are not present, must cleanly report awaiting/disabled state without pretending to be live
    assert status.status in ["disabled", "configured_awaiting_credentials"]
    assert status.is_live_api is False
    assert status.active_data_source == "local_fallback_catalog"
    assert len(status.access_requirements) > 0

def test_myscheme_normalization_handles_missing_fields():
    adapter = MySchemeAPIService()
    raw_api_payload = {
        "scheme_id": "test_crop_grant",
        "scheme_name": "Test Crop Grant Scheme",
        "level": "Central",
        "category": "Agriculture",
        "benefits": "₹10,000 per year assistance",
        # Missing documents, rules, procedures
    }
    
    normalized = adapter.normalize_myscheme_to_internal(raw_api_payload)
    assert normalized.id == "test_crop_grant"
    assert normalized.name_en == "Test Crop Grant Scheme"
    assert normalized.level == "central"
    assert normalized.benefit_en == "₹10,000 per year assistance"
    assert normalized.official_source_url == "https://myscheme.gov.in/"
    assert normalized.verification_status == "verified"
    # Doesn't silently crash on missing fields
    assert isinstance(normalized.rules, list)
    assert isinstance(normalized.required_documents, list)

def test_myscheme_normalization_with_full_criteria():
    adapter = MySchemeAPIService()
    raw_payload = {
        "id": "solar_pump_scheme",
        "name_en": "Pradhan Mantri Solar Pump Yojana",
        "name_hi": "प्रधानमंत्री सोलर पंप योजना",
        "level": "central",
        "category": "Agriculture",
        "benefit_en": "Up to 60% subsidy on solar water pumping systems.",
        "benefit_hi": "सोलर पंप सिस्टम पर 60% तक अनुदान।",
        "rules": [
            {
                "field": "occupation",
                "operator": "eq",
                "value": "farmer",
                "description_en": "Must be an active cultivator farmer.",
                "description_hi": "सक्रिय किसान होना चाहिए।"
            }
        ],
        "required_documents": [
            {
                "id": "land_record",
                "name_en": "Land Ownership Record",
                "purpose_en": "Verification of agricultural land."
            }
        ],
        "official_source_url": "https://pmkusum.mnre.gov.in/"
    }

    normalized = adapter.normalize_myscheme_to_internal(raw_payload)
    assert normalized.id == "solar_pump_scheme"
    assert len(normalized.rules) == 1
    assert normalized.rules[0].field == "occupation"
    assert len(normalized.required_documents) == 1
    assert normalized.required_documents[0].id == "land_record"
    assert normalized.official_source_url == "https://pmkusum.mnre.gov.in/"
