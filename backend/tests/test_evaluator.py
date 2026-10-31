import pytest
from app.models.profile import CitizenProfile
from app.models.scheme import SchemeDefinition, SchemeRule, AutoUpdateRecord, AutoUpdateChange
from app.engine.evaluator import evaluate_scheme, evaluate_all_schemes

@pytest.fixture
def sample_verified_scheme():
    return SchemeDefinition(
        id="test_scheme",
        name_en="Test Youth Scheme",
        name_hi="परीक्षण युवा योजना",
        name_bn="পরীক্ষামূলক যুব প্রকল্প",
        level="central",
        state=None,
        applicable_states=["ALL"],
        category="Youth",
        benefit_en="Test Benefit",
        benefit_hi="परीक्षण लाभ",
        benefit_bn="পরীক্ষামূলক সুবিধা",
        description_en="Test Description",
        description_hi="परीक्षण विवरण",
        description_bn="পরীক্ষামূলক বিবরণ",
        review_status="verified",
        verified_by=["Tester 1", "Tester 2"],
        rules=[
            SchemeRule(
                rule_id="age_rule",
                field="age",
                operator="between",
                value=[18, 35],
                description_en="Age between 18 and 35",
                description_hi="आयु 18 से 35",
                description_bn="বয়স ১৮ থেকে ৩৫",
                why_template={"en": "Age must be between {value}.", "hi": "आयु {value} होनी चाहिए।", "bn": "বয়স {value} হতে হবে।"}
            ),
            SchemeRule(
                rule_id="income_rule",
                field="annual_income",
                operator="lte",
                value=300000.0,
                description_en="Income <= 3 Lakhs",
                description_hi="आय <= 3 लाख",
                description_bn="আয় <= ৩ লক্ষ",
                why_template={"en": "Income <= {value}", "hi": "आय <= {value}", "bn": "আয় <= {value}"}
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
        state=None,
        applicable_states=["ALL"],
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        review_status="verified",
        verified_by=["Reviewer 1", "Reviewer 2"],
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
        state="MP",
        applicable_states=["MP"],
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        review_status="verified",
        verified_by=["Reviewer 1", "Reviewer 2"],
        rules=[SchemeRule(field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        required_documents=[],
        application_procedure=[],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-15",
        max_allowed_age_days=180,
        verification_status="verified"
    )
    # Resident of MH applying for MP scheme
    profile = CitizenProfile(age=25, state="Maharashtra")
    result = evaluate_scheme(state_scheme, profile)
    assert result.status == "NOT ELIGIBLE"
    assert "MP" in result.deciding_reason_en

def test_state_filtering_unknown_state():
    state_scheme = SchemeDefinition(
        id="mp_scheme",
        name_en="MP Specific Scheme",
        name_hi="मध्य प्रदेश योजना",
        level="state",
        state="MP",
        applicable_states=["MP"],
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        review_status="verified",
        verified_by=["Reviewer 1", "Reviewer 2"],
        rules=[SchemeRule(field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        required_documents=[],
        application_procedure=[],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-15",
        max_allowed_age_days=180,
        verification_status="verified"
    )
    # Missing state gives NOT SURE with state in missing_fields
    profile = CitizenProfile(age=25, state=None)
    result = evaluate_scheme(state_scheme, profile)
    assert result.status == "NOT SURE"
    assert "state" in result.missing_fields

def test_review_status_draft_and_needs_review():
    draft_scheme = SchemeDefinition(
        id="draft_scheme",
        name_en="Draft Scheme",
        name_hi="प्रारूप योजना",
        level="central",
        state=None,
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        review_status="draft",
        verified_by=[],
        rules=[SchemeRule(field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-15"
    )
    profile = CitizenProfile(age=25)
    res_draft = evaluate_scheme(draft_scheme, profile)
    assert res_draft.status == "NO CURRENT RULES"

def test_auto_updated_scheme_evaluation():
    auto_scheme = SchemeDefinition(
        id="auto_scheme",
        name_en="Auto Updated Scheme",
        name_hi="स्वचालित अद्यतन योजना",
        level="central",
        state=None,
        category="General",
        benefit_en="Test",
        benefit_hi="परीक्षण",
        description_en="Test",
        description_hi="परीक्षण",
        review_status="auto_updated",
        verified_by=[],
        auto_update=AutoUpdateRecord(
            applied_at="2026-10-31T12:00:00Z",
            run_id="run-101",
            changes=[
                AutoUpdateChange(
                    rule_id="age_rule",
                    field="age",
                    old=21,
                    new=18,
                    evidence_url="https://test.gov.in",
                    evidence_snippet="Applicant must be at least 18 years old"
                )
            ],
            checkers_agreed=True
        ),
        rules=[SchemeRule(rule_id="age_rule", field="age", operator="gte", value=18, description_en="Adult", description_hi="वयस्क")],
        official_source_url="https://test.gov.in",
        last_verified_date="2026-10-31"
    )
    profile = CitizenProfile(age=25)
    res = evaluate_scheme(auto_scheme, profile)
    assert res.status == "ELIGIBLE"
    assert res.review_status == "auto_updated"
