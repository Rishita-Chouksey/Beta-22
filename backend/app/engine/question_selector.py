from typing import List, Dict, Any, Optional
from collections import Counter
from pathlib import Path
import json
from ..models.profile import CitizenProfile
from ..models.scheme import SchemeDefinition
from ..models.api import NextQuestion, NextQuestionResponse, QuestionOption
from .evaluator import evaluate_scheme

FIELD_EASINESS_RANK = {
    "state": 1,
    "gender": 2,
    "age": 3,
    "marital_status": 4,
    "residence_type": 5,
    "occupation": 6,
    "category": 7,
    "bpl_card_holder": 8,
    "has_pucca_house": 9,
    "enrolled_higher_education": 10,
    "student_class12_marks_percent": 11,
    "landholding_hectares": 12,
    "annual_income": 13,
    "is_institutional_landholder": 14,
    "holds_constitutional_post": 15,
}

# Load from data/questions.json if available
def _load_questions_registry() -> Dict[str, Dict[str, Any]]:
    # Check root data/questions.json
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "questions.json",
        Path(__file__).resolve().parent.parent / "data" / "questions.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    reg = {}
                    for q in data.get("questions", []):
                        reg[q["field"]] = q
                    return reg
            except Exception:
                pass
    return {}

_FILE_QUESTION_REGISTRY = _load_questions_registry()

QUESTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "state": {
        "title_en": "Which state or Union Territory do you reside in?",
        "title_hi": "आप किस राज्य या केंद्र शासित प्रदेश के निवासी हैं?",
        "title_bn": "আপনি কোন রাজ্য বা কেন্দ্রশাসিত অঞ্চলের বাসিন্দা?",
        "subtitle_en": "Government welfare schemes are often specific to your state of domicile.",
        "subtitle_hi": "कई सरकारी योजनाएं आपके मूल निवास राज्य के अनुसार होती हैं।",
        "subtitle_bn": "অনেক সরকারি কল্যাণমূলক প্রকল্প আপনার স্থায়ী বসবাসের রাজ্যের নির্দিষ্ট।",
        "explanation_en": "Central schemes apply all over India, but state welfare programs require domicile in that specific state.",
        "explanation_hi": "केंद्रीय योजनाएं पूरे भारत में लागू होती हैं, लेकिन राज्य योजनाएं संबंधित राज्य के मूल निवासियों के लिए होती हैं।",
        "explanation_bn": "কেন্দ্রীয় প্রকল্পগুলি সমগ্র ভারতে প্রযোজ্য, তবে রাজ্য কল্যাণ প্রকল্পগুলির জন্য নির্দিষ্ট রাজ্যের বাসিন্দা হওয়া প্রয়োজন।",
        "examples_en": "Madhya Pradesh, Maharashtra, West Bengal, Uttar Pradesh, etc.",
        "examples_hi": "मध्य प्रदेश, महाराष्ट्र, पश्चिम बंगाल, उत्तर प्रदेश आदि।",
        "examples_bn": "মধ্যপ্রদেশ, মহারাষ্ট্র, পশ্চিমবঙ্গ, উত্তর প্রদেশ ইত্যাদি।",
        "type": "searchable_picker",
        "options": [
            {"value": "AP", "label_en": "Andhra Pradesh", "label_hi": "आंध्र प्रदेश", "label_bn": "অন্ধ্রপ্রদেশ", "spoken": ["andhra", "andhra pradesh"]},
            {"value": "AR", "label_en": "Arunachal Pradesh", "label_hi": "अरुणाचल प्रदेश", "label_bn": "অরুণাচল প্রদেশ", "spoken": ["arunachal"]},
            {"value": "AS", "label_en": "Assam", "label_hi": "असम", "label_bn": "অসম", "spoken": ["assam", "asom"]},
            {"value": "BR", "label_en": "Bihar", "label_hi": "बिहार", "label_bn": "বিহার", "spoken": ["bihar"]},
            {"value": "CT", "label_en": "Chhattisgarh", "label_hi": "छत्तीसगढ़", "label_bn": "ছত্তিশগড়", "spoken": ["chhattisgarh"]},
            {"value": "GA", "label_en": "Goa", "label_hi": "गोवा", "label_bn": "গোয়া", "spoken": ["goa"]},
            {"value": "GJ", "label_en": "Gujarat", "label_hi": "गुजरात", "label_bn": "গুজরাত", "spoken": ["gujarat"]},
            {"value": "HR", "label_en": "Haryana", "label_hi": "हरियाणा", "label_bn": "হরিয়ানা", "spoken": ["haryana"]},
            {"value": "HP", "label_en": "Himachal Pradesh", "label_hi": "हिमाचल प्रदेश", "label_bn": "হিমাচল প্রদেশ", "spoken": ["himachal"]},
            {"value": "JH", "label_en": "Jharkhand", "label_hi": "झारखंड", "label_bn": "ঝাড়খণ্ড", "spoken": ["jharkhand"]},
            {"value": "KA", "label_en": "Karnataka", "label_hi": "कर्नाटक", "label_bn": "কর্ণাটক", "spoken": ["karnataka"]},
            {"value": "KL", "label_en": "Kerala", "label_hi": "केरल", "label_bn": "কেরল", "spoken": ["kerala"]},
            {"value": "MP", "label_en": "Madhya Pradesh", "label_hi": "मध्य प्रदेश", "label_bn": "মধ্যপ্রদেশ", "spoken": ["madhya pradesh", "mp"]},
            {"value": "MH", "label_en": "Maharashtra", "label_hi": "महाराष्ट्र", "label_bn": "মহারাষ্ট্র", "spoken": ["maharashtra", "mh"]},
            {"value": "MN", "label_en": "Manipur", "label_hi": "मणिपुर", "label_bn": "মণিপুর", "spoken": ["manipur"]},
            {"value": "ML", "label_en": "Meghalaya", "label_hi": "मेघालय", "label_bn": "মেঘালয়", "spoken": ["meghalaya"]},
            {"value": "MZ", "label_en": "Mizoram", "label_hi": "मिजोरम", "label_bn": "মিজোরাম", "spoken": ["mizoram"]},
            {"value": "NL", "label_en": "Nagaland", "label_hi": "नागालैंड", "label_bn": "নাগাল্যান্ড", "spoken": ["nagaland"]},
            {"value": "OD", "label_en": "Odisha", "label_hi": "ओडिशा", "label_bn": "ওড়িশা", "spoken": ["odisha", "orissa"]},
            {"value": "PB", "label_en": "Punjab", "label_hi": "पंजाब", "label_bn": "পাঞ্জাব", "spoken": ["punjab"]},
            {"value": "RJ", "label_en": "Rajasthan", "label_hi": "राजस्थान", "label_bn": "রাজস্থান", "spoken": ["rajasthan"]},
            {"value": "SK", "label_en": "Sikkim", "label_hi": "सिक्किम", "label_bn": "সিকিম", "spoken": ["sikkim"]},
            {"value": "TN", "label_en": "Tamil Nadu", "label_hi": "तमिलनाडु", "label_bn": "তামিলনাড়ু", "spoken": ["tamil nadu"]},
            {"value": "TG", "label_en": "Telangana", "label_hi": "तेलंगाना", "label_bn": "তেলেঙ্গানা", "spoken": ["telangana"]},
            {"value": "TR", "label_en": "Tripura", "label_hi": "त्रिपुरा", "label_bn": "ত্রিপুরা", "spoken": ["tripura"]},
            {"value": "UP", "label_en": "Uttar Pradesh", "label_hi": "उत्तर प्रदेश", "label_bn": "উত্তর প্রদেশ", "spoken": ["uttar pradesh", "up"]},
            {"value": "UT", "label_en": "Uttarakhand", "label_hi": "उत्तराखंड", "label_bn": "উত্তরাখণ্ড", "spoken": ["uttarakhand"]},
            {"value": "WB", "label_en": "West Bengal", "label_hi": "पश्चिम बंगाल", "label_bn": "পশ্চিমবঙ্গ", "spoken": ["west bengal", "bengal", "wb"]},
            {"value": "AN", "label_en": "Andaman and Nicobar Islands", "label_hi": "अंडमान और निकोबार", "label_bn": "আন্দামান ও নিকোবর", "spoken": ["andaman"]},
            {"value": "CH", "label_en": "Chandigarh", "label_hi": "चंडीगढ़", "label_bn": "চণ্ডীগড়", "spoken": ["chandigarh"]},
            {"value": "DH", "label_en": "Dadra & Nagar Haveli and Daman & Diu", "label_hi": "दादरा नगर हवेली एवं दमन दीव", "label_bn": "দাদরা ও নগর হাভেলি এবং দমন ও দিউ", "spoken": ["daman", "diu"]},
            {"value": "DL", "label_en": "Delhi", "label_hi": "दिल्ली", "label_bn": "দিল্লি", "spoken": ["delhi"]},
            {"value": "JK", "label_en": "Jammu and Kashmir", "label_hi": "जम्मू और कश्मीर", "label_bn": "জম্মু ও কাশ্মীর", "spoken": ["kashmir", "jammu"]},
            {"value": "LA", "label_en": "Ladakh", "label_hi": "लद्दाख", "label_bn": "লাদাখ", "spoken": ["ladakh"]},
            {"value": "LD", "label_en": "Lakshadweep", "label_hi": "लक्षद्वीप", "label_bn": "লক্ষদ্বীপ", "spoken": ["lakshadweep"]},
            {"value": "PY", "label_en": "Puducherry", "label_hi": "पुडुचेरी", "label_bn": "পুদুচেরি", "spoken": ["puducherry", "pondicherry"]},
            {"value": "unknown", "label_en": "Other / Not sure", "label_hi": "अन्य / निश्चित नहीं", "label_bn": "অন্যান্য / নিশ্চিত নই", "spoken": ["other", "not sure", "unknown"]}
        ]
    },
    "occupation": {
        "title_en": "What is your primary occupation?",
        "title_hi": "आपका मुख्य व्यवसाय क्या है?",
        "title_bn": "আপনার প্রধান পেশা কি?",
        "subtitle_en": "Helps match occupation-targeted benefits (farmers, students, etc.).",
        "subtitle_hi": "व्यवसाय-विशिष्ट लाभों की पहचान में मदद करता है।",
        "subtitle_bn": "পেশাভিত্তিক সুবিধার সাথে মেলাতে সাহায্য করে।",
        "explanation_en": "Specialized welfare programs exist for farmers (PM-KISAN), college students (scholarships), and informal workers.",
        "explanation_hi": "किसानों (पीएम-किसान), कॉलेज छात्रों (छात्रवृत्ति) और असंगठित कामगारों के लिए विशिष्ट योजनाएं उपलब्ध हैं।",
        "explanation_bn": "কৃষকদের জন্য (পিএম-কিষাণ), শিক্ষার্থীদের জন্য (স্কলারশিপ) বিশেষ প্রকল্প রয়েছে।",
        "type": "single_choice",
        "options": [
            {"value": "farmer", "label_en": "Farmer / Cultivator", "label_hi": "किसान / काश्तकार", "label_bn": "কৃষক / চাষী"},
            {"value": "student", "label_en": "College Student", "label_hi": "कॉलेज छात्र / छात्रा", "label_bn": "কলেজ পড়ুয়া / শিক্ষার্থী"},
            {"value": "agricultural_worker", "label_en": "Agricultural Laborer", "label_hi": "खेतिहर मजदूर", "label_bn": "কৃষি শ্রমিক"},
            {"value": "self_employed", "label_en": "Self-employed / Small Business", "label_hi": "स्वरोजगार / छोटा व्यवसाय", "label_bn": "স্বনির্ভর / ক্ষুদ্র ব্যবসায়ী"},
            {"value": "homemaker", "label_en": "Homemaker", "label_hi": "गृहिणी", "label_bn": "গৃহিণী"},
            {"value": "unemployed", "label_en": "Unemployed / Looking for work", "label_hi": "बेरोजगार", "label_bn": "বেকার"},
            {"value": "private_job", "label_en": "Private Employment", "label_hi": "निजी नौकरी", "label_bn": "বেসরকারি চাকরি"},
            {"value": "other", "label_en": "Other", "label_hi": "अन्य", "label_bn": "অন্যান্য"}
        ]
    },
    "residence_type": {
        "title_en": "What is your residence area type?",
        "title_hi": "आपका निवास क्षेत्र किस प्रकार का है?",
        "title_bn": "আপনার বসবাসের এলাকা কোন ধরনের?",
        "subtitle_en": "Tells us whether you live in a rural village or an urban city.",
        "subtitle_hi": "यह बताता है कि आप ग्रामीण गांव में रहते हैं या शहरी क्षेत्र में।",
        "subtitle_bn": "আপনি গ্রামে থাকেন নাকি শহরে তা বোঝায়।",
        "explanation_en": "Identifies schemes dedicated specifically for village Gram Panchayat areas (like PMAY-G rural housing) versus municipal urban areas.",
        "explanation_hi": "ग्राम पंचायत क्षेत्र (जैसे पीएम आवास ग्रामीण) या नगर निगम/नगर पालिका क्षेत्र के लिए बनी योजनाओं की पहचान में मदद करता है।",
        "explanation_bn": "গ্রাম পঞ্চায়েত এলাকা বা পৌরসভা এলাকার জন্য নির্ধারিত প্রকল্প চিহ্নিত করতে সাহায্য করে।",
        "type": "single_choice",
        "options": [
            {"label_en": "Rural", "label_hi": "ग्रामीण (गांव)", "label_bn": "গ্রামীণ (গ্রাম)", "value": "rural"},
            {"label_en": "Urban", "label_hi": "शहरी (शहर/कस्बा)", "label_bn": "শহুরে (শহর)", "value": "urban"},
            {"label_en": "Not sure / Semi-urban", "label_hi": "निश्चित नहीं / अर्ध-शहरी", "label_bn": "নিশ্চিত নই / উপশহর", "value": "not_sure"}
        ]
    },
    "gender": {
        "title_en": "What is your gender?",
        "title_hi": "आपका लिंग क्या है?",
        "title_bn": "আপনার লিঙ্গ কি?",
        "type": "single_choice",
        "options": [
            {"label_en": "Female", "label_hi": "महिला", "label_bn": "মহিলা", "value": "female"},
            {"label_en": "Male", "label_hi": "पुरुष", "label_bn": "পুরুষ", "value": "male"},
            {"label_en": "Transgender / Other", "label_hi": "थर्ड जेंडर / अन्य", "label_bn": "রূপান্তরিত লিঙ্গ / অন্যান্য", "value": "transgender"}
        ]
    },
    "age": {
        "title_en": "What is your age in completed years?",
        "title_hi": "आपकी आयु कितने वर्ष है?",
        "title_bn": "আপনার বয়স কত বছর?",
        "type": "number",
        "min_val": 1,
        "max_val": 120,
        "unit": "years"
    },
    "marital_status": {
        "title_en": "What is your marital status?",
        "title_hi": "आपकी वैवाहिक स्थिति क्या है?",
        "title_bn": "আপনার বৈবাহিক অবস্থা কি?",
        "type": "single_choice",
        "options": [
            {"label_en": "Widow (Lost husband)", "label_hi": "विधवा (पति का निधन)", "label_bn": "বিধবা (স্বামীহারা)", "value": "widow"},
            {"label_en": "Married", "label_hi": "विवाहित", "label_bn": "বিবাহিত", "value": "married"},
            {"label_en": "Single / Unmarried", "label_hi": "अविवाहित", "label_bn": "অবিবাহিত", "value": "single"},
            {"label_en": "Divorced / Deserted", "label_hi": "तलाकशुदा / परित्यक्ता", "label_bn": "তালাকপ্রাপ্ত / পরিত্যক্তা", "value": "divorced"}
        ]
    },
    "landholding_hectares": {
        "title_en": "How much cultivable agricultural land does your family own (in hectares)?",
        "title_hi": "आपके परिवार के पास कितनी कृषि योग्य भूमि (हेक्टेयर में) है?",
        "title_bn": "আপনার পরিবারের আবাদযোগ্য কৃষিজমি (হেক্টরে) কত?",
        "type": "number",
        "min_val": 0.0,
        "max_val": 100.0,
        "unit": "hectares"
    },
    "annual_income": {
        "title_en": "What is your total annual family income in Rupees (₹)?",
        "title_hi": "आपके परिवार की कुल वार्षिक आय (रुपये में) कितनी है?",
        "title_bn": "আপনার পরিবারের মোট বার্ষিক আয় কত টাকা (₹)?",
        "type": "number",
        "min_val": 0.0,
        "max_val": 100000000.0,
        "unit": "INR"
    },
    "bpl_card_holder": {
        "title_en": "Does your family possess a BPL (Below Poverty Line) or Antyodaya ration card?",
        "title_hi": "क्या आपके परिवार के पास बीपीएल या अंत्योदय राशन कार्ड है?",
        "title_bn": "আপনার পরিবারের কি বিपीএল বা অন্ত্যোদয় রেশন কার্ড আছে?",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, have BPL/Antyodaya card", "label_hi": "हाँ, बीपीएल/अंत्योदय कार्ड है", "label_bn": "হ্যাঁ, বিপিএল কার্ড আছে", "value": True},
            {"label_en": "No, standard ration card or none", "label_hi": "नहीं, सामान्य राशन कार्ड है या नहीं है", "label_bn": "না, সাধারণ কার্ড আছে বা নেই", "value": False}
        ]
    },
    "student_class12_marks_percent": {
        "title_en": "What was your score percentage in the Class 12 board examination?",
        "title_hi": "12वीं बोर्ड परीक्षा में आपका प्रतिशत कितना था?",
        "title_bn": "দ্বাদশ শ্রেণির বোর্ড পরীক্ষায় আপনার শতাংশ কত ছিল?",
        "type": "number",
        "min_val": 0.0,
        "max_val": 100.0,
        "unit": "%"
    },
    "enrolled_higher_education": {
        "title_en": "Are you currently enrolled in a recognised college, university, or professional course?",
        "title_hi": "क्या आप किसी मान्यता प्राप्त कॉलेज या उच्च शिक्षण संस्थान में नामांकित हैं?",
        "title_bn": "আপনি কি কোনো স্বীকৃত কলেজ বা বিশ্ববিদ্যালয়ে পাঠরত?",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, actively enrolled in higher education", "label_hi": "हाँ, उच्च शिक्षा में नामांकित हूँ", "label_bn": "হ্যাঁ, উচ্চশিক্ষায় পাঠরত", "value": True},
            {"label_en": "No", "label_hi": "नहीं", "label_bn": "না", "value": False}
        ]
    }
}

