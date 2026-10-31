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
                "warning_hi": f"नागरिक की आयु {profile.age} वर्ष (नाबालिग) दर्ज है, लेकिन वैवाहिक स्थिति '{profile.marital_status}' है। भारत में विवाह की न्यूनतम कानूनी आयु 18/21 वर्ष है।",
                "warning_bn": f"নাগরিকের বয়স {profile.age} বছর (নাবালক), কিন্তু বৈবাহিক অবস্থা '{profile.marital_status}'। ভারতে বিয়ের ন্যূনতম আইনি বয়স ১৮/২১ বছর।"
            })

    # 2. High annual income alongside Below Poverty Line (BPL) card
    if profile.annual_income is not None and profile.annual_income > 600000 and profile.bpl_card_holder is True:
        contradictions.append({
            "fields": ["annual_income", "bpl_card_holder"],
            "warning_en": f"Family income of ₹{profile.annual_income:,.0f} exceeds standard poverty thresholds, but BPL ration card is claimed. Official revenue re-verification required.",
            "warning_hi": f"परिवार की आय ₹{profile.annual_income:,.0f} गरीबी रेखा से काफी अधिक है, परंतु बीपीएल कार्ड धारक स्थिति दर्ज है। राजस्व पुनर्सत्यापन आवश्यक है।",
            "warning_bn": f"পারিবারিক আয় ₹{profile.annual_income:,.0f} দারিদ্র্যসীমার উল্লেখযোগ্য ঊর্ধ্বে, কিন্তু বিপিএল রেশন কার্ড দাবি করা হয়েছে। রাজস্ব পুনঃযাচাই প্রয়োজন।"
        })

    # 3. Cultivator farmer with zero agricultural land
    if profile.occupation == "farmer" and profile.landholding_hectares is not None and profile.landholding_hectares == 0.0:
        contradictions.append({
            "fields": ["occupation", "landholding_hectares"],
            "warning_en": "Primary occupation is marked as Farmer/Cultivator, but agricultural landholding is 0 hectares. If you work on others' land, please select 'Agricultural Laborer'.",
            "warning_hi": "मुख्य व्यवसाय किसान/काश्तकार चुना गया है, लेकिन कृषि भूमि 0 हेक्टेयर है। यदि आप दूसरों के खेत में मजदूरी करते हैं, तो 'खेतिहर मजदूर' चुनें।",
            "warning_bn": "প্রধান পেশা কৃষক/চাষী নির্বাচিত, কিন্তু কৃষিজমি ০ হেক্টর। অন্যের জমিতে কাজ করলে 'কৃষি শ্রমিক' নির্বাচন করুন।"
        })

    # 4. Senior citizen marked as active student
    if profile.age is not None and profile.age >= 60 and profile.occupation == "student":
        contradictions.append({
            "fields": ["age", "occupation"],
            "warning_en": f"Age {profile.age} is categorized as a senior citizen, but occupation is entered as active student. Youth education scholarships require fresh enrollment verification.",
            "warning_hi": f"आयु {profile.age} वर्ष वरिष्ठ नागरिक श्रेणी में है, लेकिन व्यवसाय 'छात्र' दर्ज है। युवा छात्रवृत्ति योजनाओं के लिए नवीन नामांकन सत्यापन आवश्यक है।",
            "warning_bn": f"বয়স {profile.age} বছর প্রবীণ নাগরিক শ্রেণির অন্তর্গত, কিন্তু পেশা 'শিক্ষার্থী' দেওয়া হয়েছে। ছাত্রবৃত্তি প্রকল্পের জন্য নতুন ভর্তির যাচাইকরণ প্রয়োজন।"
        })

    return contradictions

