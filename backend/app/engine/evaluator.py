from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from ..models.profile import CitizenProfile
from ..models.scheme import SchemeDefinition, SchemeRule
from ..models.evaluation import SchemeEvaluationResult, OverallEvaluationResponse, RuleEvaluationResult
from .rules import evaluate_single_rule

def evaluate_scheme(scheme: SchemeDefinition, profile: CitizenProfile, verified_reference_date: Optional[date] = None) -> SchemeEvaluationResult:
    """
    Evaluates a single scheme against a citizen profile.
    Returns SchemeEvaluationResult with status:
    - ELIGIBLE
    - NOT ELIGIBLE
    - NOT SURE
    - NO CURRENT RULES
    """
    # 1. Staleness and Verification Check
    ref_date = verified_reference_date or date.today()
    try:
        scheme_date = datetime.strptime(scheme.last_verified_date, "%Y-%m-%d").date()
        age_days = (ref_date - scheme_date).days
        is_stale = age_days > scheme.max_allowed_age_days or scheme.verification_status != "verified"
    except Exception:
        is_stale = True

    if is_stale or not scheme.rules or scheme.verification_status != "verified":
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            level=scheme.level,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            status="NO CURRENT RULES",
            deciding_reason_en="Scheme rules are currently unverified, incomplete or outdated. Cannot generate definitive eligibility.",
            deciding_reason_hi="योजना के नियम वर्तमान में असत्यापित, अपूर्ण या पुराने हैं। निश्चित पात्रता उत्पन्न नहीं की जा सकती।",
            rule_results=[],
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=True,
            official_source_url=scheme.official_source_url
        )

    # 2. State Applicability Check
    rule_results: List[RuleEvaluationResult] = []
    missing_fields: List[str] = []
    
    if "ALL" not in scheme.applicable_states:
        if profile.state is None:
            rule_results.append(RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=None,
                outcome="UNKNOWN",
                reason_en=f"State is required. Scheme is only applicable in: {', '.join(scheme.applicable_states)}",
                reason_hi=f"राज्य की जानकारी आवश्यक है। यह योजना केवल निम्नलिखित राज्यों में लागू है: {', '.join(scheme.applicable_states)}"
            ))
            missing_fields.append("state")
        elif profile.state not in scheme.applicable_states:
            rule_results.append(RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=profile.state,
                outcome="FAIL",
                reason_en=f"Scheme applies only to residents of {', '.join(scheme.applicable_states)}. Citizen state is {profile.state}.",
                reason_hi=f"यह योजना केवल {', '.join(scheme.applicable_states)} के निवासियों पर लागू होती है। नागरिक का राज्य {profile.state} है।"
            ))
            return SchemeEvaluationResult(
                scheme_id=scheme.id,
                scheme_name_en=scheme.name_en,
                scheme_name_hi=scheme.name_hi,
                level=scheme.level,
                category=scheme.category,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                status="NOT ELIGIBLE",
                deciding_reason_en=f"Not applicable in {profile.state}. Only applicable in {', '.join(scheme.applicable_states)}.",
                deciding_reason_hi=f"{profile.state} में लागू नहीं है। केवल {', '.join(scheme.applicable_states)} में लागू है।",
                rule_results=rule_results,
                missing_fields=[],
                last_verified_date=scheme.last_verified_date,
                is_stale=False,
                official_source_url=scheme.official_source_url
            )
        else:
            rule_results.append(RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=profile.state,
                outcome="PASS",
                reason_en=f"Resident of eligible state ({profile.state}).",
                reason_hi=f"पात्र राज्य ({profile.state}) का निवासी।"
            ))

    # 3. Evaluate each rule in the scheme
    has_fail = False
    has_unknown = False
    first_fail_reason_en = ""
    first_fail_reason_hi = ""
    first_unknown_reason_en = ""
    first_unknown_reason_hi = ""

    for rule in scheme.rules:
        res = evaluate_single_rule(rule, profile)
        rule_results.append(res)
        
        if res.outcome == "FAIL":
            has_fail = True
            if not first_fail_reason_en:
                first_fail_reason_en = res.reason_en
                first_fail_reason_hi = res.reason_hi
        elif res.outcome == "UNKNOWN":
            has_unknown = True
            if res.field not in missing_fields and getattr(profile, res.field, None) is None:
                missing_fields.append(res.field)
            if not first_unknown_reason_en:
                first_unknown_reason_en = res.reason_en
                first_unknown_reason_hi = res.reason_hi

    # 4. Synthesize scheme outcome
    if has_fail:
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            level=scheme.level,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            status="NOT ELIGIBLE",
            deciding_reason_en=first_fail_reason_en or "Does not satisfy one or more required eligibility conditions.",
            deciding_reason_hi=first_fail_reason_hi or "एक या अधिक आवश्यक पात्रता शर्तों को पूरा नहीं करता है।",
            rule_results=rule_results,
            missing_fields=missing_fields,
            last_verified_date=scheme.last_verified_date,
            is_stale=False,
            official_source_url=scheme.official_source_url
        )
    elif has_unknown:
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            level=scheme.level,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            status="NOT SURE",
            deciding_reason_en=first_unknown_reason_en or "Additional details or official verification required to establish certainty.",
            deciding_reason_hi=first_unknown_reason_hi or "निश्चितता स्थापित करने के लिए अतिरिक्त विवरण या आधिकारिक सत्यापन की आवश्यकता है।",
            rule_results=rule_results,
            missing_fields=missing_fields,
            last_verified_date=scheme.last_verified_date,
            is_stale=False,
            official_source_url=scheme.official_source_url
        )
    else:
        # Every rule passed
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            level=scheme.level,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            status="ELIGIBLE",
            deciding_reason_en="All confirmed profile criteria strictly meet the verified official eligibility guidelines.",
            deciding_reason_hi="सभी पुष्ट प्रोफ़ाइल मानदंड सत्यापित आधिकारिक पात्रता दिशानिर्देशों को पूरा करते हैं।",
            rule_results=rule_results,
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=False,
            official_source_url=scheme.official_source_url
        )

def evaluate_all_schemes(schemes: List[SchemeDefinition], profile: CitizenProfile) -> OverallEvaluationResponse:
    """Evaluates all schemes in the library and sorts them into 4 distinct categories."""
    eligible: List[SchemeEvaluationResult] = []
    not_sure: List[SchemeEvaluationResult] = []
    not_eligible: List[SchemeEvaluationResult] = []
    no_rules: List[SchemeEvaluationResult] = []

    for scheme in schemes:
        res = evaluate_scheme(scheme, profile)
        if res.status == "ELIGIBLE":
            eligible.append(res)
        elif res.status == "NOT SURE":
            not_sure.append(res)
        elif res.status == "NOT ELIGIBLE":
            not_eligible.append(res)
        else:
            no_rules.append(res)

    return OverallEvaluationResponse(
        eligible=eligible,
        not_sure=not_sure,
        not_eligible=not_eligible,
        no_rules=no_rules,
        total_evaluated=len(schemes),
        active_profile_summary=profile.model_dump(exclude_none=True)
    )
