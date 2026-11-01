from typing import List, Dict, Any, Optional
from datetime import date, datetime
from ..models.scheme import SchemeDefinition
from ..models.profile import CitizenProfile
from ..models.evaluation import SchemeEvaluationResult, OverallEvaluationResponse, RuleEvaluationResult
from .rules import evaluate_single_rule
import re

STATE_NAMES = {
    "MP": {"en": "Madhya Pradesh", "hi": "मध्य प्रदेश", "bn": "মধ্যপ্রদেশ", "mr": "मध्य प्रदेश"},
    "MH": {"en": "Maharashtra", "hi": "महाराष्ट्र", "bn": "মহারাষ্ট্র", "mr": "महाराष्ट्र"},
    "WB": {"en": "West Bengal", "hi": "पश्चिम बंगाल", "bn": "পশ্চিমবঙ্গ", "mr": "पश्चिम बंगाल"},
    "UP": {"en": "Uttar Pradesh", "hi": "उत्तर प्रदेश", "bn": "উত্তরপ্রদেশ", "mr": "उत्तर प्रदेश"},
    "PB": {"en": "Punjab", "hi": "पंजाब", "bn": "পাঞ্জাব", "mr": "पंजाब"},
    "SK": {"en": "Sikkim", "hi": "सिक्किम", "bn": "সিকিম", "mr": "सिक्किम"},
    "DL": {"en": "Delhi", "hi": "दिल्ली", "bn": "দিল্লি", "mr": "दिल्ली"},
    "RJ": {"en": "Rajasthan", "hi": "राजस्थान", "bn": "রাজস্থান", "mr": "राजस्थान"},
    "BR": {"en": "Bihar", "hi": "बिहार", "bn": "বিহার", "mr": "बिहार"},
}

