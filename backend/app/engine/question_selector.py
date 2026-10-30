from typing import List, Dict, Any, Optional
from collections import Counter
from ..models.profile import CitizenProfile
from ..models.scheme import SchemeDefinition
from ..models.api import NextQuestion, NextQuestionResponse, QuestionOption
from .evaluator import evaluate_scheme

# Difficulty / cognitive load ranking (lower number = easier / faster to answer)
FIELD_EASINESS_RANK = {
    "state": 1,
    "gender": 2,
    "age": 3,
    "marital_status": 4,
    "occupation": 5,
    "category": 6,
    "residence_type": 7,
    "bpl_card_holder": 8,
    "has_pucca_house": 9,
    "enrolled_higher_education": 10,
    "student_class12_marks_percent": 11,
    "landholding_hectares": 12,
    "annual_income": 13,
    "is_institutional_landholder": 14,
    "holds_constitutional_post": 15,
}

QUESTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "state": {
        "title_en": "Which state do you reside in?",
        "title_hi": "आप किस राज्य के निवासी हैं?",
        "subtitle_en": "Many government schemes are state-specific.",
        "subtitle_hi": "कई सरकारी योजनाएं राज्य-विशिष्ट होती हैं।",
        "type": "single_choice",
        "options": [
            {"label_en": "Madhya Pradesh", "label_hi": "मध्य प्रदेश", "value": "Madhya Pradesh"},
            {"label_en": "Maharashtra", "label_hi": "महाराष्ट्र", "value": "Maharashtra"},
            {"label_en": "Uttar Pradesh", "label_hi": "उत्तर प्रदेश", "value": "Uttar Pradesh"},
            {"label_en": "Rajasthan", "label_hi": "राजस्थान", "value": "Rajasthan"},
            {"label_en": "Bihar", "label_hi": "बिहार", "value": "Bihar"},
            {"label_en": "Other State / UT", "label_hi": "अन्य राज्य / केंद्र शासित प्रदेश", "value": "Other"},
        ]
    },
    "gender": {
        "title_en": "What is your gender?",
        "title_hi": "आपका लिंग क्या है?",
        "subtitle_en": "Certain schemes offer dedicated support for women or transgender citizens.",
        "subtitle_hi": "कुछ योजनाएं महिलाओं या ट्रांसजेंडर नागरिकों के लिए विशेष सहायता प्रदान करती हैं।",
        "type": "single_choice",
        "options": [
            {"label_en": "Female", "label_hi": "महिला", "value": "female"},
            {"label_en": "Male", "label_hi": "पुरुष", "value": "male"},
            {"label_en": "Transgender / Other", "label_hi": "ट्रांसजेंडर / अन्य", "value": "transgender"},
        ]
    },
    "age": {
        "title_en": "What is your age in years?",
        "title_hi": "आपकी आयु कितने वर्ष है?",
        "subtitle_en": "Helps match age-bracket specific schemes like pensions, scholarships and youth funds.",
        "subtitle_hi": "पेंशन, छात्रवृत्ति और युवा योजनाओं की पात्रता निर्धारित करने में मदद करता है।",
        "type": "number",
        "min_val": 1,
        "max_val": 110,
        "unit": "years"
    },
    "marital_status": {
        "title_en": "What is your marital status?",
        "title_hi": "आपकी वैवाहिक स्थिति क्या है?",
        "subtitle_en": "Special security schemes exist for widows, single women and destitute citizens.",
        "subtitle_hi": "विधवाओं, एकल महिलाओं और निराधार नागरिकों के लिए विशेष सामाजिक सुरक्षा योजनाएं हैं।",
        "type": "single_choice",
        "options": [
            {"label_en": "Widow / Widower", "label_hi": "विधवा / विधुर", "value": "widow"},
            {"label_en": "Married", "label_hi": "विवाहित", "value": "married"},
            {"label_en": "Unmarried / Single", "label_hi": "अविवाहित", "value": "single"},
            {"label_en": "Divorced / Deserted", "label_hi": "तलाकशुदा / परित्यक्ता", "value": "divorced"},
        ]
    },
    "occupation": {
        "title_en": "What is your primary occupation or current status?",
        "title_hi": "आपका मुख्य व्यवसाय या वर्तमान स्थिति क्या है?",
        "subtitle_en": "Select the option that best describes your daily livelihood.",
        "subtitle_hi": "वह विकल्प चुनें जो आपकी आजीविका का सबसे अच्छा वर्णन करता है।",
        "type": "single_choice",
        "options": [
            {"label_en": "Farmer / Cultivator", "label_hi": "किसान / कृषक", "value": "farmer"},
            {"label_en": "College / School Student", "label_hi": "कॉलेज / स्कूल छात्र", "value": "student"},
            {"label_en": "Agricultural Laborer", "label_hi": "खेतिहर मजदूर", "value": "agricultural_worker"},
            {"label_en": "Homemaker", "label_hi": "गृहिणी", "value": "homemaker"},
            {"label_en": "Self Employed / Small Artisan", "label_hi": "स्व-रोजगार / छोटा कारीगर", "value": "self_employed"},
            {"label_en": "Unemployed / Looking for Work", "label_hi": "बेरोजगार / काम की तलाश", "value": "unemployed"},
            {"label_en": "Private / Unorganized Job", "label_hi": "निजी / असंगठित क्षेत्र में कार्य", "value": "private_job"}
        ]
    },
    "annual_income": {
        "title_en": "What is your approximate annual family income?",
        "title_hi": "आपके परिवार की अनुमानित वार्षिक आय कितनी है?",
        "subtitle_en": "Select your income range or enter the amount from your income certificate.",
        "subtitle_hi": "अपनी आय सीमा चुनें या अपने आय प्रमाण पत्र से राशि दर्ज करें।",
        "type": "single_choice",
        "options": [
            {"label_en": "Less than ₹1,00,000 (Low / BPL)", "label_hi": "₹1,00,000 से कम (कम आय / बीपीएल)", "value": 65000},
            {"label_en": "₹1,00,000 to ₹2,50,000", "label_hi": "₹1,00,000 से ₹2,50,000", "value": 180000},
            {"label_en": "₹2,50,000 to ₹6,00,000", "label_hi": "₹2,50,000 से ₹6,00,000", "value": 450000},
            {"label_en": "Above ₹6,00,000", "label_hi": "₹6,00,000 से अधिक", "value": 750000}
        ]
    },
    "landholding_hectares": {
        "title_en": "How much agricultural land does your family own?",
        "title_hi": "आपके परिवार के पास कितनी कृषि भूमि है?",
        "subtitle_en": "1 hectare is approx 2.47 acres. Small farmers possess up to 2 hectares.",
        "subtitle_hi": "1 हेक्टेयर लगभग 2.47 एकड़ होता है। लघु किसानों के पास 2 हेक्टेयर तक भूमि होती है।",
        "type": "single_choice",
        "options": [
            {"label_en": "No agricultural land (0 ha)", "label_hi": "कोई कृषि भूमि नहीं (0 हेक्टेयर)", "value": 0.0},
            {"label_en": "Small / Marginal (Up to 2 hectares)", "label_hi": "लघु एवं सीमांत (2 हेक्टेयर तक)", "value": 1.5},
            {"label_en": "Medium / Large (More than 2 hectares)", "label_hi": "मध्यम / बड़ा (2 हेक्टेयर से अधिक)", "value": 3.5}
        ]
    },
    "student_class12_marks_percent": {
        "title_en": "What was your percentage in Class 12 board exams?",
        "title_hi": "12वीं बोर्ड परीक्षा में आपका प्रतिशत कितना था?",
        "subtitle_en": "Required for merit scholarships such as MMVY (>=70% MPBSE or >=85% CBSE).",
        "subtitle_hi": "मेधावी छात्रवृत्ति (जैसे एमएमवीवाई) के लिए आवश्यक है।",
        "type": "number",
        "min_val": 33,
        "max_val": 100,
        "unit": "%"
    },
    "enrolled_higher_education": {
        "title_en": "Are you currently enrolled in an undergraduate or professional course?",
        "title_hi": "क्या आप वर्तमान में किसी स्नातक या व्यावसायिक पाठ्यक्रम में नामांकित हैं?",
        "subtitle_en": "Such as Engineering, Medical, Degree colleges, or Polytechnics.",
        "subtitle_hi": "जैसे इंजीनियरिंग, मेडिकल, डिग्री कॉलेज या पॉलिटेक्निक।",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, enrolled in Higher Education", "label_hi": "हाँ, उच्च शिक्षा में नामांकित हूँ", "value": True},
            {"label_en": "No / Not enrolled", "label_hi": "नहीं / नामांकित नहीं हूँ", "value": False}
        ]
    },
    "has_pucca_house": {
        "title_en": "Does your family own a permanent pucca house?",
        "title_hi": "क्या आपके परिवार के पास पक्का पक्का मकान है?",
        "subtitle_en": "Housing assistance schemes (PMAY) prioritize families residing in kutcha or makeshift dwellings.",
        "subtitle_hi": "आवास योजनाएं (पीएमएवाई) कच्चे मकानों में रहने वाले परिवारों को प्राथमिकता देती हैं।",
        "type": "boolean",
        "options": [
            {"label_en": "No, we live in a Kutcha / temporary house", "label_hi": "नहीं, हम कच्चे / अस्थायी मकान में रहते हैं", "value": False},
            {"label_en": "Yes, we own a Pucca house", "label_hi": "हाँ, हमारे पास पक्का मकान है", "value": True}
        ]
    },
    "bpl_card_holder": {
        "title_en": "Does your family possess a BPL / Antyodaya Ration Card?",
        "title_hi": "क्या आपके परिवार के पास बीपीएल / अंत्योदय राशन कार्ड है?",
        "subtitle_en": "Below Poverty Line verification card issued by the State Food & Civil Supplies.",
        "subtitle_hi": "खाद्य एवं नागरिक आपूर्ति विभाग द्वारा जारी गरीबी रेखा से नीचे का कार्ड।",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, we have BPL / Antyodaya Card", "label_hi": "हाँ, बीपीएल / अंत्योदय कार्ड है", "value": True},
            {"label_en": "No BPL Card", "label_hi": "बीपीएल कार्ड नहीं है", "value": False}
        ]
    },
    "is_institutional_landholder": {
        "title_en": "Is the agricultural land held under any institutional or trust name?",
        "title_hi": "क्या कृषि भूमि किसी संस्थागत या ट्रस्ट के नाम पर है?",
        "subtitle_en": "Schemes like PM-KISAN only benefit individual farmer families.",
        "subtitle_hi": "पीएम-किसान जैसी योजनाएं केवल व्यक्तिगत किसान परिवारों को लाभ देती हैं।",
        "type": "boolean",
        "options": [
            {"label_en": "No, land is individually / family owned", "label_hi": "नहीं, भूमि व्यक्तिगत / परिवार के नाम है", "value": False},
            {"label_en": "Yes, land is institutionally held", "label_hi": "हाँ, भूमि संस्थागत है", "value": True}
        ]
    },
    "holds_constitutional_post": {
        "title_en": "Does anyone in your immediate family hold a government job or constitutional post?",
        "title_hi": "क्या आपके परिवार में कोई सरकारी नौकरी या संवैधानिक पद पर है?",
        "subtitle_en": "Includes regular government employees, MPs, MLAs, and municipal chairpersons.",
        "subtitle_hi": "नियमित सरकारी कर्मचारी, सांसद, विधायक आदि शामिल हैं।",
        "type": "boolean",
        "options": [
            {"label_en": "No, no government employees", "label_hi": "नहीं, कोई सरकारी कर्मचारी नहीं है", "value": False},
            {"label_en": "Yes, someone holds a govt post", "label_hi": "हाँ, कोई सरकारी पद पर है", "value": True}
        ]
    }
}

