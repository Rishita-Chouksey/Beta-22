import pytest
from app.models.profile import CitizenProfile
from app.services.scheme_service import scheme_service
from app.engine.evaluator import evaluate_all_schemes
from app.services.checklist_service import generate_consolidated_checklist

def test_persona_1_rural_farmer():
    """
    Persona 1: Rural Farmer
    - 48 year old male farmer residing in rural Madhya Pradesh
    - Holds 1.5 hectares cultivable land
    - Annual income ₹65,000 (below poverty line)
    - Lives in kutcha house, non-institutional landholder, no govt post
    Expectations:
    - PM-KISAN: ELIGIBLE
    - PMAY-G: ELIGIBLE
    - MMVY: NOT ELIGIBLE (not student, no marks)
    """
    farmer = CitizenProfile(
        age=48,
        gender="male",
        marital_status="married",
        state="Madhya Pradesh",
        residence_type="rural",
        occupation="farmer",
        landholding_hectares=1.5,
        annual_income=65000.0,
        is_institutional_landholder=False,
        holds_constitutional_post=False,
        has_pucca_house=False,
        bpl_card_holder=True
    )

    schemes = scheme_service.get_all_schemes()
    eval_res = evaluate_all_schemes(schemes, farmer)

    eligible_ids = [s.scheme_id for s in eval_res.eligible]
    assert "pm_kisan" in eligible_ids
    assert "pm_awas_yojana_gramin" in eligible_ids
    
    not_eligible_ids = [s.scheme_id for s in eval_res.not_eligible]
    assert "mmvy_scholarship" in not_eligible_ids

    # Document Checklist test
    checklist = generate_consolidated_checklist(eligible_ids)
    doc_ids = [d.document_id for d in checklist.documents]
    assert "aadhaar" in doc_ids
    assert "land_record" in doc_ids
    assert "bank_passbook" in doc_ids

def test_persona_2_widowed_woman():
    """
    Persona 2: Widowed Woman
    - 52 year old female widow residing in Madhya Pradesh
    - BPL card holder, annual family income ₹24,000
    - No govt employee in family, landholding <= 2 ha
    Expectations:
    - IGNWPS (Indira Gandhi National Widow Pension): ELIGIBLE
    - Ladli Behna (MP): ELIGIBLE
    - PM-KISAN: NOT ELIGIBLE (not farmer)
    """
    widow = CitizenProfile(
        age=52,
        gender="female",
        marital_status="widow",
        state="Madhya Pradesh",
        residence_type="rural",
        occupation="homemaker",
        annual_income=24000.0,
        bpl_card_holder=True,
        holds_constitutional_post=False,
        landholding_hectares=0.0
    )

    schemes = scheme_service.get_all_schemes()
    eval_res = evaluate_all_schemes(schemes, widow)

    eligible_ids = [s.scheme_id for s in eval_res.eligible]
    assert "ignwps_widow_pension" in eligible_ids
    assert "ladli_behna_mp" in eligible_ids

    not_eligible_ids = [s.scheme_id for s in eval_res.not_eligible]
    assert "pm_kisan" in not_eligible_ids

    # Document Checklist test
    checklist = generate_consolidated_checklist(eligible_ids)
    doc_ids = [d.document_id for d in checklist.documents]
    assert "death_certificate_husband" in doc_ids
    assert "samagra_id" in doc_ids

def test_persona_3_college_student():
    """
    Persona 3: College-going Student
    - 19 year old student residing in Madhya Pradesh
    - Scored 86% in Class 12 board examination
    - Enrolled in recognized Higher Education engineering course
    - Family annual income ₹4,50,000 (well within ₹6 Lakh ceiling)
    Expectations:
    - MMVY Scholarship: ELIGIBLE
    - PM-KISAN: NOT ELIGIBLE (not a farmer)
    - IGNWPS: NOT ELIGIBLE (not widow)
    """
    student = CitizenProfile(
        age=19,
        gender="female",
        marital_status="single",
        state="Madhya Pradesh",
        occupation="student",
        student_class12_marks_percent=86.0,
        enrolled_higher_education=True,
        annual_income=450000.0,
        holds_constitutional_post=False
    )

    schemes = scheme_service.get_all_schemes()
    eval_res = evaluate_all_schemes(schemes, student)

    eligible_ids = [s.scheme_id for s in eval_res.eligible]
    assert "mmvy_scholarship" in eligible_ids

    not_eligible_ids = [s.scheme_id for s in eval_res.not_eligible]
    assert "pm_kisan" in not_eligible_ids
    assert "ignwps_widow_pension" in not_eligible_ids

    # Document Checklist test
    checklist = generate_consolidated_checklist(eligible_ids)
    doc_ids = [d.document_id for d in checklist.documents]
    assert "mp_domicile" in doc_ids
    assert "marksheet_12th" in doc_ids
    assert "income_cert" in doc_ids
