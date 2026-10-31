import pytest
from updater.rules_checker import (
    parse_indian_number,
    RulesChecker,
    CheckerResult
)

def test_parse_indian_number():
    assert parse_indian_number("₹6,000") == 6000.0
    assert parse_indian_number("₹6,00,000") == 600000.0
    assert parse_indian_number("Rs. 2.5 lakh") == 250000.0
    assert parse_indian_number("2.5 लाख") == 250000.0
    assert parse_indian_number("1.2 crore") == 12000000.0
    assert parse_indian_number("50 thousand") == 50000.0
    assert parse_indian_number("invalid") is None

def test_extract_income_limit_english_and_hindi():
    checker = RulesChecker()

    text_en = (
        "Eligibility Guidelines:\n"
        "Total family annual income must not exceed ₹6,00,000 from all sources.\n"
        "Applicant must be a permanent resident."
    )
    res_en = checker.check("income_limit", text_en)
    assert res_en.value == 600000.0
    assert res_en.unit == "INR"
    assert "₹6,00,000" in res_en.evidence_snippet
    assert res_en.evidence_snippet in text_en

    text_hi = (
        "पात्रता की शर्तें:\n"
        "आवेदक के परिवार की कुल वार्षिक आय ₹2.5 लाख से अधिक नहीं होनी चाहिए।\n"
    )
    res_hi = checker.check("income_limit", text_hi)
    assert res_hi.value == 250000.0
    assert res_hi.evidence_snippet in text_hi

def test_extract_benefit_amount():
    checker = RulesChecker()
    text = (
        "Under PM-KISAN scheme, eligible landholding farmer families will receive "
        "a financial benefit of ₹6,000 per year in three equal installments."
    )
    res = checker.check("amount_inr", text)
    assert res.value == 6000.0
    assert res.evidence_snippet in text

def test_extract_age_range():
    checker = RulesChecker()
    text_range = "The applicant woman must be of age between 21 and 60 years at the time of application."
    res_range = checker.check("age_range", text_range)
    assert res_range.value == {"min_age": 21, "max_age": 60}
    assert res_range.evidence_snippet in text_range

    text_min = "Eligible widows must be of age 40 years and above."
    res_min = checker.check("age_range", text_min)
    assert res_min.value == {"min_age": 40, "max_age": None}
    assert res_min.evidence_snippet in text_min

def test_extract_land_area_and_conversion():
    checker = RulesChecker()
    text_ha = "The maximum agricultural landholding allowed is 2.5 hectares."
    res_ha = checker.check("land_area", text_ha)
    assert res_ha.value == 2.5
    assert res_ha.unit == "hectares"

    text_acre = "Applicant family must not own more than 5 acres of land."
    res_acre = checker.check("land_area", text_acre)
    # 5 acres * 0.404686 = 2.02 hectares
    assert res_acre.value == 2.02
    assert res_acre.unit == "hectares"

def test_ambiguous_conflicting_numbers_return_none():
    checker = RulesChecker()
    # Conflicting income limits on same page
    ambiguous_text = (
        "Criteria A: Family annual income limit is ₹2,00,000.\n"
        "Criteria B: Annual income must not exceed ₹5,00,000."
    )
    res = checker.check("income_limit", ambiguous_text)
    assert res.value is None
    assert res.confidence == 0.0