def evaluate_single_scheme(scheme: SchemeDefinition, profile: CitizenProfile, ref_date: Optional[date] = None) -> SchemeEvaluationResult:
    """
    Evaluates a single scheme against a citizen profile deterministically.
    Generates full multilingual results in English, Hindi, Bengali, and Marathi.
    """
    if ref_date is None:
        ref_date = date.today()
    name_bn = getattr(scheme, "name_bn", "") or scheme.name_en
    name_mr = getattr(scheme, "name_mr", "") or scheme.name_en
    benefit_bn = getattr(scheme, "benefit_bn", "") or scheme.benefit_en
    benefit_mr = getattr(scheme, "benefit_mr", "") or scheme.benefit_en
    cat_hi = getattr(scheme, "category_hi", scheme.category)
    cat_bn = getattr(scheme, "category_bn", scheme.category)
    cat_mr = getattr(scheme, "category_mr", scheme.category)

    # 1. Verification and Review Status Check
    review_status = getattr(scheme, "review_status", "verified")
    
    # Draft and needs_review always return NO CURRENT RULES
    if review_status in ["draft", "needs_review"]:
        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            scheme_name_en=scheme.name_en,
            scheme_name_hi=scheme.name_hi,
            scheme_name_bn=name_bn,
            scheme_name_mr=name_mr,
            level=scheme.level,
            state=scheme.state,
            category=scheme.category,
            category_hi=cat_hi,
            category_bn=cat_bn,
            category_mr=cat_mr,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            benefit_bn=benefit_bn,
            benefit_mr=benefit_mr,
            status="NO CURRENT RULES",
            deciding_reason_en=f"Scheme rules are currently in '{review_status}' status. Pending verification before rules can be evaluated.",
            deciding_reason_hi=f"योजना के नियम वर्तमान में '{review_status}' स्थिति में हैं। सत्यापन पूर्ण होने तक नियमों का मूल्यांकन स्थगित है।",
            deciding_reason_bn=f"প্রকল্পের নিয়ম বর্তমানে '{review_status}' অবস্থায় রয়েছে। নিয়ম যাচাইয়ের অপেক্ষায় রয়েছে।",
            deciding_reason_mr=f"योजनेचे नियम सध्या '{review_status}' स्थितीत आहेत. नियमांचे मूल्यमापन करण्यापूर्वी पडताळणी प्रलंबित आहे.",
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
                scheme_name_bn=name_bn,
                scheme_name_mr=name_mr,
                level=scheme.level,
                state=scheme.state,
                category=scheme.category,
                category_hi=cat_hi,
                category_bn=cat_bn,
                category_mr=cat_mr,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                benefit_bn=benefit_bn,
                benefit_mr=benefit_mr,
                status="NO CURRENT RULES",
                deciding_reason_en="Scheme verification incomplete (requires at least two verified reviewers).",
                deciding_reason_hi="योजना सत्यापन अपूर्ण है (कम से कम दो समीक्षकों द्वारा सत्यापन आवश्यक है)।",
                deciding_reason_bn="প্রকল্পের যাচাইকরণ অসম্পূর্ণ (কমপক্ষে দুজন পরীক্ষকের যাচাই প্রয়োজন)।",
                deciding_reason_mr="योजना पडताळणी अपूर्ण आहे (किमान दोन पडताळणीकारांची स्वाक्षरी आवश्यक आहे).",
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
                scheme_name_bn=name_bn,
                scheme_name_mr=name_mr,
                level=scheme.level,
                state=scheme.state,
                category=scheme.category,
                category_hi=cat_hi,
                category_bn=cat_bn,
                category_mr=cat_mr,
                benefit_en=scheme.benefit_en,
                benefit_hi=scheme.benefit_hi,
                benefit_bn=benefit_bn,
                benefit_mr=benefit_mr,
                status="NO CURRENT RULES",
                deciding_reason_en="Auto-updated scheme rules lack confirmed checker agreement block.",
                deciding_reason_hi="स्वचालित रूप से अद्यतन योजना नियमों में आवश्यक सहमति पुष्टि का अभाव है।",
                deciding_reason_bn="স্বয়ংক্রিয়ভাবে হালনাগাদ প্রকল্পের নিয়মে নিশ্চিতকরণের অভাব রয়েছে।",
                deciding_reason_mr="स्वयंचलितपणे अद्यतनित केलेल्या योजनेच्या नियमांमध्ये पडताळणीची पुष्टी झालेली नाही.",
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
            scheme_name_bn=name_bn,
            scheme_name_mr=name_mr,
            level=scheme.level,
            state=scheme.state,
            category=scheme.category,
            category_hi=cat_hi,
            category_bn=cat_bn,
            category_mr=cat_mr,
            benefit_en=scheme.benefit_en,
            benefit_hi=scheme.benefit_hi,
            benefit_bn=benefit_bn,
            benefit_mr=benefit_mr,
            status="NO CURRENT RULES",
            deciding_reason_en="Scheme rules are currently unverified, incomplete or outdated. Cannot generate definitive eligibility.",
            deciding_reason_hi="योजना के नियम वर्तमान में असत्यापित, अपूर्ण या पुराने हैं। निश्चित पात्रता उत्पन्न नहीं की जा सकती।",
            deciding_reason_bn="প্রকল্পের নিয়মাবলী বর্তমানে যাচাইহীন, অসম্পূর্ণ বা মেয়াদোত্তীর্ণ।",
            deciding_reason_mr="योजनेचे नियम सध्या असत्यापित, अपूर्ण किंवा कालबाह्य आहेत. निश्चित पात्रता ठरवता येत नाही.",
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
    satisfied_conditions_mr: List[str] = []
    unknown_conditions_en: List[str] = []
    unknown_conditions_hi: List[str] = []
    unknown_conditions_bn: List[str] = []
    unknown_conditions_mr: List[str] = []
    failed_conditions_en: List[str] = []
    failed_conditions_hi: List[str] = []
    failed_conditions_bn: List[str] = []
    failed_conditions_mr: List[str] = []

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
                reason_bn=f"এই প্রকল্পটি বিশেষভাবে {expected_state_code} এর বাসিন্দাদের জন্য প্রযোজ্য। নাগরিকের রাজ্য অজানা বা প্রদান করা হয়নি।",
                reason_mr=f"ही योजना केवळ {expected_state_code} च्या रहिवाशांसाठी लागू आहे. नागरिकाचे राज्य अज्ञात आहे किंवा प्रदान केलेले नाही."
            )
            rule_results.append(state_res)
            missing_fields.append("state")
            unknown_conditions_en.append(state_res.reason_en)
            unknown_conditions_hi.append(state_res.reason_hi)
            unknown_conditions_bn.append(state_res.reason_bn or "")
            unknown_conditions_mr.append(state_res.reason_mr or "")
        elif citizen_state_code != expected_state_code:
            state_res = RuleEvaluationResult(
                field="state",
                operator="eq",
                expected_value=expected_state_code,
                actual_value=citizen_state_code,
                outcome="FAIL",
                reason_en=f"Scheme applies specifically to {expected_state_code} residents. Citizen state is {citizen_state_code}.",
                reason_hi=f"यह योजना केवल {expected_state_code} के निवासियों के लिए है। नागरिक {citizen_state_code} के निवासी हैं।",
                reason_bn=f"এই প্রকল্প শুধুমাত্র {expected_state_code} এর বাসিন্দাদের জন্য। নাগরিকের রাজ্য {citizen_state_code}।",
                reason_mr=f"ही योजना केवळ {expected_state_code} च्या रहिवाशांसाठी आहे. नागरिक {citizen_state_code} चे रहिवासी आहेत."
            )
            rule_results.append(state_res)
            failed_conditions_en.append(state_res.reason_en)
            failed_conditions_hi.append(state_res.reason_hi)
            failed_conditions_bn.append(state_res.reason_bn or "")
            failed_conditions_mr.append(state_res.reason_mr or "")
        else:
            state_res = RuleEvaluationResult(
                field="state",
                operator="eq",
                expected_value=expected_state_code,
                actual_value=citizen_state_code,
                outcome="PASS",
                reason_en=f"Satisfies state residency requirement ({expected_state_code}).",
                reason_hi=f"राज्य निवास की आवश्यकता पूरी करता है ({expected_state_code})।",
                reason_bn=f"রাজ্যের স্থায়ী বসবাসের শর্ত পূরণ করে ({expected_state_code})।",
                reason_mr=f"राज्य निवासाची आवश्यकता पूर्ण करते ({expected_state_code})."
            )
            rule_results.append(state_res)
            satisfied_conditions_en.append(state_res.reason_en)
            satisfied_conditions_hi.append(state_res.reason_hi)
            satisfied_conditions_bn.append(state_res.reason_bn or "")
            satisfied_conditions_mr.append(state_res.reason_mr or "")

    # 3. Evaluate Rule Suite
    for rule in scheme.rules:
        res = evaluate_single_rule(rule, profile)
        rule_results.append(res)

        if res.outcome == "PASS":
            satisfied_conditions_en.append(res.reason_en)
            satisfied_conditions_hi.append(res.reason_hi)
            satisfied_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
            satisfied_conditions_mr.append(getattr(res, "reason_mr", "") or res.reason_en)
        elif res.outcome == "FAIL":
            failed_conditions_en.append(res.reason_en)
            failed_conditions_hi.append(res.reason_hi)
            failed_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
            failed_conditions_mr.append(getattr(res, "reason_mr", "") or res.reason_en)
        elif res.outcome == "UNKNOWN":
            unknown_conditions_en.append(res.reason_en)
            unknown_conditions_hi.append(res.reason_hi)
            unknown_conditions_bn.append(getattr(res, "reason_bn", "") or res.reason_en)
            unknown_conditions_mr.append(getattr(res, "reason_mr", "") or res.reason_en)
            if res.field not in missing_fields:
                missing_fields.append(res.field)

    # 4. Final Verdict Mechanical Synthesis
    has_failed = len(failed_conditions_en) > 0
    has_unknown = len(unknown_conditions_en) > 0

    if has_failed:
        status = "NOT ELIGIBLE"
        deciding_reason_en = failed_conditions_en[0]
        deciding_reason_hi = failed_conditions_hi[0]
        deciding_reason_bn = failed_conditions_bn[0] if failed_conditions_bn else failed_conditions_en[0]
        deciding_reason_mr = failed_conditions_mr[0] if failed_conditions_mr else failed_conditions_en[0]
    elif has_unknown:
        status = "NOT SURE"
        deciding_reason_en = unknown_conditions_en[0]
        deciding_reason_hi = unknown_conditions_hi[0]
        deciding_reason_bn = unknown_conditions_bn[0] if unknown_conditions_bn else unknown_conditions_en[0]
        deciding_reason_mr = unknown_conditions_mr[0] if unknown_conditions_mr else unknown_conditions_en[0]
    else:
        status = "ELIGIBLE"
        deciding_reason_en = f"All {len(satisfied_conditions_en)} eligibility criteria satisfied based on confirmed profile."
        deciding_reason_hi = f"पुष्ट प्रोफ़ाइल के आधार पर सभी {len(satisfied_conditions_hi)} पात्रता मानदंड पूरे हुए।"
        deciding_reason_bn = f"নিশ্চিত প্রোফাইলের ভিত্তিতে সমস্ত {len(satisfied_conditions_bn)} যোগ্যতার মানদণ্ড পূরণ হয়েছে।"
        deciding_reason_mr = f"पुष्टी केलेल्या प्रोफाइलवर आधारित सर्व {len(satisfied_conditions_mr)} पात्रता निकष पूर्ण झाले आहेत."

    return SchemeEvaluationResult(
        scheme_id=scheme.id,
        scheme_name_en=scheme.name_en,
        scheme_name_hi=scheme.name_hi,
        scheme_name_bn=name_bn,
        scheme_name_mr=name_mr,
        level=scheme.level,
        state=scheme.state,
        category=scheme.category,
        category_hi=cat_hi,
        category_bn=cat_bn,
        category_mr=cat_mr,
        benefit_en=scheme.benefit_en,
        benefit_hi=scheme.benefit_hi,
        benefit_bn=benefit_bn,
        benefit_mr=benefit_mr,
        status=status,
        deciding_reason_en=deciding_reason_en,
        deciding_reason_hi=deciding_reason_hi,
        deciding_reason_bn=deciding_reason_bn,
        deciding_reason_mr=deciding_reason_mr,
        rule_results=rule_results,
        satisfied_conditions=satisfied_conditions_en,
        unknown_conditions=unknown_conditions_en,
        failed_conditions=failed_conditions_en,
        satisfied_conditions_en=satisfied_conditions_en,
        satisfied_conditions_hi=satisfied_conditions_hi,
        satisfied_conditions_bn=satisfied_conditions_bn,
        satisfied_conditions_mr=satisfied_conditions_mr,
        unknown_conditions_en=unknown_conditions_en,
        unknown_conditions_hi=unknown_conditions_hi,
        unknown_conditions_bn=unknown_conditions_bn,
        unknown_conditions_mr=unknown_conditions_mr,
        failed_conditions_en=failed_conditions_en,
        failed_conditions_hi=failed_conditions_hi,
        failed_conditions_bn=failed_conditions_bn,
        failed_conditions_mr=failed_conditions_mr,
        missing_fields=missing_fields,
        last_verified_date=scheme.last_verified_date,
        is_stale=False,
        official_source_url=scheme.official_source_url,
        review_status=review_status,
        auto_updated_at=scheme.auto_update.applied_at if scheme.auto_update else None,
        machine_translated=scheme.machine_translated
    )

