from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from ..models.profile import CitizenProfile
from ..models.scheme import SchemeDefinition, SchemeRule
from ..models.evaluation import SchemeEvaluationResult, OverallEvaluationResponse, RuleEvaluationResult
from .rules import evaluate_single_rule

def detect_profile_contradictions(profile: CitizenProfile) -> List[Dict[str, Any]]:
    """
    Detects logically conflicting or legally contradictory profile answers.
    Ensures contradictory citizen profiles are transparently flagged.
    """
    contradictions = []

    # 1. Underage claiming widow / married / divorced
    if profile.age is not None and profile.age < 18:
        if profile.marital_status in ["married", "widow", "divorced"]:
            contradictions.append({
                "fields": ["age", "marital_status"],
                "warning_en": f"Citizen age is recorded as {profile.age} years (minor), but marital status is recorded as '{profile.marital_status}'. Legal marriage age in India is 18 (female) / 21 (male).",
                "warning_hi": f"नागरिक की आयु {profile.age} वर्ष (नाबालिग) दर्ज है, लेकिन वैवाहिक स्थिति '{profile.marital_status}' है। भारत में विवाह की न्यूनतम कानूनी आयु 18/21 वर्ष है।"
            })

    # 2. High annual income alongside Below Poverty Line (BPL) card
    if profile.annual_income is not None and profile.annual_income > 600000 and profile.bpl_card_holder is True:
        contradictions.append({
            "fields": ["annual_income", "bpl_card_holder"],
            "warning_en": f"Family income of ₹{profile.annual_income:,.0f} exceeds standard poverty thresholds, but BPL ration card is claimed. Official revenue re-verification required.",
            "warning_hi": f"परिवार की आय ₹{profile.annual_income:,.0f} गरीबी रेखा से काफी अधिक है, परंतु बीपीएल कार्ड धारक स्थिति दर्ज है। राजस्व पुनर्सत्यापन आवश्यक है।"
        })

    # 3. Cultivator farmer with zero agricultural land
    if profile.occupation == "farmer" and profile.landholding_hectares is not None and profile.landholding_hectares == 0.0:
        contradictions.append({
            "fields": ["occupation", "landholding_hectares"],
            "warning_en": "Primary occupation is marked as Farmer/Cultivator, but agricultural landholding is 0 hectares. If you work on others' land, please select 'Agricultural Laborer'.",
            "warning_hi": "मुख्य व्यवसाय किसान/काश्तकार चुना गया है, लेकिन कृषि भूमि 0 हेक्टेयर है। यदि आप दूसरों के खेत में मजदूरी करते हैं, तो 'खेतिहर मजदूर' चुनें।"
        })

    # 4. Senior citizen marked as active student
    if profile.age is not None and profile.age >= 60 and profile.occupation == "student":
        contradictions.append({
            "fields": ["age", "occupation"],
            "warning_en": f"Age {profile.age} is categorized as a senior citizen, but occupation is entered as active student. Youth education scholarships require fresh enrollment verification.",
            "warning_hi": f"आयु {profile.age} वर्ष वरिष्ठ नागरिक श्रेणी में है, लेकिन व्यवसाय 'छात्र' दर्ज है। युवा छात्रवृत्ति योजनाओं के लिए नवीन नामांकन सत्यापन आवश्यक है।"
        })

    return contradictions

