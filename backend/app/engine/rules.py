from typing import Any, Tuple, Optional, List
from ..models.profile import CitizenProfile
from ..models.scheme import SchemeRule
from ..models.evaluation import RuleEvaluationResult

# Mapping income bands to numerical ranges (min, max)
INCOME_BAND_RANGES = {
    "below_1_lakh": (0, 100000),
    "1_to_2.5_lakh": (100000, 250000),
    "2.5_to_6_lakh": (250000, 600000),
    "above_6_lakh": (600000, 10000000),
}

def evaluate_single_rule(rule: SchemeRule, profile: CitizenProfile) -> RuleEvaluationResult:
    """
    Evaluates a single SchemeRule against a CitizenProfile.
    Returns RuleEvaluationResult with outcome: 'PASS', 'FAIL', or 'UNKNOWN'.
    Never guesses unknown values.
    Handles income ranges crossing limits, borderline values, OR combinations, and unconfirmed fields.
    """
    # 0. Handle composite OR rules
    if rule.operator.lower() == "or" or (rule.or_rules and len(rule.or_rules) > 0):
        sub_rules = rule.or_rules or []
        sub_results = [evaluate_single_rule(r, profile) for r in sub_rules]
        passed = [sr for sr in sub_results if sr.outcome == "PASS"]
        if passed:
            return RuleEvaluationResult(
                field=rule.field,
                operator="or",
                expected_value=rule.value,
                actual_value=passed[0].actual_value,
                outcome="PASS",
                reason_en=f"Satisfied alternative condition: {passed[0].reason_en}",
                reason_hi=f"वैकल्पिक शर्त पूरी हुई: {passed[0].reason_hi}",
                is_external_unverifiable=False
            )
        if all(sr.outcome == "FAIL" for sr in sub_results):
            return RuleEvaluationResult(
                field=rule.field,
                operator="or",
                expected_value=rule.value,
                actual_value=[sr.actual_value for sr in sub_results],
                outcome="FAIL",
                reason_en=f"None of the alternative criteria met: {rule.description_en}",
                reason_hi=f"वैकल्पिक मानदंडों में से कोई भी पूरा नहीं हुआ: {rule.description_hi}",
                is_external_unverifiable=False
            )
        return RuleEvaluationResult(
            field=rule.field,
            operator="or",
            expected_value=rule.value,
            actual_value=None,
            outcome="UNKNOWN",
            reason_en=f"Verification required for one of the alternative conditions: {rule.description_en}",
            reason_hi=f"वैकल्पिक शर्तों में से एक के सत्यापन की आवश्यकता है: {rule.description_hi}",
            is_external_unverifiable=False
        )

    field_name = rule.field
    actual_value = getattr(profile, field_name, None)
    
    # 1. Missing field
    if actual_value is None:
        # Check if income is queried but only income_band is provided
        if field_name == "annual_income" and profile.income_band:
            return _evaluate_income_band(rule, profile.income_band)
            
        return RuleEvaluationResult(
            field=field_name,
            operator=rule.operator,
            expected_value=rule.value,
            actual_value=None,
            outcome="UNKNOWN",
            reason_en=f"Information for '{field_name}' has not been provided yet.",
            reason_hi=f"'{field_name}' के लिए जानकारी अभी प्रदान नहीं की गई है।",
            is_external_unverifiable=rule.is_external_unverifiable
        )
        
    # 2. Check confirmation: unconfirmed fields must never be used for definitive eligibility
    if not profile.is_field_confirmed(field_name):
        return RuleEvaluationResult(
            field=field_name,
            operator=rule.operator,
            expected_value=rule.value,
            actual_value=actual_value,
            outcome="UNKNOWN",
            reason_en=f"Value for '{field_name}' is extracted but not yet confirmed by citizen.",
            reason_hi=f"'{field_name}' का मान निकाला गया है लेकिन नागरिक द्वारा पुष्टि नहीं की गई है।",
            is_external_unverifiable=rule.is_external_unverifiable
        )
        
    # 3. External unverifiable condition flag
    if rule.is_external_unverifiable:
        return RuleEvaluationResult(
            field=field_name,
            operator=rule.operator,
            expected_value=rule.value,
            actual_value=actual_value,
            outcome="UNKNOWN",
            reason_en=f"External official verification required: {rule.description_en}",
            reason_hi=f"बाहरी आधिकारिक सत्यापन आवश्यक: {rule.description_hi}",
            is_external_unverifiable=True
        )

    # 4. Operator evaluation
    op = rule.operator.lower()
    expected = rule.value

    try:
        if op == "eq":
            return _eval_eq(rule, actual_value, expected)
        elif op == "ne":
            return _eval_ne(rule, actual_value, expected)
        elif op == "in":
            return _eval_in(rule, actual_value, expected)
        elif op == "not_in":
            return _eval_not_in(rule, actual_value, expected)
        elif op == "lte":
            return _eval_lte(rule, actual_value, expected)
        elif op == "gte":
            return _eval_gte(rule, actual_value, expected)
        elif op == "between":
            return _eval_between(rule, actual_value, expected)
        else:
            return RuleEvaluationResult(
                field=field_name,
                operator=op,
                expected_value=expected,
                actual_value=actual_value,
                outcome="UNKNOWN",
                reason_en=f"Unsupported operator '{op}'.",
                reason_hi=f"असमर्थित ऑपरेटर '{op}'।",
                is_external_unverifiable=False
            )
    except Exception as e:
        return RuleEvaluationResult(
            field=field_name,
            operator=op,
            expected_value=expected,
            actual_value=actual_value,
            outcome="UNKNOWN",
            reason_en=f"Error evaluating condition: {str(e)}",
            reason_hi=f"शर्त का मूल्यांकन करने में त्रुटि: {str(e)}",
            is_external_unverifiable=False
        )