def evaluate_scheme(scheme: SchemeDefinition, profile: CitizenProfile, verified_reference_date: Optional[date] = None) -> SchemeEvaluationResult:
    """
    Evaluates a single scheme against a citizen profile.
    Returns SchemeEvaluationResult with status:
    - ELIGIBLE (Likely eligible)
    - NOT ELIGIBLE (Not eligible)
    - NOT SURE (Needs verification)
    - NO CURRENT RULES (Unverified, draft, needs_review, or stale)
    """
    ref_date = verified_reference_date or date.today()
    
    # 1. Verification and Review Status Check
    review_status = getattr(scheme, "review_status", "verified")
    
    # Draft and needs_review always return NO CURRENT RULES
    if review_status in ["draft", "needs_review"]:
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            scheme_name_bn=getattr(scheme, "name_bn", "") or scheme.name_en,
            level=scheme.level,
            state=scheme.state,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            benefit_bn=getattr(scheme, "benefit_bn", "") or scheme.benefit_en,
            status="NO CURRENT RULES",
            deciding_reason_en=f"Scheme rules are currently in '{review_status}' status. Pending verification before rules can be evaluated.",
            deciding_reason_hi=f"योजना के नियम वर्तमान में '{review_status}' स्थिति में हैं। सत्यापन पूर्ण होने तक नियमों का मूल्यांकन स्थगित है।",
            deciding_reason_bn=f"প্রকল্পের নিয়ম বর্তমানে '{review_status}' অবস্থায় রয়েছে। নিয়ম যাচাইয়ের অপেক্ষায় রয়েছে।",
            rule_results=[],
            satisfied_conditions=[],
            unknown_conditions=["Scheme rules pending human review / verification."],
            failed_conditions=[],
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=True,
            official_source_url=scheme.official_source_url,
            review_status=review_status,
            auto_updated_at=scheme.auto_update.applied_at if scheme.auto_update else None,
            machine_translated=scheme.machine_translated
        )

    # Check verification requirements
    if review_status == "verified":
        if not scheme.verified_by or len(scheme.verified_by) < 2:
            return SchemeEvaluationResult(
                scheme_id=scheme.id,
                scheme_name_en=scheme.name_en,
                scheme_name_hi=scheme.name_hi,
                scheme_name_bn=getattr(scheme, "name_bn", "") or scheme.name_en,
                level=scheme.level,
                state=scheme.state,
                category=scheme.category,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                benefit_bn=getattr(scheme, "benefit_bn", "") or scheme.benefit_en,
                status="NO CURRENT RULES",
                deciding_reason_en="Scheme verification incomplete (requires at least two verified reviewers).",
                deciding_reason_hi="योजना सत्यापन अपूर्ण है (कम से कम दो समीक्षकों द्वारा सत्यापन आवश्यक है)।",
                deciding_reason_bn="প্রকল্পের যাচাইকরণ অসম্পূর্ণ (কমপক্ষে দুজন পরীক্ষকের যাচাই প্রয়োজন)।",
                rule_results=[],
                satisfied_conditions=[],
                unknown_conditions=["Scheme requires two verified_by signatures."],
                failed_conditions=[],
                missing_fields=[],
                last_verified_date=scheme.last_verified_date,
                is_stale=True,
                official_source_url=scheme.official_source_url,
                review_status=review_status,
                machine_translated=scheme.machine_translated
            )

    if review_status == "auto_updated":
        if not scheme.auto_update or not scheme.auto_update.checkers_agreed:
            return SchemeEvaluationResult(
                scheme_id=scheme.id,
                scheme_name_en=scheme.name_en,
                scheme_name_hi=scheme.name_hi,
                scheme_name_bn=getattr(scheme, "name_bn", "") or scheme.name_en,
                level=scheme.level,
                state=scheme.state,
                category=scheme.category,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                benefit_bn=getattr(scheme, "benefit_bn", "") or scheme.benefit_en,
                status="NO CURRENT RULES",
                deciding_reason_en="Auto-updated scheme rules lack confirmed checker agreement block.",
                deciding_reason_hi="स्वचालित रूप से अद्यतन योजना नियमों में आवश्यक सहमति पुष्टि का अभाव है।",
                deciding_reason_bn="স্বয়ংক্রিয়ভাবে হালনাগাদ প্রকল্পের নিয়মে নিশ্চিতকরণের অভাব রয়েছে।",
                rule_results=[],
                satisfied_conditions=[],
                unknown_conditions=["Pending verification."],
                failed_conditions=[],
                missing_fields=[],
                last_verified_date=scheme.last_verified_date,
                is_stale=True,
                official_source_url=scheme.official_source_url,
                review_status=review_status,
                machine_translated=scheme.machine_translated
            )

    # Check Staleness threshold
    try:
        scheme_date = datetime.strptime(scheme.last_verified_date, "%Y-%m-%d").date()
        age_days = (ref_date - scheme_date).days
        is_stale = age_days > scheme.max_allowed_age_days
    except Exception:
        is_stale = True

    if is_stale or not scheme.rules:
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            scheme_name_bn=getattr(scheme, "name_bn", "") or scheme.name_en,
            level=scheme.level,
            state=scheme.state,
            category=scheme.category,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            benefit_bn=getattr(scheme, "benefit_bn", "") or scheme.benefit_en,
            status="NO CURRENT RULES",
            deciding_reason_en="Scheme rules are currently unverified, incomplete or outdated. Cannot generate definitive eligibility.",
            deciding_reason_hi="योजना के नियम वर्तमान में असत्यापित, अपूर्ण या पुराने हैं। निश्चित पात्रता उत्पन्न नहीं की जा सकती।",
            deciding_reason_bn="প্রকল্পের নিয়মাবলী বর্তমানে যাচাইহীন, অসম্পূর্ণ বা মেয়াদোত্তীর্ণ।",
            rule_results=[],
            satisfied_conditions=[],
            unknown_conditions=["Scheme rules pending official audit/verification."],
            failed_conditions=[],
            missing_fields=[],
            last_verified_date=scheme.last_verified_date,
            is_stale=True,
            official_source_url=scheme.official_source_url,
            review_status=review_status,
            auto_updated_at=scheme.auto_update.applied_at if scheme.auto_update else None,
            machine_translated=scheme.machine_translated
        )

    # 2. State Applicability (Engine Rule)
    rule_results: List[RuleEvaluationResult] = []
    missing_fields: List[str] = []
    satisfied_conditions_en: List[str] = []
    satisfied_conditions_hi: List[str] = []
    satisfied_conditions_bn: List[str] = []
    unknown_conditions_en: List[str] = []
    unknown_conditions_hi: List[str] = []
    unknown_conditions_bn: List[str] = []
    failed_conditions_en: List[str] = []
    failed_conditions_hi: List[str] = []
    failed_conditions_bn: List[str] = []

    # Implicit Engine Rule: State schemes get an implicit rule state eq <scheme.state>
    if scheme.level == "state":
        citizen_state_code = profile.get_normalized_state_code()
        expected_state_code = (scheme.state or "").upper()

        if citizen_state_code is None or citizen_state_code == "unknown":
            state_res = RuleEvaluationResult(
                field="state",
                operator="eq",
                expected_value=expected_state_code,
                actual_value=profile.state,
                outcome="UNKNOWN",
                reason_en=f"Scheme applies specifically to residents of {expected_state_code}. Citizen state is unknown or not provided.",
                reason_hi=f"यह योजना केवल {expected_state_code} के निवासियों के लिए है। नागरिक का राज्य अज्ञात या प्रदान नहीं किया गया है।",
                reason_bn=f"এই প্রকল্পটি বিশেষভাবে {expected_state_code} এর বাসিন্দাদের জন্য প্রযোজ্য। নাগরিকের রাজ্য অজানা বা প্রদান করা হয়নি।"
            )
            rule_results.append(state_res)
            missing_fields.append("state")
            unknown_conditions_en.append(state_res.reason_en)
            unknown_conditions_hi.append(state_res.reason_hi)
            unknown_conditions_bn.append(state_res.reason_bn or "")
        elif citizen_state_code != expected_state_code:
            state_res = RuleEvaluationResult(
                field="state",
                operator="eq",
                expected_value=expected_state_code,
                actual_value=citizen_state_code,
                outcome="FAIL",
                reason_en=f"Scheme applies specifically to {expected_state_code} residents. Citizen state is {citizen_state_code}.",
                reason_hi=f"यह योजना केवल {expected_state_code} के निवासियों के लिए है। नागरिक {citizen_state_code} के निवासी हैं।",
                reason_bn=f"এই প্রকল্প শুধুমাত্র {expected_state_code} এর বাসিন্দাদের জন্য। নাগরিকের রাজ্য {citizen_state_code}।"
            )
            rule_results.append(state_res)
            failed_conditions_en.append(state_res.reason_en)
            failed_conditions_hi.append(state_res.reason_hi)
            failed_conditions_bn.append(state_res.reason_bn or "")
        else:
            state_res = RuleEvaluationResult(
                field="state",
                operator="eq",
                expected_value=expected_state_code,
                actual_value=citizen_state_code,
                outcome="PASS",
                reason_en=f"Satisfies state residency requirement ({expected_state_code}).",
                reason_hi=f"राज्य निवास की आवश्यकता पूरी करता है ({expected_state_code})।",
                reason_bn=f"রাজ্যের স্থায়ী বসবাসের শর্ত পূরণ করে ({expected_state_code})।"
            )
            rule_results.append(state_res)
            satisfied_conditions_en.append(state_res.reason_en)
            satisfied_conditions_hi.append(state_res.reason_hi)
            satisfied_conditions_bn.append(state_res.reason_bn or "")

    # 3. Evaluate Rule Suite
    for rule in scheme.rules:
        res = evaluate_single_rule(rule, profile)
        rule_results.append(res)

        if res.outcome == "PASS":
            satisfied_conditions_en.append(res.reason_en)
            satisfied_conditions_hi.append(res.reason_hi)
            satisfied_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
        elif res.outcome == "FAIL":
            failed_conditions_en.append(res.reason_en)
            failed_conditions_hi.append(res.reason_hi)
            failed_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
        elif res.outcome == "UNKNOWN":
            unknown_conditions_en.append(res.reason_en)
            unknown_conditions_hi.append(res.reason_hi)
            unknown_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
            if res.field not in missing_fields:
                missing_fields.append(res.field)

    # 4. Final Verdict Mechanical Synthesis
    has_failed = len(failed_conditions_en) > 0
    has_unknown = len(unknown_conditions_en) > 0

    if has_failed:
        status = "NOT ELIGIBLE"
        deciding_reason_en = failed_conditions_en[0]
        deciding_reason_hi = failed_conditions_hi[0]
        deciding_reason_bn = failed_conditions_bn[0]
    elif has_unknown:
        status = "NOT SURE"
        deciding_reason_en = unknown_conditions_en[0]
        deciding_reason_hi = unknown_conditions_hi[0]
        deciding_reason_bn = unknown_conditions_bn[0]
    else:
        status = "ELIGIBLE"
        deciding_reason_en = f"All {len(satisfied_conditions_en)} eligibility criteria satisfied based on confirmed profile."
        deciding_reason_hi = f"पुष्ट प्रोफ़ाइल के आधार पर सभी {len(satisfied_conditions_hi)} पात्रता मानदंड पूरे हुए।"
        deciding_reason_bn = f"নিশ্চিত প্রোফাইলের ভিত্তিতে সমস্ত {len(satisfied_conditions_bn)} যোগ্যতার মানদণ্ড পূরণ হয়েছে।"

    return SchemeEvaluationResult(
        scheme_id=scheme.id,
        scheme_name_en=scheme.name_en,
        scheme_name_hi=scheme.name_hi,
        scheme_name_bn=getattr(scheme, "name_bn", "") or scheme.name_en,
        level=scheme.level,
        state=scheme.state,
        category=scheme.category,
        benefit_en=scheme.benefit_en,
        benefit_hi=scheme.benefit_hi,
        benefit_bn=getattr(scheme, "benefit_bn", "") or scheme.benefit_en,
        status=status,
        deciding_reason_en=deciding_reason_en,
        deciding_reason_hi=deciding_reason_hi,
        deciding_reason_bn=deciding_reason_bn,
        rule_results=rule_results,
        satisfied_conditions=satisfied_conditions_en,
        unknown_conditions=unknown_conditions_en,
        failed_conditions=failed_conditions_en,
        satisfied_conditions_en=satisfied_conditions_en,
        satisfied_conditions_hi=satisfied_conditions_hi,
        satisfied_conditions_bn=satisfied_conditions_bn,
        unknown_conditions_en=unknown_conditions_en,
        unknown_conditions_hi=unknown_conditions_hi,
        unknown_conditions_bn=unknown_conditions_bn,
        failed_conditions_en=failed_conditions_en,
        failed_conditions_hi=failed_conditions_hi,
        failed_conditions_bn=failed_conditions_bn,
        missing_fields=missing_fields,
        last_verified_date=scheme.last_verified_date,
        is_stale=False,
        official_source_url=scheme.official_source_url,
        review_status=review_status,
        auto_updated_at=scheme.auto_update.applied_at if scheme.auto_update else None,
        machine_translated=scheme.machine_translated
    )

def evaluate_all_schemes(schemes: List[SchemeDefinition], profile: CitizenProfile, verified_reference_date: Optional[date] = None) -> OverallEvaluationResponse:
    """
    Evaluates all schemes deterministically.
    Categorizes results strictly into 4 disjoint lists:
    1. Eligible
    2. Not sure
    3. Not eligible
    4. No current rules
    """
    eligible = []
    not_sure = []
    not_eligible = []
    no_rules = []

    for scheme in schemes:
        res = evaluate_scheme(scheme, profile, verified_reference_date)
        if res.status == "ELIGIBLE":
            eligible.append(res)
        elif res.status == "NOT ELIGIBLE":
            not_eligible.append(res)
        elif res.status == "NOT SURE":
            not_sure.append(res)
        elif res.status == "NO CURRENT RULES":
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