def evaluate_scheme(scheme: SchemeDefinition, profile: CitizenProfile, verified_reference_date: Optional[date] = None) -> SchemeEvaluationResult:
    """
    Evaluates a single scheme against a citizen profile.
    Returns SchemeEvaluationResult with status:
    - ELIGIBLE (Likely eligible)
    - NOT ELIGIBLE (Not eligible)
    - NOT SURE (Needs verification)
    - NO CURRENT RULES (Unverified/stale)
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
            satisfied_conditions=[],
            unknown_conditions=["Scheme rules pending official audit/verification."],
            failed_conditions=[],
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=True,
            official_source_url=scheme.official_source_url
        )

    # 2. State Applicability Check
    rule_results: List[RuleEvaluationResult] = []
    missing_fields: List[str] = []
    satisfied_conditions: List[str] = []
    unknown_conditions: List[str] = []
    failed_conditions: List[str] = []
    
    if "ALL" not in scheme.applicable_states:
        if profile.state is None:
            state_res = RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=None,
                outcome="UNKNOWN",
                reason_en=f"State residence required. Scheme is specific to: {', '.join(scheme.applicable_states)}.",
                reason_hi=f"राज्य निवास आवश्यक है। यह योजना केवल {', '.join(scheme.applicable_states)} के लिए है।"
            )
            rule_results.append(state_res)
            missing_fields.append("state")
            unknown_conditions.append(state_res.reason_en)
        elif profile.state not in scheme.applicable_states:
            state_res = RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=profile.state,
                outcome="FAIL",
                reason_en=f"Scheme applies only to residents of {', '.join(scheme.applicable_states)}. Citizen resides in {profile.state}.",
                reason_hi=f"यह योजना केवल {', '.join(scheme.applicable_states)} के निवासियों पर लागू होती है। नागरिक का राज्य {profile.state} है।"
            )
            rule_results.append(state_res)
            failed_conditions.append(state_res.reason_en)
            return SchemeEvaluationResult(
                scheme_id=scheme.id,
                scheme_name_en=scheme.name_en,
                scheme_name_hi=scheme.name_hi,
                level=scheme.level,
                category=scheme.category,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                status="NOT ELIGIBLE",
                deciding_reason_en=f"Not applicable in {profile.state}. Exclusively applicable in {', '.join(scheme.applicable_states)}.",
                deciding_reason_hi=f"{profile.state} में लागू नहीं है। केवल {', '.join(scheme.applicable_states)} में लागू है।",
                rule_results=rule_results,
                satisfied_conditions=satisfied_conditions,
                unknown_conditions=unknown_conditions,
                failed_conditions=failed_conditions,
                missing_fields=[],
                last_verified_date=scheme.last_verified_date,
                is_stale=False,
                official_source_url=scheme.official_source_url
            )
        else:
            state_res = RuleEvaluationResult(
                field="state",
                operator="in",
                expected_value=scheme.applicable_states,
                actual_value=profile.state,
                outcome="PASS",
                reason_en=f"Resident of eligible state ({profile.state}).",
                reason_hi=f"पात्र राज्य ({profile.state}) का निवासी।"
            )
            rule_results.append(state_res)
            satisfied_conditions.append(state_res.reason_en)

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
            failed_conditions.append(res.reason_en)
            if not first_fail_reason_en:
                first_fail_reason_en = res.reason_en
                first_fail_reason_hi = res.reason_hi
        elif res.outcome == "UNKNOWN":
            has_unknown = True
            unknown_conditions.append(res.reason_en)
            if res.field not in missing_fields and getattr(profile, res.field, None) is None:
                missing_fields.append(res.field)
            if not first_unknown_reason_en:
                first_unknown_reason_en = res.reason_en
                first_unknown_reason_hi = res.reason_hi
        elif res.outcome == "PASS":
            satisfied_conditions.append(res.reason_en)

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
            satisfied_conditions=satisfied_conditions,
            unknown_conditions=unknown_conditions,
            failed_conditions=failed_conditions,
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
            satisfied_conditions=satisfied_conditions,
            unknown_conditions=unknown_conditions,
            failed_conditions=failed_conditions,
            missing_fields=missing_fields,
            last_verified_date=scheme.last_verified_date,
            is_stale=False,
            official_source_url=scheme.official_source_url
        )
    else:
        # Every rule passed with confirmed answers
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
            satisfied_conditions=satisfied_conditions,
            unknown_conditions=[],
            failed_conditions=[],
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=False,
            official_source_url=scheme.official_source_url
        )

def evaluate_all_schemes(schemes: List[SchemeDefinition], profile: CitizenProfile) -> OverallEvaluationResponse:
    """Evaluates all schemes in the library, detects profile contradictions, and sorts into distinct categories."""
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

    contradictions = detect_profile_contradictions(profile)

    return OverallEvaluationResponse(
        eligible=eligible,
        not_sure=not_sure,
        not_eligible=not_eligible,
        no_rules=no_rules,
        total_evaluated=len(schemes),
        active_profile_summary=profile.model_dump(exclude_none=True),
        contradictions=contradictions
    )