def _eval_eq(rule: SchemeRule, actual: Any, expected: Any) -> RuleEvaluationResult:
    if isinstance(actual, str) and isinstance(expected, str):
        match = actual.strip().lower() == expected.strip().lower()
    else:
        match = actual == expected
        
    if match:
        return RuleEvaluationResult(
            field=rule.field,
            operator="eq",
            expected_value=expected,
            actual_value=actual,
            outcome="PASS",
            reason_en=f"Matches requirement: {rule.description_en} (Provided: {actual})",
            reason_hi=f"आवश्यकता से मेल खाता है: {rule.description_hi} (प्रदान किया गया: {actual})"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="eq",
            expected_value=expected,
            actual_value=actual,
            outcome="FAIL",
            reason_en=f"Does not match requirement: {rule.description_en} (Provided: {actual})",
            reason_hi=f"आवश्यकता से मेल नहीं खाता: {rule.description_hi} (प्रदान किया गया: {actual})"
        )

def _eval_ne(rule: SchemeRule, actual: Any, expected: Any) -> RuleEvaluationResult:
    if isinstance(actual, str) and isinstance(expected, str):
        match = actual.strip().lower() != expected.strip().lower()
    else:
        match = actual != expected
        
    if match:
        return RuleEvaluationResult(
            field=rule.field,
            operator="ne",
            expected_value=expected,
            actual_value=actual,
            outcome="PASS",
            reason_en=f"Satisfies exclusion criteria: {rule.description_en}",
            reason_hi=f"अपवर्जन मानदंड को पूरा करता है: {rule.description_hi}"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="ne",
            expected_value=expected,
            actual_value=actual,
            outcome="FAIL",
            reason_en=f"Violates restriction: {rule.description_en} (Provided: {actual})",
            reason_hi=f"प्रतिबंध का उल्लंघन करता है: {rule.description_hi} (प्रदान किया गया: {actual})"
        )

