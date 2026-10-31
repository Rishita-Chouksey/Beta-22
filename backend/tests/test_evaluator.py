import pytest
from app.models.profile import CitizenProfile
from app.models.scheme import SchemeDefinition, SchemeRule
from app.engine.evaluator import evaluate_scheme, evaluate_all_schemes

@pytest.fixture
def sample_verified_scheme():
    return SchemeDefinition(
        id="test_scheme",
        name_en="Test Youth Scheme",
        name_hi="परीक्षण युवा योजना",
        level="central",
        applicable_states=["ALL"],
        category="Youth",
        benefit_en="Test Benefit",
        benefit_hi="परीक्षण लाभ",
        description_en="Test Description",
        description_hi="परीक्षण विवरण",
        rules=[
            SchemeRule(
                field="age",
                operator="between",
                value=[18, 35],
                description_en="Age between 18 and 35",
                description_hi="आयु 18 से 35"
            ),
            SchemeRule(
                field="annual_income",
                operator="lte",
                value=300000.0,
                description_en="Income <= 3 Lakhs",
                description_hi="आय <= 3 लाख"
            )
        ],
        required_documents=[],
        application_procedure=[],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-15",
        max_allowed_age_days=180,
        verification_status="verified"
    )

def test_scheme_evaluation_eligible(sample_verified_scheme):
    profile = CitizenProfile(age=24, annual_income=180000.0)
    result = evaluate_scheme(sample_verified_scheme, profile)
    assert result.status == "ELIGIBLE"
    assert len(result.missing_fields) == 0

def test_scheme_evaluation_not_eligible(sample_verified_scheme):
    profile = CitizenProfile(age=40, annual_income=180000.0)
    result = evaluate_scheme(sample_verified_scheme, profile)
    assert result.status == "NOT ELIGIBLE"
    assert "outside eligible range" in result.deciding_reason_en

def test_scheme_evaluation_not_sure_due_to_missing_field(sample_verified_scheme):
    profile = CitizenProfile(age=24) # annual_income missing
    result = evaluate_scheme(sample_verified_scheme, profile)
    assert result.status == "NOT SURE"
    assert "annual_income" in result.missing_fields

def test_scheme_evaluation_stale_or_unverified():
    stale_scheme = SchemeDefinition(
        id="stale_scheme",
        name_en="Outdated Scheme",
        name_hi="पुरानी योजना",
        level="central",
        applicable_states=["ALL"],
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        rules=[SchemeRule(field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        required_documents=[],
        application_procedure=[],
        official_source_url="https://test.gov.in",
        last_verified_date="2022-01-01", # Stale > 180 days
        max_allowed_age_days=180,
        verification_status="verified"
    )
    profile = CitizenProfile(age=25)
    result = evaluate_scheme(stale_scheme, profile)
    assert result.status == "NO CURRENT RULES"

def test_state_filtering_rejection():
    state_scheme = SchemeDefinition(
        id="mp_scheme",
        name_en="MP Specific Scheme",
        name_hi="मध्य प्रदेश योजना",
        level="state",
        applicable_states=["Madhya Pradesh"],
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        rules=[SchemeRule(field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        required_documents=[],
        application_procedure=[],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-15",
        max_allowed_age_days=180,
        verification_status="verified"
    )
    # Resident of Maharashtra applying for MP scheme
    profile = CitizenProfile(age=25, state="Maharashtra")
    result = evaluate_scheme(state_scheme, profile)
    assert result.status == "NOT ELIGIBLE"
    assert "Not applicable in Maharashtra" in result.deciding_reason_en