def select_next_question(schemes: List[SchemeDefinition], profile: CitizenProfile, current_step: int = 1) -> NextQuestionResponse:
    """
    Intelligent Question Selection Algorithm (TRD):
    1. Evaluate all available schemes using the current profile.
    2. Exclude schemes already determined as Not eligible or Already fully Eligible.
    3. Identify all unknown fields that can affect remaining schemes ('NOT SURE').
    4. Ask the field appearing in the highest number of remaining undecided schemes.
    5. Break ties by selecting the easiest question (FIELD_EASINESS_RANK).
    6. Stop when no additional answer can change the results or 8 questions reached.
    """
    # Step 1 & 2: Evaluate and exclude resolved schemes
    undecided_schemes: List[SchemeDefinition] = []
    
    for s in schemes:
        res = evaluate_scheme(s, profile)
        # We only care about schemes that are in NOT SURE and have missing fields
        if res.status == "NOT SURE" and len(res.missing_fields) > 0:
            undecided_schemes.append(s)

    # If 8 questions reached or no schemes remain undecided or no missing fields affect outcomes, stop!
    if current_step > 8 or not undecided_schemes:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="All relevant schemes have been conclusively evaluated based on your profile.",
            resolved_message_hi="आपकी प्रोफ़ाइल के आधार पर सभी प्रासंगिक योजनाओं का निर्णायक मूल्यांकन कर लिया गया है।"
        )

    # Step 3: Count frequency of each unknown field in remaining undecided schemes
    field_counts = Counter()
    for s in undecided_schemes:
        res = evaluate_scheme(s, profile)
        for field in res.missing_fields:
            if getattr(profile, field, None) is None:
                field_counts[field] += 1

    # Filter out fields that are already answered
    unanswered_fields = [f for f in field_counts.keys() if getattr(profile, f, None) is None]

    if not unanswered_fields:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="Sufficient information collected to finalize scheme evaluation.",
            resolved_message_hi="योजना मूल्यांकन को अंतिम रूप देने के लिए पर्याप्त जानकारी एकत्र की गई है।"
        )

    # Step 4 & 5: Sort by:
    # 1) Frequency in undecided schemes (descending)
    # 2) Easiness rank (ascending - lower rank is easier)
    def sort_key(f: str):
        count = field_counts[f]
        easiness = FIELD_EASINESS_RANK.get(f, 99)
        return (-count, easiness)

    best_field = sorted(unanswered_fields, key=sort_key)[0]
    
    # Construct Question object
    q_data = QUESTION_REGISTRY.get(best_field)
    if not q_data:
        # Fallback generic question
        q_data = {
            "title_en": f"Please provide your {best_field.replace('_', ' ')}",
            "title_hi": f"कृपया अपना {best_field.replace('_', ' ')} बताएं",
            "subtitle_en": "Required to confirm scheme eligibility.",
            "subtitle_hi": "योजना पात्रता की पुष्टि के लिए आवश्यक।",
            "type": "text",
            "options": None
        }

    options_list = None
    if q_data.get("options"):
        options_list = [QuestionOption(**opt) for opt in q_data["options"]]

    question = NextQuestion(
        field=best_field,
        title_en=q_data["title_en"],
        title_hi=q_data["title_hi"],
        subtitle_en=q_data.get("subtitle_en"),
        subtitle_hi=q_data.get("subtitle_hi"),
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