def _eval_in(rule: SchemeRule, actual: Any, expected: list) -> RuleEvaluationResult:
    if isinstance(actual, str):
        actual_norm = actual.strip().lower()
        expected_norm = [str(x).strip().lower() for x in expected]
        match = actual_norm in expected_norm
    else:
        match = actual in expected
        
    if match:
        return RuleEvaluationResult(
            field=rule.field,
            operator="in",
            expected_value=expected,
            actual_value=actual,
            outcome="PASS",
            reason_en=f"Value '{actual}' falls within permissible categories: {expected}",
            reason_hi=f"मान '{actual}' अनुमेय श्रेणियों के अंतर्गत आता है: {expected}"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="in",
            expected_value=expected,
            actual_value=actual,
            outcome="FAIL",
            reason_en=f"Value '{actual}' is not in allowed categories: {rule.description_en}",
            reason_hi=f"मान '{actual}' अनुमत श्रेणियों में नहीं है: {rule.description_hi}"
        )

def _eval_not_in(rule: SchemeRule, actual: Any, expected: list) -> RuleEvaluationResult:
    if isinstance(actual, str):
        actual_norm = actual.strip().lower()
        expected_norm = [str(x).strip().lower() for x in expected]
        match = actual_norm not in expected_norm
    else:
        match = actual not in expected
        
    if match:
        return RuleEvaluationResult(
            field=rule.field,
            operator="not_in",
            expected_value=expected,
            actual_value=actual,
            outcome="PASS",
            reason_en=f"Condition met: {rule.description_en}",
            reason_hi=f"शर्त पूरी हुई: {rule.description_hi}"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="not_in",
            expected_value=expected,
            actual_value=actual,
            outcome="FAIL",
            reason_en=f"Value '{actual}' falls under restricted categories.",
            reason_hi=f"मान '{actual}' प्रतिबंधित श्रेणियों के अंतर्गत आता है।"
        )

def _eval_lte(rule: SchemeRule, actual: Any, expected: float) -> RuleEvaluationResult:
    actual_num = float(actual)
    expected_num = float(expected)
    
    # Borderline threshold check (within 1% near the threshold)
    if expected_num > 0 and abs(actual_num - expected_num) <= (0.01 * expected_num) and actual_num <= expected_num:
        return RuleEvaluationResult(
            field=rule.field,
            operator="lte",
            expected_value=expected_num,
            actual_value=actual_num,
            outcome="UNKNOWN",
            reason_en=f"Value {actual_num} is borderline close to limit {expected_num}. Official documentation required to confirm exact boundary.",
            reason_hi=f"मान {actual_num} सीमा {expected_num} के बहुत करीब है। सटीक सीमा की पुष्टि के लिए आधिकारिक दस्तावेज़ आवश्यक हैं।"
        )
        
    if actual_num <= expected_num:
        return RuleEvaluationResult(
            field=rule.field,
            operator="lte",
            expected_value=expected_num,
            actual_value=actual_num,
            outcome="PASS",
            reason_en=f"Satisfies maximum limit: {actual_num} <= {expected_num} ({rule.description_en})",
            reason_hi=f"अधिकतम सीमा को पूरा करता है: {actual_num} <= {expected_num} ({rule.description_hi})"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="lte",
            expected_value=expected_num,
            actual_value=actual_num,
            outcome="FAIL",
            reason_en=f"Exceeds maximum permissible limit: {actual_num} > {expected_num} ({rule.description_en})",
            reason_hi=f"अधिकतम अनुमेय सीमा से अधिक है: {actual_num} > {expected_num} ({rule.description_hi})"
        )

def _eval_gte(rule: SchemeRule, actual: Any, expected: float) -> RuleEvaluationResult:
    actual_num = float(actual)
    expected_num = float(expected)
    
    if actual_num >= expected_num:
        return RuleEvaluationResult(
            field=rule.field,
            operator="gte",
            expected_value=expected_num,
            actual_value=actual_num,
            outcome="PASS",
            reason_en=f"Meets minimum threshold: {actual_num} >= {expected_num} ({rule.description_en})",
            reason_hi=f"न्यूनतम सीमा को पूरा करता है: {actual_num} >= {expected_num} ({rule.description_hi})"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="gte",
            expected_value=expected_num,
            actual_value=actual_num,
            outcome="FAIL",
            reason_en=f"Below minimum required threshold: {actual_num} < {expected_num} ({rule.description_en})",
            reason_hi=f"आवश्यक न्यूनतम सीमा से कम है: {actual_num} < {expected_num} ({rule.description_hi})"
        )

