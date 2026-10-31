import pytest
from app.services.scheme_service import scheme_service
from app.models.profile import CitizenProfile
from app.engine.evaluator import evaluate_all_schemes, evaluate_scheme, detect_profile_contradictions

@pytest.fixture(autouse=True)
def load_all_schemes():
    scheme_service.load_schemes()

def test_persona_29_year_old_widow_not_eligible_for_mmvy():
    """
    Critical requirement:
    A 29-year-old widow must NEVER receive an MMVY recommendation merely because
    she is a student or satisfies some unrelated profile conditions.
    MMVY is restricted to dependent unmarried youth directly entering higher education.
    She may however be eligible for Ladli Behna (if residing in MP with income <= 2.5L).
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        age=29,
        gender="female",
        marital_status="widow",
        occupation="student",
        state="Madhya Pradesh",
        annual_income=24000.0,
        landholding_hectares=0.0,
        student_class12_marks_percent=88.0,
        enrolled_higher_education=True,
        confirmed_fields=[
            "age", "gender", "marital_status", "occupation", "state",
            "annual_income", "landholding_hectares", "student_class12_marks_percent", "enrolled_higher_education"
        ]
    )
    result = evaluate_all_schemes(schemes, profile)
    
    eligible_ids = [s.scheme_id for s in result.eligible]
    not_eligible_ids = [s.scheme_id for s in result.not_eligible]

    # Must NOT be eligible for MMVY
    assert "mmvy_scholarship" not in eligible_ids
    assert "mmvy_scholarship" in not_eligible_ids

    # Find MMVY result and verify the deciding reason mentions marital status/dependent student criteria
    mmvy_res = next(s for s in result.not_eligible if s.scheme_id == "mmvy_scholarship")
    assert any("widow" in reason.lower() or "unmarried" in reason.lower() for reason in mmvy_res.failed_conditions)

    # Must be eligible for Ladli Behna (age 21-60, female, MP resident, income <= 2.5L, land <= 2.02ha)
    assert "ladli_behna_mp" in eligible_ids

    # Must NOT be eligible for central widow pension IGNWPS (requires age 40 to 79)
    assert "ignwps_widow_pension" in not_eligible_ids
    ignwps_res = next(s for s in result.not_eligible if s.scheme_id == "ignwps_widow_pension")
    assert any("40" in reason or "age" in reason.lower() for reason in ignwps_res.failed_conditions)

def test_eligible_college_going_student():
    """
    Eligible college-going student in Madhya Pradesh:
    19-year-old unmarried female student, 86% in 12th board, enrolled in higher education, income 4.5L.
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        age=19,
        gender="female",
        marital_status="single",
        occupation="student",
        state="Madhya Pradesh",
        student_class12_marks_percent=86.0,
        enrolled_higher_education=True,
        annual_income=450000.0,
        confirmed_fields=[
            "age", "gender", "marital_status", "occupation", "state",
            "student_class12_marks_percent", "enrolled_higher_education", "annual_income"
        ]
    )
    result = evaluate_all_schemes(schemes, profile)
    eligible_ids = [s.scheme_id for s in result.eligible]
    assert "mmvy_scholarship" in eligible_ids
    mmvy_res = next(s for s in result.eligible if s.scheme_id == "mmvy_scholarship")
    assert mmvy_res.status == "ELIGIBLE"
    assert len(mmvy_res.satisfied_conditions) >= 4

def test_ineligible_student():
    """
    Student with low Class 12 marks (55% < 70%) or income exceeding limit (> 6 Lakhs).
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        age=19,
        gender="male",
        marital_status="single",
        occupation="student",
        state="Madhya Pradesh",
        student_class12_marks_percent=55.0, # Fails merit criterion
        enrolled_higher_education=True,
        annual_income=700000.0, # Fails income criterion
        confirmed_fields=[
            "age", "gender", "marital_status", "occupation", "state",
            "student_class12_marks_percent", "enrolled_higher_education", "annual_income"
        ]
    )
    result = evaluate_all_schemes(schemes, profile)
    not_eligible_ids = [s.scheme_id for s in result.not_eligible]
    assert "mmvy_scholarship" in not_eligible_ids
    mmvy_res = next(s for s in result.not_eligible if s.scheme_id == "mmvy_scholarship")
    assert len(mmvy_res.failed_conditions) >= 1

def test_rural_farmer():
    """
    Rural smallholder farmer: 48-year-old, MP, 1.5 hectares land, non-institutional landholder, no govt post.
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        age=48,
        gender="male",
        marital_status="married",
        occupation="farmer",
        state="Madhya Pradesh",
        residence_type="rural",
        landholding_hectares=1.5,
        annual_income=65000.0,
        is_institutional_landholder=False,
        holds_constitutional_post=False,
        has_pucca_house=False,
        bpl_card_holder=True,
        confirmed_fields=[
            "age", "gender", "marital_status", "occupation", "state",
            "residence_type", "landholding_hectares", "annual_income",
            "is_institutional_landholder", "holds_constitutional_post",
            "has_pucca_house", "bpl_card_holder"
        ]
    )
    result = evaluate_all_schemes(schemes, profile)
    eligible_ids = [s.scheme_id for s in result.eligible]
    assert "pm_kisan" in eligible_ids
    assert "pm_awas_yojana_gramin" in eligible_ids
    assert "mmvy_scholarship" not in eligible_ids

