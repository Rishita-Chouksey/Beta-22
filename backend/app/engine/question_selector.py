from typing import List, Dict, Any, Optional
from collections import Counter
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

QUESTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "state": {
        "title_en": "Which state do you reside in?",
        "title_hi": "आप किस राज्य के निवासी हैं?",
        "subtitle_en": "Government welfare schemes are often state-specific.",
        "subtitle_hi": "कई सरकारी योजनाएं राज्य-विशिष्ट होती हैं।",
        "explanation_en": "Central schemes apply all over India, but state welfare programs (like MMVY or Ladli Behna in MP, Sanjay Gandhi in Maharashtra) require domicile in that specific state.",
        "explanation_hi": "केंद्रीय योजनाएं पूरे भारत में लागू होती हैं, लेकिन राज्य योजनाएं (जैसे एमपी में लाड़ली बहना या एमएमवीवाई, महाराष्ट्र में संजय गांधी) संबंधित राज्य के मूल निवासियों के लिए होती हैं।",
        "examples_en": "Madhya Pradesh, Maharashtra, Uttar Pradesh, etc.",
        "examples_hi": "मध्य प्रदेश, महाराष्ट्र, उत्तर प्रदेश आदि।",
        "type": "single_choice",
        "options": [
            {"label_en": "Madhya Pradesh", "label_hi": "मध्य प्रदेश", "value": "Madhya Pradesh", "description_en": "State resident / Domicile holder", "description_hi": "राज्य के मूल निवासी"},
            {"label_en": "Maharashtra", "label_hi": "महाराष्ट्र", "value": "Maharashtra", "description_en": "State resident / 15 years domicile", "description_hi": "15 वर्ष से राज्य के निवासी"},
            {"label_en": "Uttar Pradesh", "label_hi": "उत्तर प्रदेश", "value": "Uttar Pradesh", "description_en": "State resident", "description_hi": "राज्य के निवासी"},
            {"label_en": "Rajasthan", "label_hi": "राजस्थान", "value": "Rajasthan", "description_en": "State resident", "description_hi": "राज्य के निवासी"},
            {"label_en": "Bihar", "label_hi": "बिहार", "value": "Bihar", "description_en": "State resident", "description_hi": "राज्य के निवासी"},
            {"label_en": "Other State / UT", "label_hi": "अन्य राज्य / केंद्र शासित प्रदेश", "value": "Other", "description_en": "Other Indian state or Union Territory", "description_hi": "अन्य भारतीय राज्य"},
        ]
    },
    "residence_type": {
        "title_en": "What is your residence area type?",
        "title_hi": "आपका निवास क्षेत्र किस प्रकार का है?",
        "subtitle_en": "Tells us whether you live in a rural village or an urban city.",
        "subtitle_hi": "यह बताता है कि आप ग्रामीण गांव में रहते हैं या शहरी क्षेत्र में।",
        "explanation_en": "This helps identify schemes dedicated specifically for people living in village Gram Panchayat areas (like PMAY-G rural housing) versus municipal urban areas.",
        "explanation_hi": "यह ग्राम पंचायत क्षेत्र (जैसे पीएम आवास ग्रामीण) या नगर निगम/नगर पालिका क्षेत्र के लिए बनी विशिष्ट योजनाओं की पहचान में मदद करता है।",
        "examples_en": "Rural: Village under Gram Panchayat. Urban: Town/city under Municipality or Municipal Corporation.",
        "examples_hi": "ग्रामीण: ग्राम पंचायत के अधीन गांव। शहरी: नगरपालिका या नगर निगम के अधीन शहर/कस्बा।",
        "type": "single_choice",
        "options": [
            {"label_en": "Rural", "label_hi": "ग्रामीण (गांव)", "value": "rural", "description_en": "Village or Gram Panchayat area", "description_hi": "ग्राम पंचायत अथवा ग्रामीण इलाका"},
            {"label_en": "Urban", "label_hi": "शहरी (शहर/कस्बा)", "value": "urban", "description_en": "City, town under Municipal Corporation or Nagar Palika", "description_hi": "नगर निगम, नगरपालिका या नगर परिषद क्षेत्र"},
            {"label_en": "Not sure / Semi-urban", "label_hi": "निश्चित नहीं / अर्ध-शहरी", "value": "not_sure", "description_en": "Select this if you are not sure of your exact revenue category", "description_hi": "यदि आपको प्रशासनिक श्रेणी का ज्ञान नहीं है"}
        ]
    },
    "gender": {
        "title_en": "What is your gender?",
        "title_hi": "आपका लिंग क्या है?",
        "subtitle_en": "Certain schemes offer dedicated support for women or transgender citizens.",
        "subtitle_hi": "कुछ योजनाएं महिलाओं या ट्रांसजेंडर नागरिकों के लिए विशेष सहायता प्रदान करती हैं।",
        "explanation_en": "Flagship welfare programs like Mukhyamantri Ladli Behna Yojana and Widow Pensions provide direct monthly aid exclusively to women beneficiaries.",
        "explanation_hi": "लाड़ली बहना और विधवा पेंशन जैसी योजनाएं विशेष रूप से महिला लाभार्थियों को मासिक वित्तीय सहायता देती हैं।",
        "examples_en": "Female, Male, or Transgender.",
        "examples_hi": "महिला, पुरुष, अथवा ट्रांसजेंडर।",
        "type": "single_choice",
        "options": [
            {"label_en": "Female", "label_hi": "महिला (Female)", "value": "female", "description_en": "Eligible for specialized women empowerment schemes", "description_hi": "महिला सशक्तिकरण योजनाओं हेतु पात्र"},
            {"label_en": "Male", "label_hi": "पुरुष (Male)", "value": "male", "description_en": "Eligible for agriculture, youth and health schemes", "description_hi": "कृषि, युवा एवं स्वास्थ्य योजनाओं हेतु"},
            {"label_en": "Transgender / Other", "label_hi": "ट्रांसजेंडर / अन्य", "value": "transgender", "description_en": "Eligible for social security assistance", "description_hi": "सामाजिक सुरक्षा सहायता"}
        ]
    },
    "age": {
        "title_en": "What is your age in completed years?",
        "title_hi": "आपकी आयु कितने वर्ष है?",
        "subtitle_en": "Determines age-bracket eligibility for pensions, scholarships, and child/youth welfare.",
        "subtitle_hi": "पेंशन, छात्रवृत्ति और युवा कल्याण योजनाओं की आयु सीमा तय करने में मदद करता है।",
        "explanation_en": "Different schemes have statutory age windows. For example, IGNWPS Widow Pension requires age 40 to 79, Ladli Behna requires age 21 to 60, and Sanjay Gandhi Niradhar requires 18+.",
        "explanation_hi": "विभिन्न योजनाओं की वैधानिक आयु सीमा होती है। जैसे विधवा पेंशन में 40-79 वर्ष, लाड़ली बहना में 21-60 वर्ष और संजय गांधी योजना में 18 वर्ष या अधिक।",
        "examples_en": "Enter your age as recorded in your Aadhaar card or voter ID (e.g., 29, 48).",
        "examples_hi": "आधार कार्ड में दर्ज अपनी सही आयु दर्ज करें (उदा. 29, 48)।",
        "type": "number",
        "min_val": 1,
        "max_val": 115,
        "unit": "years"
    },
    "marital_status": {
        "title_en": "What is your marital status?",
        "title_hi": "आपकी वैवाहिक स्थिति क्या है?",
        "subtitle_en": "Special security assistance exists for widows, single women, and destitute citizens.",
        "subtitle_hi": "विधवाओं, एकल महिलाओं और निराधार नागरिकों के लिए विशेष सुरक्षा सहायता उपलब्ध है।",
        "explanation_en": "Widow pension schemes require official widow status (husband's death certificate). Schemes like MMVY require unmarried dependent student status. Ladli Behna covers married, widowed and divorced women.",
        "explanation_hi": "विधवा पेंशन योजनाओं के लिए पति का मृत्यु प्रमाण पत्र आवश्यक होता है। छात्रवृत्ति योजनाएं अविवाहित आश्रित युवाओं के लिए होती हैं। लाड़ली बहना में विवाहित, विधवा व परित्यक्ता महिलाएं पात्र हैं।",
        "examples_en": "Widow, Married, Unmarried / Single, Divorced / Deserted.",
        "examples_hi": "विधवा, विवाहित, अविवाहित, अथवा तलाकशुदा / परित्यक्ता।",
        "type": "single_choice",
        "options": [
            {"label_en": "Widow / Widower", "label_hi": "विधवा / विधुर", "value": "widow", "description_en": "Lost spouse; potential eligibility for widow pensions and woman aid", "description_hi": "पति/पत्नी का देहांत; विधवा पेंशन व महिला सहायता हेतु"},
            {"label_en": "Married", "label_hi": "विवाहित", "value": "married", "description_en": "Currently married; eligible for family welfare and housing aid", "description_hi": "वर्तमान में विवाहित; परिवार कल्याण व आवास योजनाओं हेतु"},
            {"label_en": "Unmarried / Single", "label_hi": "अविवाहित / अकेला", "value": "single", "description_en": "Dependent youth student or single adult", "description_hi": "अविवाहित आश्रित छात्र या अविवाहित वयस्क"},
            {"label_en": "Divorced / Deserted", "label_hi": "तलाकशुदा / परित्यक्ता", "value": "divorced", "description_en": "Legally separated or abandoned by spouse", "description_hi": "पति द्वारा परित्यक्ता या कानूनी रूप से तलाकशुदा"}
        ]
    },
    "occupation": {
        "title_en": "What is your primary occupation or current status?",
        "title_hi": "आपका मुख्य व्यवसाय या वर्तमान स्थिति क्या है?",
        "subtitle_en": "Identifies sector-specific schemes for farmers, students, laborers and homemakers.",
        "subtitle_hi": "किसानों, छात्रों, मजदूरों और गृहिणियों के लिए विशिष्ट योजनाओं की पहचान करता है।",
        "explanation_en": "PM-KISAN is exclusively for active farmers cultivating land. MMVY is for students enrolled in higher education. Housing and pension schemes support laborers, homemakers, and self-employed individuals.",
        "explanation_hi": "पीएम किसान केवल खेती करने वाले किसानों के लिए है। मेधावी छात्रवृत्ति कॉलेज छात्रों के लिए है। आवास व पेंशन योजनाएं मजदूरों, गृहिणियों और स्व-रोजगार वालों को लाभ देती हैं।",
        "examples_en": "Farmer cultivating own land, college student, wage laborer, homemaker.",
        "examples_hi": "स्वयं की जमीन पर खेती करने वाला किसान, कॉलेज छात्र, दैनिक मजदूर, गृहिणी।",
        "type": "single_choice",
        "options": [
            {"label_en": "Farmer / Cultivator", "label_hi": "किसान / काश्तकार", "value": "farmer", "description_en": "Cultivates agricultural land; eligible for PM-KISAN & farm subsidies", "description_hi": "कृषि भूमि पर खेती करने वाले; पीएम किसान हेतु पात्र"},
            {"label_en": "College / Higher Education Student", "label_hi": "कॉलेज / उच्च शिक्षा छात्र", "value": "student", "description_en": "Enrolled in degree/diploma course; eligible for scholarships", "description_hi": "डिग्री/डिप्लोमा में अध्ययनरत; छात्रवृत्ति हेतु पात्र"},
            {"label_en": "Agricultural Laborer / Daily Wage Worker", "label_hi": "खेतिहर मजदूर / दैनिक श्रमिक", "value": "agricultural_worker", "description_en": "Works on daily wages without owning major land", "description_hi": "दैनिक मजदूरी पर कार्य करने वाले"},
            {"label_en": "Homemaker", "label_hi": "गृहिणी", "value": "homemaker", "description_en": "Manages household family affairs", "description_hi": "घर का कार्य संभालने वाली महिलाएं"},
            {"label_en": "Self-Employed / Small Artisan / Vendor", "label_hi": "स्व-रोजगार / छोटा दुकानदार / कारीगर", "value": "self_employed", "description_en": "Small street vendor, shopkeeper, or craftsperson", "description_hi": "छोटा व्यापार या हस्तशिल्प"},
            {"label_en": "Unemployed / Looking for Work", "label_hi": "बेरोजगार / काम की तलाश", "value": "unemployed", "description_en": "Currently seeking employment", "description_hi": "वर्तमान में रोजगार की तलाश में"},
            {"label_en": "Private / Unorganized Sector Job", "label_hi": "निजी / असंगठित क्षेत्र में कार्य", "value": "private_job", "description_en": "Employed in informal or private enterprise", "description_hi": "निजी या असंगठित क्षेत्र में कार्यरत"}
        ]
    },
    "annual_income": {
        "title_en": "What is your approximate annual family income?",
        "title_hi": "आपके परिवार की अनुमानित वार्षिक आय कितनी है?",
        "subtitle_en": "Please consider total income of all earning family members combined.",
        "subtitle_hi": "कृपया परिवार के सभी कमाने वाले सदस्यों की संयुक्त वार्षिक आय बताएं।",
        "explanation_en": "Government welfare schemes check total household family income (as certified on an Income Certificate from the Tehsildar/SDM), not just personal pocket earnings.",
        "explanation_hi": "सरकारी योजनाओं में तहसीलदार या एसडीएम द्वारा जारी आय प्रमाण पत्र पर दर्ज परिवार की कुल वार्षिक आय देखी जाती है, केवल व्यक्तिगत कमाई नहीं।",
        "examples_en": "Under ₹1 Lakh for BPL households; up to ₹2.5 Lakhs for Ladli Behna/Ayushman; up to ₹6 Lakhs for MMVY.",
        "examples_hi": "बीपीएल हेतु ₹1 लाख से कम; लाड़ली बहना व आयुष्मान हेतु ₹2.5 लाख तक; छात्रवृत्ति हेतु ₹6 लाख तक।",
        "type": "single_choice",
        "options": [
            {"label_en": "Less than ₹1,00,000 (Low income / BPL)", "label_hi": "₹1,00,000 से कम (अति निम्न आय / बीपीएल)", "value": 65000, "description_en": "Priority household, housing aid, destitute pensions", "description_hi": "आवास योजना एवं सामाजिक सुरक्षा पेंशन हेतु पात्र"},
            {"label_en": "₹1,00,000 to ₹2,50,000", "label_hi": "₹1,00,000 से ₹2,50,000", "value": 180000, "description_en": "Qualifies for Ladli Behna and Ayushman Bharat health cover", "description_hi": "लाड़ली बहना एवं आयुष्मान भारत कार्ड हेतु पात्र"},
            {"label_en": "₹2,50,000 to ₹6,00,000", "label_hi": "₹2,50,000 से ₹6,00,000", "value": 450000, "description_en": "Qualifies for MMVY Higher Education tuition reimbursement", "description_hi": "मेधावी छात्रवृत्ति शिक्षण शुल्क प्रतिपूर्ति हेतु पात्र"},
            {"label_en": "Above ₹6,00,000", "label_hi": "₹6,00,000 से अधिक", "value": 750000, "description_en": "Exceeds income threshold for most subsidized welfare grants", "description_hi": "अधिकांश रियायती कल्याणकारी योजनाओं की सीमा से अधिक"},
            {"label_en": "Not sure / Don't have exact certificate", "label_hi": "निश्चित नहीं / सटीक जानकारी नहीं है", "value": 9999999, "description_en": "Select this if exact income is unknown; scheme results will show requirements", "description_hi": "परिणाम में आवश्यक आय सीमा दिखाई जाएगी"}
        ]
    },
    "landholding_hectares": {
        "title_en": "How much agricultural land does your family own?",
        "title_hi": "आपके परिवार के पास कितनी कृषि भूमि है?",
        "subtitle_en": "1 hectare is approx 2.47 acres. Small farmers possess up to 2.0 hectares.",
        "subtitle_hi": "1 हेक्टेयर लगभग 2.47 एकड़ के बराबर होता है। लघु किसानों के पास 2 हेक्टेयर तक भूमि होती है।",
        "explanation_en": "PM-KISAN requires cultivable landholding up to 2.0 hectares in the applicant's name. Ladli Behna requires land under 5 acres (approx 2.02 ha).",
        "explanation_hi": "पीएम किसान योजना के लिए 2 हेक्टेयर तक की कृषि भूमि आवश्यक है। लाड़ली बहना में 5 एकड़ (लगभग 2 हेक्टेयर) से कम भूमि होनी चाहिए।",
        "examples_en": "No land (0 ha), 1.5 hectares (~3.7 acres), 3 hectares (~7.4 acres).",
        "examples_hi": "भूमिहीन (0 हेक्टेयर), 1.5 हेक्टेयर (लगभग 3.7 एकड़)।",
        "type": "single_choice",
        "options": [
            {"label_en": "No agricultural land (0 hectares / Landless)", "label_hi": "कोई कृषि भूमि नहीं (0 हेक्टेयर / भूमिहीन)", "value": 0.0, "description_en": "Landless citizen or non-agricultural family", "description_hi": "भूमिहीन नागरिक अथवा गैर-कृषि परिवार"},
            {"label_en": "Small / Marginal (Up to 2.0 hectares / ~5 acres)", "label_hi": "लघु एवं सीमांत किसान (2 हेक्टेयर तक)", "value": 1.5, "description_en": "Eligible for PM-KISAN ₹6,000 annual aid", "description_hi": "पीएम किसान ₹6,000 वार्षिक सहायता हेतु पात्र"},
            {"label_en": "Large landholder (More than 2.0 hectares)", "label_hi": "बड़ा भूमिधारक (2 हेक्टेयर से अधिक)", "value": 3.5, "description_en": "Medium to large agrarian holdings", "description_hi": "मध्यम अथवा बड़े कृषि जोतदार"},
            {"label_en": "Not sure / Land in family dispute", "label_hi": "निश्चित नहीं / रिकॉर्ड ज्ञात नहीं", "value": 0.0, "description_en": "Will require Patwari Khasra verification", "description_hi": "पटवारी खसरा सत्यापन की आवश्यकता होगी"}
        ]
    },
    "student_class12_marks_percent": {
        "title_en": "What was your percentage in Class 12 board examination?",
        "title_hi": "12वीं बोर्ड परीक्षा में आपका प्रतिशत कितना था?",
        "subtitle_en": "Required for merit scholarships such as MMVY (>=70% MPBSE or >=85% CBSE).",
        "subtitle_hi": "मेधावी छात्रवृत्ति (जैसे एमएमवीवाई) के लिए आवश्यक है (एमपी बोर्ड 70%+, सीबीएसई 85%+)।",
        "explanation_en": "Mukhyamantri Medhavi Vidyarthi Yojana rewards merit: students from MP Board need 70% or higher, while CBSE/ICSE board students need 85% or higher.",
        "explanation_hi": "मेधावी विद्यार्थी योजना में एमपी बोर्ड से 70% या अधिक, अथवा सीबीएसई/आईसीएसई से 85% या अधिक अंक आवश्यक हैं।",
        "examples_en": "Enter percentage from your official marksheet (e.g. 78.5, 86.0).",
        "examples_hi": "अपनी अंकसूची से कुल प्रतिशत दर्ज करें (उदा. 78.5, 86.0)।",
        "type": "number",
        "min_val": 33,
        "max_val": 100,
        "unit": "%"
    },
    "enrolled_higher_education": {
        "title_en": "Are you admitted into a recognized undergraduate or professional course?",
        "title_hi": "क्या आपने किसी मान्यता प्राप्त स्नातक या व्यावसायिक पाठ्यक्रम में प्रवेश लिया है?",
        "subtitle_en": "Such as Engineering, Medical, Law, Degree colleges, or Polytechnics.",
        "subtitle_hi": "जैसे इंजीनियरिंग, मेडिकल, लॉ, डिग्री कॉलेज या पॉलिटेक्निक।",
        "explanation_en": "MMVY reimburses tuition fees directly to the admitted educational institution following direct counseling/merit admission.",
        "explanation_hi": "एमएमवीवाई छात्रवृत्ति में कॉलेज में प्रवेश के बाद शैक्षणिक शिक्षण शुल्क सीधे कॉलेज को भुगतान किया जाता है।",
        "examples_en": "B.Tech, MBBS, BDS, BA LLB, BSc, BCom, BA, or Polytechnic diploma.",
        "examples_hi": "बी.टेक, एमबीबीएस, बीए एलएलबी, बीएससी, बीए या पॉलिटेक्निक।",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, admitted in Higher Education", "label_hi": "हाँ, उच्च शिक्षा में प्रवेश ले लिया है", "value": True, "description_en": "Hold admission allotment letter and fee receipt", "description_hi": "कॉलेज आवंटन पत्र एवं शुल्क रसीद उपलब्ध है"},
            {"label_en": "No / Not enrolled", "label_hi": "नहीं / प्रवेश नहीं लिया है", "value": False, "description_en": "Not currently enrolled in higher education", "description_hi": "वर्तमान में उच्च शिक्षा में नामांकित नहीं हैं"}
        ]
    },
    "has_pucca_house": {
        "title_en": "Does your family own a permanent pucca house?",
        "title_hi": "क्या आपके परिवार के पास कोई पक्का पक्का मकान है?",
        "subtitle_en": "Housing assistance schemes (PMAY) prioritize families residing in kutcha or makeshift dwellings.",
        "subtitle_hi": "आवास योजनाएं (पीएमएवाई) कच्चे मकानों में रहने वाले परिवारों को प्राथमिकता देती हैं।",
        "explanation_en": "A pucca house has permanent concrete/brick walls and roof. PMAY-G grants ₹1.2 Lakh to build a house for families living in kutcha dwellings without a pucca house anywhere in India.",
        "explanation_hi": "पक्के मकान से तात्पर्य सीमेंट/ईंट की छत व दीवारों वाले मकान से है। कच्चे या जीर्ण-शीर्ण घरों में रहने वाले बेघर परिवारों को पक्का मकान बनाने हेतु अनुदान मिलता है।",
        "examples_en": "No (we live in kutcha/mud house), or Yes (we have a pucca house).",
        "examples_hi": "नहीं (हम कच्चे मकान में रहते हैं), अथवा हाँ (हमारा पक्का मकान है)।",
        "type": "boolean",
        "options": [
            {"label_en": "No, we live in a Kutcha / temporary house", "label_hi": "नहीं, हम कच्चे / अस्थायी मकान में रहते हैं", "value": False, "description_en": "Priority for PMAY-G ₹1.2 Lakh housing grant", "description_hi": "पीएम आवास योजना ग्रामीण हेतु पात्र"},
            {"label_en": "Yes, we own a Pucca house", "label_hi": "हाँ, हमारे पास पक्का मकान है", "value": True, "description_en": "Already have permanent brick/concrete housing", "description_hi": "पहले से पक्का आवास उपलब्ध है"}
        ]
    },
    "bpl_card_holder": {
        "title_en": "Does your family possess a BPL / Antyodaya Ration Card?",
        "title_hi": "क्या आपके परिवार के पास बीपीएल / अंत्योदय राशन कार्ड है?",
        "subtitle_en": "Below Poverty Line verification card issued by the State Food & Civil Supplies.",
        "subtitle_hi": "खाद्य एवं नागरिक आपूर्ति विभाग द्वारा जारी गरीबी रेखा से नीचे का कार्ड।",
        "explanation_en": "BPL ration card is official evidence of socio-economic vulnerability required for schemes like IGNWPS Widow Pension and subsidized health coverage.",
        "explanation_hi": "बीपीएल राशन कार्ड गरीबी रेखा से नीचे होने का आधिकारिक प्रमाण है, जो विधवा पेंशन और रियायती योजनाओं के लिए अनिवार्य है।",
        "examples_en": "BPL card with blue/yellow cover or Antyodaya Anna Yojana (AAY) card.",
        "examples_hi": "बीपीएल राशन कार्ड अथवा अंत्योदय अन्न योजना कार्ड।",
        "type": "boolean",
        "options": [
            {"label_en": "Yes, we have BPL / Antyodaya Card", "label_hi": "हाँ, हमारे पास बीपीएल / अंत्योदय कार्ड है", "value": True, "description_en": "Verified below poverty line household", "description_hi": "सत्यापित गरीबी रेखा से नीचे परिवार"},
            {"label_en": "No BPL Card", "label_hi": "बीपीएल कार्ड नहीं है", "value": False, "description_en": "Normal ration card or non-BPL family", "description_hi": "सामान्य राशन कार्ड धारक अथवा गैर-बीपीएल"}
        ]
    },
    "is_institutional_landholder": {
        "title_en": "Is the agricultural land registered under an institution, trust, or enterprise?",
        "title_hi": "क्या कृषि भूमि किसी संस्थागत, ट्रस्ट या कंपनी के नाम पर है?",
        "subtitle_en": "Schemes like PM-KISAN only benefit individual family cultivators.",
        "subtitle_hi": "पीएम-किसान जैसी योजनाएं केवल व्यक्तिगत किसान परिवारों को लाभ देती हैं।",
        "explanation_en": "Land registered under temple trusts, corporate bodies, or educational societies is excluded from government farmer income support.",
        "explanation_hi": "ट्रस्ट, कंपनी या संस्था के नाम पंजीकृत भूमि पर किसान सम्मान निधि का लाभ नहीं मिलता; भूमि व्यक्तिगत नाम पर होनी चाहिए।",
        "examples_en": "No (family owned), or Yes (institutional).",
        "examples_hi": "नहीं (व्यक्तिगत/पारिवारिक भूमि), अथवा हाँ (संस्थागत)।",
        "type": "boolean",
        "options": [
            {"label_en": "No, land is individually / family owned", "label_hi": "नहीं, भूमि व्यक्तिगत / परिवार के नाम है", "value": False, "description_en": "Eligible for individual farmer income transfer", "description_hi": "व्यक्तिगत किसान लाभ हेतु पात्र"},
            {"label_en": "Yes, land is institutionally held", "label_hi": "हाँ, भूमि संस्थागत या ट्रस्ट के नाम है", "value": True, "description_en": "Excluded from PM-KISAN guidelines", "description_hi": "पीएम किसान नियमों के अंतर्गत अपात्र"}
        ]
    },
    "holds_constitutional_post": {
        "title_en": "Does anyone in your immediate family hold a government job or constitutional post?",
        "title_hi": "क्या आपके परिवार में कोई सरकारी नौकरी या संवैधानिक पद पर है?",
        "subtitle_en": "Includes regular government employees, MPs, MLAs, and municipal chairpersons.",
        "subtitle_hi": "नियमित सरकारी कर्मचारी, सांसद, विधायक, नगर पालिका अध्यक्ष आदि शामिल हैं।",
        "explanation_en": "Central schemes exclude families having regular government pensioners, income tax payers, or elected constitutional post holders from subsidized cash transfers.",
        "explanation_hi": "नियमित सरकारी नौकरी या संवैधानिक पदों पर आसीन परिवारों को कल्याणकारी नकद सहायता योजनाओं से अलग रखा जाता है।",
        "examples_en": "Government officers, teachers in govt service, retired gazetted officers.",
        "examples_hi": "नियमित सरकारी कर्मचारी, अधिकारी या जनप्रतिनिधि।",
        "type": "boolean",
        "options": [
            {"label_en": "No, no government employees in family", "label_hi": "नहीं, परिवार में कोई सरकारी पद पर नहीं है", "value": False, "description_en": "Eligible for public welfare benefits", "description_hi": "सार्वजनिक कल्याण सहायता हेतु पात्र"},
            {"label_en": "Yes, someone holds a govt post", "label_hi": "हाँ, परिवार में सरकारी पद / नौकरी है", "value": True, "description_en": "Statutory exclusion applies for direct welfare grants", "description_hi": "प्रत्यक्ष अनुदान नियमों के अंतर्गत अपवर्जित"}
        ]
    }
}