evaluate_scheme = evaluate_single_scheme

def detect_profile_contradictions(profile: CitizenProfile) -> List[Dict[str, Any]]:
    """
    Profile contradiction engine detects incompatible claims:
    e.g. Underage widow, high income with BPL card, cultivator farmer with 0 land.
    """
    contradictions = []
    # 1. Underage widow / married
    if profile.age is not None and profile.age < 18 and profile.marital_status in ["widow", "married", "divorced"]:
        contradictions.append({
            "type": "underage_marital_status",
            "fields": ["age", "marital_status"],
            "message_en": "Citizen is a minor (under 18) but has marital status indicating marriage/widowhood.",
            "message_hi": "नागरिक नाबालिग है (18 वर्ष से कम) लेकिन वैवाहिक स्थिति विवाह/विधवा होने का संकेत देती है।",
            "message_bn": "নাগরিক অপ্রাপ্তবয়স্ক (১৮ বছরের কম) কিন্তু বৈবাহিক অবস্থা বিবাহিত/বিধবা নির্দেশ করে।",
            "message_mr": "नागरिक अल्पवयीन आहे (१८ वर्षांखालील) परंतु वैवाहिक स्थिती विवाह/विधवा असल्याचे दर्शवते."
        })
    # 2. High income with BPL card
    if profile.annual_income is not None and profile.annual_income > 250000.0 and profile.bpl_card_holder is True:
        contradictions.append({
            "type": "high_income_bpl",
            "fields": ["annual_income", "bpl_card_holder"],
            "message_en": "High annual income reported along with BPL card holder status.",
            "message_hi": "बीपीएल कार्डधारक स्थिति के साथ उच्च वार्षिक आय दर्ज की गई है।",
            "message_bn": "বিপিএল কার্ড থাকার পাশাপাশি উচ্চ বার্ষিক আয় রিপোর্ট করা হয়েছে।",
            "message_mr": "बीपीएल कार्डधारक असण्यासोबत उच्च वार्षिक उत्पन्न नोंदवले आहे."
        })
    # 3. Farmer with 0 landholding
    if profile.occupation == "farmer" and profile.landholding_hectares is not None and profile.landholding_hectares == 0.0:
        contradictions.append({
            "type": "farmer_zero_land",
            "fields": ["occupation", "landholding_hectares"],
            "message_en": "Occupation reported as farmer, but landholding is reported as 0 hectares.",
            "message_hi": "व्यवसाय किसान दर्ज किया गया है, लेकिन भूमि 0 हेक्टेयर दर्ज की गई है।",
            "message_bn": "পেশা কৃষক হিসেবে বলা হয়েছে, কিন্তু জমির পরিমাণ ০ হেক্টর।",
            "message_mr": "व्यवसाय शेतकरी नोंदवला आहे, परंतु शेतजमीन ० हेक्टर नोंदवली आहे."
        })
    return contradictions

