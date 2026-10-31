import pytest
import json
from unittest.mock import MagicMock
from updater.ai_checker import AIChecker

def test_ai_checker_valid_extraction():
    fake_client = MagicMock()
    mock_resp = MagicMock()
    page_text = "The official annual income limit for MMVY is ₹6,00,000 per family."
    
    mock_resp.text = json.dumps({
        "found": True,
        "value": 600000.0,
        "unit": "INR",
        "evidence_snippet": "annual income limit for MMVY is ₹6,00,000 per family.",
        "reasoning": "Explicit annual family income limit mentioned."
    })
    fake_client.models.generate_content.return_value = mock_resp

    checker = AIChecker(client=fake_client)
    res = checker.check("annual_income", "income_limit", page_text)

    assert res.value == 600000.0
    assert res.unit == "INR"
    assert res.confidence == 1.0
    assert res.evidence_snippet in page_text

def test_ai_checker_rejects_hallucinated_evidence():
    fake_client = MagicMock()
    mock_resp = MagicMock()
    page_text = "The scheme offers health insurance up to 5 lakh rupees."
    
    # Model returns an evidence snippet that is NOT in page_text
    mock_resp.text = json.dumps({
        "found": True,
        "value": 500000.0,
        "unit": "INR",
        "evidence_snippet": "The government strictly guarantees 5 lakh rupees for everyone.",
        "reasoning": "Extracted from header."
    })
    fake_client.models.generate_content.return_value = mock_resp

    checker = AIChecker(client=fake_client)
    res = checker.check("benefit_amount", "amount_inr", page_text)

    # Must be rejected because evidence snippet was hallucinated!
    assert res.value is None
    assert res.confidence == 0.0
    assert res.raw_match == "hallucinated_evidence"

def test_ai_checker_handles_not_found():
    fake_client = MagicMock()
    mock_resp = MagicMock()
    page_text = "Welcome to the official portal. Please login with your credentials."
    
    mock_resp.text = json.dumps({
        "found": False,
        "value": None,
        "unit": None,
        "evidence_snippet": None,
        "reasoning": "No income limit stated."
    })
    fake_client.models.generate_content.return_value = mock_resp

    checker = AIChecker(client=fake_client)
    res = checker.check("annual_income", "income_limit", page_text)
    assert res.value is None
    assert res.confidence == 0.0

def test_ai_checker_without_api_key_returns_ai_unavailable():
    checker = AIChecker(api_key="")
    res = checker.check("annual_income", "income_limit", "some page text")
    assert res.value is None
    assert res.raw_match == "ai_unavailable"
