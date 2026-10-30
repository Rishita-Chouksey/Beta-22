import pytest
from app.models.profile import CitizenProfile
from app.services.scheme_service import scheme_service
from app.engine.question_selector import select_next_question

def test_initial_question_selection():
    # Empty profile should select the highest frequency, easiest field
    profile = CitizenProfile()
    schemes = scheme_service.get_all_schemes()
    res = select_next_question(schemes, profile, current_step=1)
    
    assert res.has_more is True
    assert res.question is not None
    assert res.question.field in ["state", "gender", "age", "occupation", "annual_income"]

def test_stopping_condition_when_all_schemes_resolved():
    # Provide complete profile for farmer persona
    farmer_profile = CitizenProfile(
        occupation="farmer",
        residence_type="rural",
        landholding_hectares=1.5,
        is_institutional_landholder=False,
        holds_constitutional_post=False,
        state="Madhya Pradesh",
        gender="male",
        age=45,
        annual_income=65000.0,
        has_pucca_house=False,
        bpl_card_holder=True,
        student_class12_marks_percent=0.0,
        enrolled_higher_education=False,
        marital_status="married"
    )
    schemes = scheme_service.get_all_schemes()
    res = select_next_question(schemes, farmer_profile, current_step=9)
    # Since all fields are populated and step exceeds target, has_more must be False
    assert res.has_more is False
    assert res.question is None