def is_scheme_relevant_to_profile(scheme: SchemeDefinition, profile: CitizenProfile) -> bool:
    """
    Checks if a scheme is relevant to the citizen's core demographic / persona.
    Prevents cluttering Not Eligible / Not Sure lists with obviously irrelevant schemes
    (e.g., student scholarships for a 52-year-old widow, or farmer schemes for a non-farmer).
    """
    # 1. Farmer schemes: If citizen has specified an occupation that is NOT farmer, farmer-only schemes are irrelevant
    scheme_requires_farmer = any(
        rule.field == "occupation" and rule.operator in ["eq", "in"] and "farmer" in str(rule.value)
        for rule in scheme.rules
    )
    if scheme_requires_farmer and profile.occupation and profile.occupation != "farmer":
        return False

    # 2. Student / Education schemes: If citizen has specified an occupation that is NOT student (or age >= 35), youth scholarships are irrelevant
    scheme_requires_student = any(
        (rule.field == "occupation" and "student" in str(rule.value)) or
        (rule.field == "enrolled_higher_education" and rule.value is True) or
        (rule.field == "student_class12_marks_percent")
        for rule in scheme.rules
    )
    if scheme_requires_student:
        if (profile.occupation and profile.occupation != "student") or (profile.age and profile.age >= 35):
            return False

    # 3. Female / Widow exclusive schemes: If citizen is male, exclusive female schemes are irrelevant
    scheme_requires_female = any(
        (rule.field == "gender" and rule.value == "female") or
        (rule.field == "marital_status" and rule.value == "widow")
        for rule in scheme.rules
    )
    if scheme_requires_female and profile.gender and profile.gender == "male":
        return False

    return True