def _eval_between(rule: SchemeRule, actual: Any, expected: list) -> RuleEvaluationResult:
    actual_num = float(actual)
    min_val = float(expected[0])
    max_val = float(expected[1])
    
    if min_val <= actual_num <= max_val:
        return RuleEvaluationResult(
            field=rule.field,
            operator="between",
            expected_value=expected,
            actual_value=actual_num,
            outcome="PASS",
            reason_en=f"Value {actual_num} is within eligible range [{min_val}, {max_val}] ({rule.description_en})",
            reason_hi=f"मान {actual_num} पात्र सीमा [{min_val}, {max_val}] के अंतर्गत है ({rule.description_hi})"
        )
    else:
        return RuleEvaluationResult(
            field=rule.field,
            operator="between",
            expected_value=expected,
            actual_value=actual_num,
            outcome="FAIL",
            reason_en=f"Value {actual_num} falls outside eligible range [{min_val}, {max_val}] ({rule.description_en})",
            reason_hi=f"मान {actual_num} पात्र सीमा [{min_val}, {max_val}] से बाहर है ({rule.description_hi})"
        )

def _evaluate_income_band(rule: SchemeRule, band_key: str) -> RuleEvaluationResult:
    """Handles income band selection when exact numeric income is not provided."""
    band_range = INCOME_BAND_RANGES.get(band_key)
    if not band_range:
        return RuleEvaluationResult(
            field="annual_income",
            operator=rule.operator,
            expected_value=rule.value,
            actual_value=band_key,
            outcome="UNKNOWN",
            reason_en=f"Income range '{band_key}' cannot be evaluated deterministically.",
            reason_hi=f"आय सीमा '{band_key}' का निश्चित मूल्यांकन नहीं किया जा सकता।"
        )
        
    b_min, b_max = band_range
    op = rule.operator.lower()
    limit = float(rule.value) if isinstance(rule.value, (int, float)) else 0.0
    
    if op == "lte":
        if b_max <= limit:
            return RuleEvaluationResult(
                field="annual_income",
                operator="lte",
                expected_value=limit,
                actual_value=f"{b_min}-{b_max}",
                outcome="PASS",
                reason_en=f"Income band up to ₹{b_max} is completely within eligibility threshold of ₹{limit}.",
                reason_hi=f"₹{b_max} तक का आय वर्ग पूरी तरह से ₹{limit} की पात्रता सीमा के भीतर है।"
            )
        elif b_min > limit:
            return RuleEvaluationResult(
                field="annual_income",
                operator="lte",
                expected_value=limit,
                actual_value=f"{b_min}-{b_max}",
                outcome="FAIL",
                reason_en=f"Income band starting at ₹{b_min} exceeds maximum eligibility limit of ₹{limit}.",
                reason_hi=f"₹{b_min} से शुरू होने वाला आय वर्ग ₹{limit} की अधिकतम पात्रता सीमा से अधिक है।"
            )
        else:
            # Range crosses eligibility limit! Must return UNKNOWN / Not sure
            return RuleEvaluationResult(
                field="annual_income",
                operator="lte",
                expected_value=limit,
                actual_value=f"{b_min}-{b_max}",
                outcome="UNKNOWN",
                reason_en=f"Selected income range (₹{b_min} - ₹{b_max}) straddles the scheme limit (₹{limit}). Exact income certificate required to confirm.",
                reason_hi=f"चयनित आय वर्ग (₹{b_min} - ₹{b_max}) योजना सीमा (₹{limit}) के दोनों ओर पड़ता है। पुष्टि के लिए सटीक आय प्रमाण पत्र आवश्यक है।"
            )
            
    return RuleEvaluationResult(
        field="annual_income",
        operator=rule.operator,
        expected_value=rule.value,
        actual_value=band_key,
        outcome="UNKNOWN",
        reason_en="Income range requires specific value for deterministic evaluation.",
        reason_hi="निश्चित मूल्यांकन के लिए विशिष्ट आय मान आवश्यक है।"
    )