# Override with any custom questions loaded from file
QUESTION_REGISTRY.update(_FILE_QUESTION_REGISTRY)

def select_next_question(
    arg1: Any = None,
    arg2: Any = None,
    profile: Optional[CitizenProfile] = None,
    schemes: Optional[List[SchemeDefinition]] = None,
    current_step: Optional[int] = None,
    max_questions_budget: int = 8
) -> NextQuestionResponse:
    """
    Selects the single most impactful next question based on information gain.
    Ensures early state filtering for state-specific schemes.
    """
    if isinstance(arg1, CitizenProfile):
        profile = arg1
        if isinstance(arg2, list):
            schemes = arg2
    elif isinstance(arg1, list):
        schemes = arg1
        if isinstance(arg2, CitizenProfile):
            profile = arg2

    if profile is None:
        profile = CitizenProfile()
    if schemes is None:
        from ..services.scheme_service import scheme_service
        schemes = scheme_service.get_all_schemes()

    current_answered = [f for f, v in profile.model_dump().items() if v is not None and f not in ["confirmed_fields", "skipped_fields"]]
    current_step = current_step if current_step is not None else (len(current_answered) + 1)

    if current_step > max_questions_budget:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en=f"Reached optimal question limit ({max_questions_budget}). Ready for evaluation.",
            resolved_message_hi=f"अधिकतम प्रश्न सीमा ({max_questions_budget}) पूरी हुई। पात्रता मूल्यांकन तैयार है।",
            resolved_message_bn=f"সর্বোচ্চ প্রশ্নের সীমা ({max_questions_budget}) পূর্ণ হয়েছে। মূল্যায়নের জন্য প্রস্তুত।"
        )

    # 1. Identify which schemes are currently UNDECIDED (status NOT SURE)
    undecided_schemes: List[SchemeDefinition] = []
    for s in schemes:
        review_status = getattr(s, "review_status", "verified")
        if review_status not in ["verified", "auto_updated"]:
            continue
        eval_res = evaluate_scheme(s, profile)
        if eval_res.status == "NOT SURE":
            undecided_schemes.append(s)

    if not undecided_schemes:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="All official government scheme rules have been deterministically resolved.",
            resolved_message_hi="सभी आधिकारिक सरकारी योजनाओं के नियमों का निश्चित समाधान हो चुका है।",
            resolved_message_bn="সমস্ত সরকারি প্রকল্পের নিয়মের সমাধান হয়েছে।"
        )

    # 2. Count frequency of missing/unanswered fields across remaining undecided schemes
    field_counts = Counter()
    for s in undecided_schemes:
        eval_res = evaluate_scheme(s, profile)
        for missing_f in eval_res.missing_fields:
            if missing_f in profile.skipped_fields:
                continue
            curr_val = getattr(profile, missing_f, None)
            if curr_val is None or not profile.is_field_confirmed(missing_f):
                field_counts[missing_f] += 1

    unanswered_fields = list(field_counts.keys())
    if not unanswered_fields:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="No further questions can alter the evaluation results.",
            resolved_message_hi="कोई अन्य प्रश्न परिणाम को नहीं बदल सकता।",
            resolved_message_bn="অন্য কোনো প্রশ্ন ফলাফল পরিবর্তন করতে পারবে না।"
        )

    # Sort by: 1) Frequency (descending), 2) Easiness rank (ascending)
    def sort_key(f: str):
        count = field_counts[f]
        easiness = FIELD_EASINESS_RANK.get(f, 99)
        return (-count, easiness)

    best_field = sorted(unanswered_fields, key=sort_key)[0]
    
    q_data = QUESTION_REGISTRY.get(best_field)
    if not q_data:
        q_data = {
            "title_en": f"Please provide your {best_field.replace('_', ' ')}",
            "title_hi": f"कृपया अपना {best_field.replace('_', ' ')} बताएं",
            "title_bn": f"অনুগ্রহ করে আপনার {best_field.replace('_', ' ')} প্রদান করুন",
            "subtitle_en": "Required to confirm scheme eligibility.",
            "subtitle_hi": "योजना पात्रता की पुष्टि के लिए आवश्यक।",
            "subtitle_bn": "প্রকল্পের যোগ্যতা নিশ্চিত করতে প্রয়োজন।",
            "type": "single_choice",
            "options": None
        }

    options_list = None
    if q_data.get("options"):
        options_list = [QuestionOption(**opt) for opt in q_data["options"]]

    question = NextQuestion(
        field=best_field,
        title_en=q_data["title_en"],
        title_hi=q_data["title_hi"],
        title_bn=q_data.get("title_bn", ""),
        subtitle_en=q_data.get("subtitle_en"),
        subtitle_hi=q_data.get("subtitle_hi"),
        subtitle_bn=q_data.get("subtitle_bn"),
        explanation_en=q_data.get("explanation_en"),
        explanation_hi=q_data.get("explanation_hi"),
        explanation_bn=q_data.get("explanation_bn"),
        examples_en=q_data.get("examples_en"),
        examples_hi=q_data.get("examples_hi"),
        examples_bn=q_data.get("examples_bn"),
        type=q_data["type"],
        options=options_list,
        min_val=q_data.get("min_val"),
        max_val=q_data.get("max_val"),
        unit=q_data.get("unit"),
        progress_index=current_step,
        total_estimated=min(8, max(current_step, len(unanswered_fields) + current_step - 1))
    )

    return NextQuestionResponse(
        has_more=True,
        question=question
    )