def evaluate_all_schemes(schemes: List[SchemeDefinition], profile: CitizenProfile, verified_reference_date: Optional[date] = None) -> OverallEvaluationResponse:
    """
    Evaluates all schemes deterministically.
    Categorizes results strictly into 4 disjoint lists:
    1. Eligible
    2. Not sure
    3. Not eligible
    4. No current rules
    Filters out schemes irrelevant to citizen's persona from not_sure/not_eligible.
    """
    ref_date = verified_reference_date or date.today()
    eligible = []
    not_sure = []
    not_eligible = []
    no_rules = []

    for scheme in schemes:
        res = evaluate_single_scheme(scheme, profile, ref_date)
        res.is_relevant_to_persona = is_scheme_relevant_to_profile(scheme, profile)
        
        if res.status == "ELIGIBLE":
            eligible.append(res)
        elif res.status == "NOT SURE":
            not_sure.append(res)
        elif res.status == "NOT ELIGIBLE":
            not_eligible.append(res)
        elif res.status == "NO CURRENT RULES":
            no_rules.append(res)

    # Detect Mutual Exclusion Contradictions
    active_contradictions = []
    all_evaluated = eligible + not_sure + not_eligible + no_rules
    evaluated_map = {s.scheme_id: s for s in all_evaluated}

    for res in eligible:
        conflicts = getattr(res, "conflicting_with", [])
        for conf_id in conflicts:
            if conf_id in evaluated_map:
                conf_res = evaluated_map[conf_id]
                if conf_res.status == "ELIGIBLE":
                    active_contradictions.append({
                        "scheme_a": res.scheme_id,
                        "scheme_a_name": res.scheme_name_en,
                        "scheme_b": conf_res.scheme_id,
                        "scheme_b_name": conf_res.scheme_name_en,
                        "reason_en": f"Citizen cannot simultaneously benefit from both {res.scheme_name_en} and {conf_res.scheme_name_en}.",
                        "reason_hi": f"नागरिक {res.scheme_name_hi} और {conf_res.scheme_name_hi} दोनों से एक साथ लाभ प्राप्त नहीं कर सकता।",
                        "reason_bn": f"নাগরিক একসাথে {res.scheme_name_bn} এবং {conf_res.scheme_name_bn} উভয় থেকে সুবিধা গ্রহণ করতে পারবেন না।",
                        "reason_mr": f"नागरिक एकाच वेळी {res.scheme_name_mr} आणि {conf_res.scheme_name_mr} या दोन्ही योजनांचा लाभ घेऊ शकत नाही."
                    })

    return OverallEvaluationResponse(
        eligible=eligible,
        not_sure=not_sure,
        not_eligible=not_eligible,
        no_rules=no_rules,
        total_evaluated=len(schemes),
        active_profile_summary=profile.model_dump(),
        contradictions=active_contradictions
    )