def test_low_income_household():
    """
    Low income family with annual income below ₹2,00,000 in rural area without pucca house.
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        residence_type="rural",
        has_pucca_house=False,
        annual_income=85000.0,
        holds_constitutional_post=False,
        confirmed_fields=["residence_type", "has_pucca_house", "annual_income", "holds_constitutional_post"]
    )
    result = evaluate_all_schemes(schemes, profile)
    eligible_ids = [s.scheme_id for s in result.eligible]
    assert "pm_awas_yojana_gramin" in eligible_ids
    assert "pm_jay_ayushman" in eligible_ids

def test_user_with_unknown_income():
    """
    When income is unknown/missing, schemes with income ceilings must return NOT SURE (Needs verification),
    NEVER ELIGIBLE.
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        residence_type="rural",
        has_pucca_house=False,
        annual_income=None, # Missing income!
        confirmed_fields=["residence_type", "has_pucca_house"]
    )
    result = evaluate_all_schemes(schemes, profile)
    eligible_ids = [s.scheme_id for s in result.eligible]
    not_sure_ids = [s.scheme_id for s in result.not_sure]

    assert "pm_awas_yojana_gramin" not in eligible_ids
    assert "pm_awas_yojana_gramin" in not_sure_ids
    pmay_res = next(s for s in result.not_sure if s.scheme_id == "pm_awas_yojana_gramin")
    assert "annual_income" in pmay_res.missing_fields

def test_user_with_missing_marital_status():
    """
    Widow pension scheme requires marital status. If missing, it must evaluate to NOT SURE, not ELIGIBLE.
    """
    ignwps = scheme_service.get_scheme_by_id("ignwps_widow_pension")
    profile = CitizenProfile(
        age=52,
        gender="female",
        marital_status=None, # Missing marital status!
        bpl_card_holder=True,
        confirmed_fields=["age", "gender", "bpl_card_holder"]
    )
    res = evaluate_scheme(ignwps, profile)
    assert res.status == "NOT SURE"
    assert "marital_status" in res.missing_fields

def test_user_with_conflicting_answers():
    """
    Profile contradiction engine must detect incompatible claims:
    e.g. Underage widow, high income with BPL card, cultivator farmer with 0 land.
    """
    profile = CitizenProfile(
        age=15, # Minor
        marital_status="widow", # Underage widow
        annual_income=900000.0, # High income
        bpl_card_holder=True, # BPL card
        occupation="farmer",
        landholding_hectares=0.0 # 0 land farmer
    )
    contradictions = detect_profile_contradictions(profile)
    assert len(contradictions) >= 3
    
    warning_fields = [c["fields"] for c in contradictions]
    assert any("age" in f and "marital_status" in f for f in warning_fields)
    assert any("annual_income" in f and "bpl_card_holder" in f for f in warning_fields)
    assert any("occupation" in f and "landholding_hectares" in f for f in warning_fields)

def test_state_filtering_rejection():
    """
    State-specific schemes (e.g. Sanjay Gandhi in Maharashtra, MMVY in MP) must reject
    applicants residing in an ineligible state.
    """
    schemes = scheme_service.get_all_schemes()
    profile = CitizenProfile(
        state="Bihar", # Ineligible for MP and Maharashtra state schemes
        confirmed_fields=["state"]
    )
    result = evaluate_all_schemes(schemes, profile)
    not_eligible_ids = [s.scheme_id for s in result.not_eligible]
    assert "mmvy_scholarship" in not_eligible_ids
    assert "ladli_behna_mp" in not_eligible_ids
    assert "sanjay_gandhi_niradhar_mh" in not_eligible_ids

