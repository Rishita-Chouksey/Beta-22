import pytest
from app.models.profile import CitizenProfile
from app.models.scheme import SchemeRule
from app.engine.rules import evaluate_single_rule

def test_rule_operator_eq():
    rule = SchemeRule(
        field="gender",
        operator="eq",
        value="female",
        description_en="Must be female",
        description_hi="महिला होनी चाहिए"
    )
    
    # PASS
    p_pass = CitizenProfile(gender="female")
    res_pass = evaluate_single_rule(rule, p_pass)
    assert res_pass.outcome == "PASS"

    # FAIL
    p_fail = CitizenProfile(gender="male")
    res_fail = evaluate_single_rule(rule, p_fail)
    assert res_fail.outcome == "FAIL"

def test_rule_operator_ne():
    rule = SchemeRule(
        field="holds_constitutional_post",
        operator="ne",
        value=True,
        description_en="Must not hold constitutional post",
        description_hi="संवैधानिक पद नहीं होना चाहिए"
    )
    p_pass = CitizenProfile(holds_constitutional_post=False)
    assert evaluate_single_rule(rule, p_pass).outcome == "PASS"

    p_fail = CitizenProfile(holds_constitutional_post=True)
    assert evaluate_single_rule(rule, p_fail).outcome == "FAIL"

def test_rule_operator_in_and_not_in():
    rule_in = SchemeRule(
        field="occupation",
        operator="in",
        value=["farmer", "agricultural_worker"],
        description_en="Must be farmer or agri laborer",
        description_hi="किसान या खेतिहर मजदूर"
    )
    assert evaluate_single_rule(rule_in, CitizenProfile(occupation="farmer")).outcome == "PASS"
    assert evaluate_single_rule(rule_in, CitizenProfile(occupation="student")).outcome == "FAIL"

    rule_not_in = SchemeRule(
        field="category",
        operator="not_in",
        value=["ExcludedCategory"],
        description_en="Not in excluded",
        description_hi="अपवर्जित में नहीं"
    )
    assert evaluate_single_rule(rule_not_in, CitizenProfile(category="OBC")).outcome == "PASS"
    assert evaluate_single_rule(rule_not_in, CitizenProfile(category="ExcludedCategory")).outcome == "FAIL"

def test_rule_operator_lte_and_gte():
    rule_lte = SchemeRule(
        field="annual_income",
        operator="lte",
        value=200000.0,
        description_en="Annual income <= 2 Lakhs",
        description_hi="वार्षिक आय <= 2 लाख"
    )
    assert evaluate_single_rule(rule_lte, CitizenProfile(annual_income=150000.0)).outcome == "PASS"
    assert evaluate_single_rule(rule_lte, CitizenProfile(annual_income=250000.0)).outcome == "FAIL"

    rule_gte = SchemeRule(
        field="student_class12_marks_percent",
        operator="gte",
        value=70.0,
        description_en="Marks >= 70%",
        description_hi="अंक >= 70%"
    )
    assert evaluate_single_rule(rule_gte, CitizenProfile(student_class12_marks_percent=85.0)).outcome == "PASS"
    assert evaluate_single_rule(rule_gte, CitizenProfile(student_class12_marks_percent=65.0)).outcome == "FAIL"

def test_rule_operator_between():
    rule = SchemeRule(
        field="age",
        operator="between",
        value=[18, 60],
        description_en="Age between 18 and 60",
        description_hi="आयु 18 से 60 वर्ष"
    )
    assert evaluate_single_rule(rule, CitizenProfile(age=25)).outcome == "PASS"
    assert evaluate_single_rule(rule, CitizenProfile(age=16)).outcome == "FAIL"
    assert evaluate_single_rule(rule, CitizenProfile(age=65)).outcome == "FAIL"

def test_missing_field_returns_unknown():
    rule = SchemeRule(
        field="landholding_hectares",
        operator="lte",
        value=2.0,
        description_en="Land <= 2 ha",
        description_hi="भूमि <= 2 हे"
    )
    p = CitizenProfile() # landholding is None
    res = evaluate_single_rule(rule, p)
    assert res.outcome == "UNKNOWN"
    assert "not been provided" in res.reason_en

def test_unconfirmed_field_returns_unknown():
    rule = SchemeRule(
        field="annual_income",
        operator="lte",
        value=250000.0,
        description_en="Income <= 2.5 L",
        description_hi="आय <= 2.5 लाख"
    )
    # Profile has confirmed_fields tracking, but 'annual_income' is NOT in confirmed_fields
    p = CitizenProfile(annual_income=120000.0, confirmed_fields=["age", "gender"])
    res = evaluate_single_rule(rule, p)
    assert res.outcome == "UNKNOWN"
    assert "not yet confirmed" in res.reason_en

def test_income_band_crossing_limits_returns_unknown():
    rule = SchemeRule(
        field="annual_income",
        operator="lte",
        value=200000.0, # Scheme threshold is 2 Lakhs
        description_en="Income <= 2 Lakhs",
        description_hi="आय <= 2 लाख"
    )
    # Band is "1_to_2.5_lakh" (range 100k - 250k), which straddles the 200k limit!
    p = CitizenProfile(income_band="1_to_2.5_lakh")
    res = evaluate_single_rule(rule, p)
    assert res.outcome == "UNKNOWN"
    assert "straddles the scheme limit" in res.reason_en

def test_borderline_value_triggers_unknown():
    rule = SchemeRule(
        field="annual_income",
        operator="lte",
        value=100000.0,
        description_en="Income <= 100,000",
        description_hi="आय <= 1 लाख"
    )
    # Income is 99,500 which is within 1% of 100,000 limit
    p = CitizenProfile(annual_income=99500.0)
    res = evaluate_single_rule(rule, p)
    assert res.outcome == "UNKNOWN"
    assert "borderline" in res.reason_en.lower()

def test_external_unverifiable_rule_triggers_unknown():
    rule = SchemeRule(
        field="landholding_hectares",
        operator="lte",
        value=2.0,
        description_en="Physical spot verification of land possession",
        description_hi="भूमि कब्जे का भौतिक सत्यापन",
        is_external_unverifiable=True
    )
    p = CitizenProfile(landholding_hectares=1.2)
    res = evaluate_single_rule(rule, p)
    assert res.outcome == "UNKNOWN"
    assert res.is_external_unverifiable is True