def select_next_question(schemes: List[SchemeDefinition], profile: CitizenProfile, current_step: int = 1) -> NextQuestionResponse:
    """
    Intelligent Dynamic Question Selection:
    1. Evaluates all schemes against the active citizen profile.
    2. Identifies schemes in NOT SURE with missing fields.
    3. Selects the unanswered field with maximum impact, tie-broken by cognitive ease.
    4. Guarantees terminating when sufficient info is gathered or step limit reached.
    """
    undecided_schemes: List[SchemeDefinition] = []
    
    for s in schemes:
        res = evaluate_scheme(s, profile)
        if res.status == "NOT SURE" and len(res.missing_fields) > 0:
            undecided_schemes.append(s)

    # Stopping condition: reached limit or all schemes resolved
    if current_step > 8 or not undecided_schemes:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="All relevant schemes have been conclusively evaluated based on your profile.",
            resolved_message_hi="आपकी प्रोफ़ाइल के आधार पर सभी प्रासंगिक योजनाओं का निर्णायक मूल्यांकन कर लिया गया है।"
        )

    # Count frequency of each unknown field in remaining undecided schemes
    field_counts = Counter()
    for s in undecided_schemes:
        res = evaluate_scheme(s, profile)
        for field in res.missing_fields:
            if getattr(profile, field, None) is None and field not in profile.skipped_fields:
                field_counts[field] += 1

    unanswered_fields = [
        f for f in field_counts.keys()
        if getattr(profile, f, None) is None and f not in profile.skipped_fields
    ]

    if not unanswered_fields:
        return NextQuestionResponse(
            has_more=False,
            question=None,
            resolved_message_en="Sufficient information collected to finalize scheme evaluation.",
            resolved_message_hi="योजना मूल्यांकन को अंतिम रूप देने के लिए पर्याप्त जानकारी एकत्र की गई है।"
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
            "subtitle_en": "Required to confirm scheme eligibility.",
            "subtitle_hi": "योजना पात्रता की पुष्टि के लिए आवश्यक।",
            "explanation_en": "This information is verified against official government scheme criteria.",
            "explanation_hi": "यह जानकारी आधिकारिक सरकारी योजना मानदंडों से जांची जाती है।",
            "examples_en": None,
            "examples_hi": None,
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
        subtitle_en=q_data.get("subtitle_en"),
        subtitle_hi=q_data.get("subtitle_hi"),
        explanation_en=q_data.get("explanation_en"),
        explanation_hi=q_data.get("explanation_hi"),
        examples_en=q_data.get("examples_en"),
        examples_hi=q_data.get("examples_hi"),
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
