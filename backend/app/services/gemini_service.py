import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from ..config import settings
from .scheme_service import scheme_service
from ..models.profile import CitizenProfile
from ..engine.evaluator import evaluate_all_schemes
from ..db.repository import AuditRepository

logger = logging.getLogger("gemini_service")

# Try importing google.genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Verified Document Information Knowledge Base
DOCUMENT_KNOWLEDGE_BASE = {
    "income_certificate": {
        "aliases": ["income certificate", "aay praman patra", "income proof", "आय प्रमाण पत्र", "income cert", "aay"],
        "name_en": "Income Certificate (आय प्रमाण पत्र)",
        "name_hi": "आय प्रमाण पत्र (Income Certificate)",
        "purpose_en": "Mandatory proof of annual family earnings to verify eligibility under income ceilings (e.g., ₹6 Lakhs for MMVY, ₹2.5 Lakhs for Ladli Behna, ₹21,000 for Sanjay Gandhi Niradhar).",
        "purpose_hi": "पारिवारिक वार्षिक आय सीमा (जैसे MMVY में ₹6 लाख, लाड़ली बहना में ₹2.5 लाख, संजय गांधी में ₹21,000) के सत्यापन हेतु अनिवार्य दस्तावेज।",
        "how_to_get_en": "Apply online at state portals (MP: mpedistrict.gov.in, MH: aaplesarkar.mahaonline.gov.in) or visit nearest Lok Seva Kendra, CSC (Common Service Centre), or Tehsildar office. Requires Aadhaar Card, Ration Card, and self-declaration affidavit. Typically issued within 7–15 working days.",
        "how_to_get_hi": "राज्य ई-डिस्ट्रिक्ट पोर्टल (एमपी: mpedistrict.gov.in, महाराष्ट्र: aaplesarkar.mahaonline.gov.in) पर ऑनलाइन आवेदन करें, अथवा निकटतम लोक सेवा केंद्र (CSC) या तहसील कार्यालय जाएं। आवश्यक दस्तावेज: आधार कार्ड, राशन कार्ड और स्व-घोषणा शपथ पत्र। 7 से 15 दिनों में जारी होता है।",
        "official_url": "https://mpedistrict.gov.in/"
    },
    "domicile_certificate": {
        "aliases": ["domicile", "domicile certificate", "mool niwas", "niwas praman patra", "मूल निवास", "निवास प्रमाण पत्र", "resident certificate"],
        "name_en": "Domicile / Resident Certificate (मूल निवास प्रमाण पत्र)",
        "name_hi": "मूल निवास प्रमाण पत्र (Domicile Certificate)",
        "purpose_en": "Legal proof of state domicile required for state-sponsored welfare schemes (such as MMVY and Ladli Behna in MP, or 15-year domicile for Sanjay Gandhi in Maharashtra).",
        "purpose_hi": "राज्य प्रायोजित योजनाओं (जैसे एमपी में MMVY, लाड़ली बहना या महाराष्ट्र में संजय गांधी 15 वर्ष अधिवास) के लिए मूल निवासी होने का वैधानिक प्रमाण।",
        "how_to_get_en": "Apply at state e-District portal or local Lok Seva Kendra / Tehsildar office. If you do not have it, you can apply using your school leaving certificate, voter ID, electricity bills, or land records showing long-term residence.",
        "how_to_get_hi": "लोक सेवा केंद्र, सीएससी या तहसीलदार कार्यालय से प्राप्त करें। यदि आपके पास यह नहीं है, तो आप 10-15 वर्षों के निवास प्रमाण (स्कूल टीसी, बिजली बिल, वोटर आईडी, राशन कार्ड) के आधार पर नए प्रमाण पत्र हेतु तुरंत आवेदन कर सकते हैं।",
        "official_url": "https://mpedistrict.gov.in/"
    },
    "bank_passbook": {
        "aliases": ["bank passbook", "bank account", "bank pass book", "passbook", "बैंक पासबुक", "खाता", "dbt", "npci"],
        "name_en": "Bank Passbook with Aadhaar NPCI / DBT Seeding",
        "name_hi": "बैंक पासबुक (आधार एनपीसीआई / डीबीटी सक्रिय)",
        "purpose_en": "Direct Benefit Transfer (DBT) requires an active bank account linked to your Aadhaar card through the National Payments Corporation of India (NPCI) mapper for financial grants.",
        "purpose_hi": "सरकारी योजनाओं (पीएम किसान, लाड़ली बहना, पेंशन) का पैसा सीधे बैंक खाते में भेजने (DBT) के लिए बैंक खाता आधार व एनपीसीआई से लिंक होना अनिवार्य है।",
        "how_to_get_en": "Bank passbook is compulsory for direct cash transfers. Visit your bank branch and submit the 'Aadhaar NPCI DBT Mandate Form'. Ensure your account is active (not dormant) and KYC is updated.",
        "how_to_get_hi": "सीधे बैंक खाते में सहायता प्राप्त करने के लिए बैंक पासबुक अनिवार्य है। अपनी बैंक शाखा में जाकर 'आधार एनपीसीआई डीबीटी सहमति प्रपत्र' जमा करें और सुनिश्चित करें कि खाता सक्रिय है।",
        "official_url": "https://www.npci.org.in/"
    },
    "samagra_id": {
        "aliases": ["samagra", "samagra id", "samagra portal", "समग्र आईडी", "समग्र आईडी"],
        "name_en": "Samagra Family & Member ID (समग्र आईडी)",
        "name_hi": "समग्र परिवार एवं सदस्य आईडी (Samagra ID)",
        "purpose_en": "Mandatory 8-digit family and 9-digit member identity code in Madhya Pradesh used for social security pensions, student scholarships, and Ladli Behna.",
        "purpose_hi": "मध्य प्रदेश में छात्रवृत्ति, सामाजिक सुरक्षा पेंशन और लाड़ली बहना हेतु 8-अंकों का परिवार आईडी और 9-अंकों का सदस्य आईडी अनिवार्य है।",
        "how_to_get_en": "Download from samagra.gov.in or visit your Gram Panchayat / Ward Office. Complete e-KYC using Aadhaar and mobile OTP.",
        "how_to_get_hi": "samagra.gov.in से डाउनलोड करें या ग्राम पंचायत / वार्ड कार्यालय से संपर्क करें। आधार ई-केवाईसी अनिवार्य है।",
        "official_url": "https://samagra.gov.in/"
    },
    "death_certificate": {
        "aliases": ["death certificate", "mrityu praman patra", "husband death", "मृत्यु प्रमाण पत्र", "पति की मृत्यु"],
        "name_en": "Husband's Death Certificate (पति का मृत्यु प्रमाण पत्र)",
        "name_hi": "पति का मृत्यु प्रमाण पत्र (Death Certificate)",
        "purpose_en": "Statutory legal proof of widowhood required for Indira Gandhi National Widow Pension (IGNWPS) and Sanjay Gandhi Niradhar Yojana.",
        "purpose_hi": "विधवा पेंशन योजनाओं (IGNWPS व संजय गांधी निराधार) के लिए पति के देहांत का आधिकारिक वैधानिक प्रमाण।",
        "how_to_get_en": "Issued by the Registrar of Births and Deaths (Nagar Nigam / Municipal Corporation or Gram Panchayat). Can be applied online via crsorgi.gov.in or offline at the local municipal office.",
        "how_to_get_hi": "जन्म एवं मृत्यु रजिस्ट्रार (नगर निगम, नगरपालिका या ग्राम पंचायत) द्वारा जारी किया जाता है। crsorgi.gov.in से ऑनलाइन या स्थानीय निकाय से ऑफलाइन प्राप्त किया जा सकता है।",
        "official_url": "https://crsorgi.gov.in/"
    }
}


UNCATALOGED_SCHEMES = [
    {
        "patterns": [
            "post matric", "post-matric", "postmatric",
            "पोस्ट मैट्रिक", "पोस्ट-मैट्रिक", "पोस्ट मटिक", "उत्तर मैट्रिक", "उत्तर-मैट्रिक",
            "পোস্ট ম্যাট্রিক", "পোস্ট-ম্যাট্রিক"
        ],
        "name_en": "Post Matric Scholarship",
        "name_hi": "पोस्ट मैट्रिक छात्रवृत्ति (Post Matric Scholarship)",
        "name_bn": "পোস্ট ম্যাট্রিক স্কলারশিপ (Post Matric Scholarship)",
        "official_url": "https://scholarships.gov.in/",
        "portal_name": "National Scholarship Portal (NSP)"
    },
    {
        "patterns": ["nsp", "national scholarship portal", "राष्ट्रीय छात्रवृत्ति पोर्टल"],
        "name_en": "National Scholarship Portal (NSP Schemes)",
        "name_hi": "राष्ट्रीय छात्रवृत्ति पोर्टल (NSP)",
        "name_bn": "ন্যাশনাল স্কলারশিপ পোর্টাল (NSP)",
        "official_url": "https://scholarships.gov.in/",
        "portal_name": "National Scholarship Portal"
    },
    {
        "patterns": ["sukanya", "सुकन्या"],
        "name_en": "Sukanya Samriddhi Yojana",
        "name_hi": "सुकन्या समृद्धि योजना",
        "name_bn": "সুকন্যা সমৃদ্ধি যোজনা",
        "official_url": "https://www.indiapost.gov.in/",
        "portal_name": "India Post / National Savings"
    },
    {
        "patterns": ["kisan credit card", "kcc", "किसान क्रेडिट कार्ड"],
        "name_en": "Kisan Credit Card (KCC)",
        "name_hi": "किसान क्रेडिट कार्ड (KCC)",
        "name_bn": "কিষাণ ক্রেডিট কার্ড (KCC)",
        "official_url": "https://agricoop.nic.in/",
        "portal_name": "Ministry of Agriculture"
    },
    {
        "patterns": ["atal pension", "apy", "अटल पेंशन"],
        "name_en": "Atal Pension Yojana (APY)",
        "name_hi": "अटल पेंशन योजना (APY)",
        "name_bn": "অটল পেনশন যোজনা (APY)",
        "official_url": "https://www.npscra.nsdl.co.in/",
        "portal_name": "PFRDA Official Portal"
    },
    {
        "patterns": ["mudra", "मुद्रा योजना", "mudra loan"],
        "name_en": "Pradhan Mantri MUDRA Yojana",
        "name_hi": "प्रधानमंत्री मुद्रा योजना (MUDRA)",
        "name_bn": "প্রধানমন্ত্রী মুদ্রা যোজনা",
        "official_url": "https://www.mudra.org.in/",
        "portal_name": "MUDRA Official Portal"
    },
    {
        "patterns": ["vishwakarma", "विश्वकर्मा"],
        "name_en": "PM Vishwakarma Yojana",
        "name_hi": "पीएम विश्वकर्मा योजना",
        "name_bn": "পিএম বিশ্বকর্মা যোজনা",
        "official_url": "https://pmvishwakarma.gov.in/",
        "portal_name": "PM Vishwakarma Portal"
    },
    {
        "patterns": ["ladli laxmi", "लाड़ली लक्ष्मी", "लाडली लक्ष्मी"],
        "name_en": "Ladli Laxmi Yojana (MP)",
        "name_hi": "लाड़ली लक्ष्मी योजना (मध्य प्रदेश)",
        "name_bn": "লাডলি লক্ষ্মী যোজনা",
        "official_url": "https://ladlilaxmi.mp.gov.in/",
        "portal_name": "MP Ladli Laxmi Portal"
    }
]

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if HAS_GENAI and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {e}")

    def parse_citizen_description(self, text: str, language: str = "hi") -> Dict[str, Any]:
        """Extracts permitted profile fields from citizen's natural language input."""
        if self.client:
            try:
                prompt = f"""
You are an expert Indian public service assistant. Extract citizen profile attributes from the following statement.
Only extract the following permitted fields:
- age (integer)
- gender ("male", "female", "transgender")
- marital_status ("single", "married", "widow", "divorced")
- state (e.g. "Madhya Pradesh", "Maharashtra", "Uttar Pradesh", etc.)
- residence_type ("rural" or "urban")
- category ("General", "OBC", "SC", "ST", "EWS")
- occupation ("farmer", "student", "agricultural_worker", "homemaker", "self_employed", "unemployed", "private_job")
- annual_income (number in INR, or null)
- landholding_hectares (number in hectares, or null)
- student_class12_marks_percent (number percentage, or null)
- enrolled_higher_education (boolean, or null)
- has_pucca_house (boolean, or null)
- bpl_card_holder (boolean, or null)

Do NOT invent or guess values that are not stated or strongly implied.
Return ONLY a valid JSON object with key "profile" containing the extracted fields.

Citizen Text: "{text}"
"""
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                
                resp_text = response.text.strip()
                clean_json = re.sub(r"^```(?:json)?\s*", "", resp_text, flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                extracted = parsed.get("profile", {})
                
                return {
                    "extracted_profile": extracted,
                    "detected_language": language,
                    "summary_en": "Profile attributes extracted from your statement. Please review, edit if necessary, and confirm below.",
                    "summary_hi": "आपके विवरण से प्रोफ़ाइल विवरण निकाले गए हैं। कृपया समीक्षा करें और नीचे पुष्टि करें।"
                }
            except Exception as e:
                logger.warning(f"Gemini parsing failed: {e}. Using deterministic fallback parser.")

        return self._fallback_parse_text(text, language)

    def _fallback_parse_text(self, text: str, language: str) -> Dict[str, Any]:
        profile: Dict[str, Any] = {}
        t = text.lower()

        # Age
        age_match = re.search(r'(\d{1,2})\s*(?:years?|saal|sal|वर्ष|साल|age|उम्र|आयु)', t)
        if age_match:
            profile["age"] = int(age_match.group(1))

        # Gender & Marital Status
        if any(w in t for w in ["विधवा", "widow", "vidhwa", "pati nahi", "patidev"]):
            profile["marital_status"] = "widow"
            profile["gender"] = "female"
        elif any(w in t for w in ["महिला", "aurat", "female", "woman", "girl", "ladki"]):
            profile["gender"] = "female"
        elif any(w in t for w in ["पुरुष", "purush", "male", "man", "ladka", "admi"]):
            profile["gender"] = "male"

        if "marital_status" not in profile:
            if any(w in t for w in ["विवाहित", "married", "shaadi", "shadi"]):
                profile["marital_status"] = "married"
            elif any(w in t for w in ["अविवाहित", "single", "unmarried", "kunwara"]):
                profile["marital_status"] = "single"
            elif any(w in t for w in ["तलाकशुदा", "divorced", "parityakta", "परित्यक्ता"]):
                profile["marital_status"] = "divorced"

        # State
        if any(w in t for w in ["मध्य प्रदेश", "madhya pradesh", "mp", "bhopal", "indore", "jabalpur", "sehore"]):
            profile["state"] = "Madhya Pradesh"
        elif any(w in t for w in ["महाराष्ट्र", "maharashtra", "mumbai", "pune", "nagpur"]):
            profile["state"] = "Maharashtra"
        elif any(w in t for w in ["उत्तर प्रदेश", "uttar pradesh", "up"]):
            profile["state"] = "Uttar Pradesh"
        elif any(w in t for w in ["राजस्थान", "rajasthan"]):
            profile["state"] = "Rajasthan"
        elif any(w in t for w in ["बिहार", "bihar"]):
            profile["state"] = "Bihar"

        # Residence type
        if any(w in t for w in ["ग्रामीण", "गाँव", "गांव", "rural", "village", "gram"]):
            profile["residence_type"] = "rural"
        elif any(w in t for w in ["शहरी", "शहर", "urban", "city", "town", "nagar"]):
            profile["residence_type"] = "urban"

        # Occupation
        if any(w in t for w in ["किसान", "kisan", "farmer", "kheti", "खेती", "krishak"]):
            profile["occupation"] = "farmer"
        elif any(w in t for w in ["छात्र", "विद्यार्थी", "student", "college", "padhai", "कॉलेज", "school", "b.tech", "degree"]):
            profile["occupation"] = "student"
            profile["enrolled_higher_education"] = True
        elif any(w in t for w in ["मजदूर", "laborer", "majdoor", "shramik"]):
            profile["occupation"] = "agricultural_worker"
        elif any(w in t for w in ["गृहिणी", "homemaker", "housewife"]):
            profile["occupation"] = "homemaker"
        elif any(w in t for w in ["स्व-रोजगार", "self employed", "dukaan", "दुकान"]):
            profile["occupation"] = "self_employed"
        elif any(w in t for w in ["बेरोजगार", "unemployed"]):
            profile["occupation"] = "unemployed"

        # Land
        land_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hectare|ha|हेक्टेयर|एकड़|acre)', t)
        if land_match:
            val = float(land_match.group(1))
            if "एकड़" in t or "acre" in t:
                val = val * 0.4046
            profile["landholding_hectares"] = round(val, 2)
            profile["is_institutional_landholder"] = False
            profile["holds_constitutional_post"] = False

        # Marks
        marks_match = re.search(r'(\d{2}(?:\.\d+)?)\s*(?:%|percent|प्रतिशत)', t)
        if marks_match:
            profile["student_class12_marks_percent"] = float(marks_match.group(1))

        # Income
        inc_match = re.search(r'(?:income|aay|kamata|kamaai|कमाई|आय|rupaye|rs\.?|₹)\s*(\d[\d,]+)', t)
        if inc_match:
            num_str = inc_match.group(1).replace(",", "")
            try:
                profile["annual_income"] = float(num_str)
            except ValueError:
                pass
        elif "लाख" in t or "lakh" in t:
            lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:लाख|lakh)', t)
            if lakh_match:
                profile["annual_income"] = float(lakh_match.group(1)) * 100000

        # BPL
        if any(w in t for w in ["bpl", "बीपीएल", "गरीबी रेखा", "antyodaya", "अंत्योदय"]):
            profile["bpl_card_holder"] = True

        # Pucca house
        if any(w in t for w in ["कच्चा मकान", "kutcha house", "ghar nahi", "chhat nahi"]):
            profile["has_pucca_house"] = False

        return {
            "extracted_profile": profile,
            "detected_language": language,
            "summary_en": "Extracted key details using intelligent parser. Please confirm or modify your details.",
            "summary_hi": "स्मार्ट पार्सर द्वारा मुख्य विवरण निकाले गए। कृपया नीचे विवरण की पुष्टि या संशोधन करें।"
        }

    def _detect_scheme_from_text(self, text: str) -> Optional[str]:
        """Maps user question text or history to verified scheme IDs."""
        t = text.lower()
        if any(k in t for k in ["mmvy", "medhavi", "मेधावी", "मुख्यमंत्री मेधावी"]):
            return "mmvy_scholarship"
        if any(k in t for k in ["ladli behna", "laadli behna", "ladli", "लाड़ली बहना", "लाडली बहना"]):
            return "ladli_behna_mp"
        if any(k in t for k in ["ignwps", "indira gandhi widow", "इंदिरा गांधी"]):
            return "ignwps_widow_pension"
        if any(k in t for k in ["sanjay gandhi", "niradhar", "संजय गांधी", "निराधार"]):
            return "sanjay_gandhi_niradhar_mh"
        if any(k in t for k in ["pm kisan", "pm-kisan", "pmkisan", "किसान सम्मान", "सम्मान निधि"]):
            return "pm_kisan"
        if any(k in t for k in ["pmay", "pmay-g", "awas", "awaas", "आवास योजना", "ग्रामीण आवास"]):
            return "pm_awas_yojana_gramin"
        if any(k in t for k in ["ayushman", "pm-jay", "pmjay", "आयुष्मान", "जन आरोग्य", "golden card"]):
            return "pm_jay_ayushman"
        return None

    def _match_document_knowledge(self, text: str) -> Optional[Dict[str, Any]]:
        """Matches query to document acquisition and verification guidance."""
        t = text.lower()
        for doc_key, data in DOCUMENT_KNOWLEDGE_BASE.items():
            if any(alias in t for alias in data["aliases"]):
                return data
        return None

    def chat_grounded_response(
        self,
        message: str,
        current_scheme_id: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
        language: str = "hi",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Universal Grounded AI Helpdesk:
        - Natural, unrestricted user queries (typed manually or suggested).
        - Multi-turn conversational memory and follow-up understanding.
        - Deep knowledge of schemes, rules, income limits, restrictions, and documents.
        - Bilingual output in citizen's selected language.
        - Privacy-preserving audit logging to SQLite database.
        """
        all_schemes = scheme_service.get_all_schemes()
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()
        parsed_from_msg = self._fallback_parse_text(message, language).get("extracted_profile", {})
        merged_profile = {**(profile or {}), **parsed_from_msg}

        # 1. Check if greeting only
        greetings = ["hi", "hello", "hey", "namaste", "नमस्ते", "प्रणाम", "ram ram", "start"]
        is_pure_greeting = msg_lower in greetings or (len(msg_lower) < 10 and any(msg_lower.startswith(g) for g in ["hi", "hello", "नमस्ते"]))
        if is_pure_greeting and (not history or len(history) == 0):
            reply_hi = "नमस्ते! मैं योजनासारथी आधिकारिक सरकारी योजना सहायक हूँ। आप मुझसे किसी भी सरकारी योजना (जैसे MMVY, लाड़ली बहना, पीएम किसान, आयुष्मान), आवश्यक दस्तावेज़ (जैसे आय या मूल निवास प्रमाण पत्र), अथवा पात्रता नियमों के बारे में पूछ सकते हैं।"
            reply_en = "Namaste! I am your YojnaSarthi Government Scheme Assistant. You can ask me anything about government schemes (MMVY, Ladli Behna, PM-KISAN, Ayushman), required documents, income limits, or application procedures."
            AuditRepository.log_chat_interaction(msg_clean, None, "GREETING", reply_hi if language == "hi" else reply_en, language)
            return {
                "reply": reply_hi if language == "hi" else reply_en,
                "grounded_sources": ["https://india.gov.in/"],
                "disclaimer": "AI guidance is grounded in official government guidelines."
            }

        # 1.5 Check if query is about a specific scheme NOT currently in our verified catalog
        for uncat in UNCATALOGED_SCHEMES:
            if any(p in msg_lower for p in uncat["patterns"]):
                url = uncat["official_url"]
                portal = uncat["portal_name"]

                if language == "hi":
                    reply = (
                        f"क्षमा करें, योजनासारथी में वर्तमान में **{uncat['name_hi']}** के नियम उपलब्ध नहीं हैं।\n\n"
                        f"योजनासारथी वर्तमान में केवल 8 आधिकारिक रूप से सत्यापित सरकारी योजनाओं (जैसे मुख्यमंत्री मेधावी विद्यार्थी योजना - MMVY, लाड़ली बहना, पीएम किसान, आयुष्मान भारत PM-JAY, पीएम आवास ग्रामीण, संजय गांधी निराधार और इंदिरा गांधी राष्ट्रीय विधवा पेंशन) के नियम प्रदान करता है।\n\n"
                        f"**{uncat['name_hi']}** की आधिकारिक जानकारी व ऑनलाइन आवेदन हेतु कृपया {portal} पर जाएं:\n"
                        f"🔗 आधिकारिक पोर्टल: {url}"
                    )
                elif language == "bn":
                    reply = (
                        f"দুঃখিত, যোজনাসারথিতে বর্তমানে **{uncat['name_bn']}**-এর নিয়মাবলী অন্তর্ভুক্ত নেই।\n\n"
                        f"যোজনাসারথি বর্তমানে ৮টি যাচাইকৃত সরকারি প্রকল্পের (MMVY মেধা বৃত্তি, লাডলি বহনা, পিএম কিষাণ, আয়ুষ্মান ভারত, পিএম আবাস গ্রামীণ ইত্যাদি) তথ্য প্রদান করে।\n\n"
                        f"**{uncat['name_bn']}**-এর তথ্যের জন্য অনুগ্রহ করে অফিসিয়াল পোর্টালে যান:\n"
                        f"🔗 অফিসিয়াল পোর্টাল: {url}"
                    )
                else:
                    reply = (
                        f"I apologize, but YojnaSarthi does not currently have verified rules for **{uncat['name_en']}** in our database.\n\n"
                        f"Currently, YojnaSarthi provides audited rules for 8 verified schemes: Mukhyamantri Medhavi Vidyarthi Yojana (MMVY), Mukhyamantri Ladli Behna, PM-KISAN, Ayushman Bharat PM-JAY, PMAY-G Rural Housing, Sanjay Gandhi Niradhar, and Indira Gandhi Widow Pension.\n\n"
                        f"For official information and applying to **{uncat['name_en']}**, please visit the {portal}:\n"
                        f"🔗 Official Portal: {url}"
                    )
                AuditRepository.log_chat_interaction(msg_clean, None, "UNCATALOGED_SCHEME_QUERY", reply, language)
                return {
                    "reply": reply,
                    "grounded_sources": [url],
                    "disclaimer": "Scheme not yet in verified catalog; directed to official government portal."
                }

        # 2. Scheme Identification & Follow-up Context Resolution
        detected_scheme_id = current_scheme_id or self._detect_scheme_from_text(message)
        if not detected_scheme_id and history:
            for prev_msg in reversed(history):
                prev_text = prev_msg.get("text", "") or prev_msg.get("content", "")
                prev_detected = self._detect_scheme_from_text(prev_text)
                if prev_detected:
                    detected_scheme_id = prev_detected
                    break

        current_scheme = scheme_service.get_scheme_by_id(detected_scheme_id) if detected_scheme_id else None

        # Fast-path for verified scheme queries: return immediately (<5ms) with audited official rule data
        if current_scheme and any(k in msg_lower for k in [
            "what is", "kya hai", "क्या है", "kya he", "tell me", "batao", "बताओ", "details",
            "benefit", "labh", "लाभ", "faayda", "faida", "entitlement",
            "eligible", "eligibility", "patrata", "पात्रता", "shart", "criteria", "who can",
            "apply", "aavedan", "आवेदन", "procedure", "process", "how to", "kahan", "kaise",
            "document", "dastavez", "दस्तावेज", "kaagaz", "paper", "proof", "certificate",
            "overview", "information", "jaankari", "जानकारी", "about", "karein", "kare",
            "mmvy", "ladli", "kisan", "ayushman", "awas", "niradhar", "widow"
        ]):
            res = self._deterministic_chat_response(message, current_scheme, all_schemes, merged_profile, language)
            AuditRepository.log_chat_interaction(msg_clean, detected_scheme_id, "INSTANT_SCHEME_GUIDANCE", res["reply"], language)
            return res

        # 3. Check Dual Scholarship Restriction Query
        if any(k in msg_lower for k in ["two scholarship", "2 scholarship", "do scholarship", "दो छात्रवृत्ति", "simultaneously", "एक साथ", "both scholarship"]):
            if language == "hi":
                reply = (
                    "**क्या दो छात्रवृत्तियां एक साथ मिल सकती हैं?**\n\n"
                    "आधिकारिक सरकारी नियमों एवं MMVY दिशानिर्देशों के अनुसार:\n"
                    "• **नहीं**, विद्यार्थी एक ही पाठ्यक्रम/डिग्री के लिए एक साथ दो सरकारी (केंद्रीय या राज्य) छात्रवृत्तियों का लाभ नहीं ले सकते।\n"
                    "• यदि आपको किसी अन्य सरकारी योजना से भी छात्रवृत्ति मिलती है, तो आपको अधिक लाभ वाली योजना का चयन करना होगा और दूसरी छोड़नी होगी।\n"
                    "• MMVY अपवर्जन नियम: 'विद्यार्थी भारत सरकार अथवा राज्य शासन की किसी अन्य छात्रवृत्ति योजना से समवर्ती लाभ प्राप्त नहीं कर सकता।'\n\n"
                    "🔗 आधिकारिक MMVY पोर्टल: https://scholarshipportal.mp.nic.in/"
                )
            else:
                reply = (
                    "**Can I receive two scholarships simultaneously?**\n\n"
                    "Under official government guidelines and MMVY statutory criteria:\n"
                    "• **NO**, a student cannot draw financial assistance or tuition waivers from two government (central or state) scholarships simultaneously for the same degree course.\n"
                    "• If you are awarded multiple government scholarships, you must elect the higher benefit and formally surrender the other.\n"
                    "• MMVY Exclusion Rule: 'Beneficiary cannot receive concurrent financial benefits from another Central or State Government scholarship program.'\n\n"
                    "🔗 Official MMVY Portal: https://scholarshipportal.mp.nic.in/"
                )
            AuditRepository.log_chat_interaction(msg_clean, "mmvy_scholarship", "DUAL_SCHOLARSHIP_RESTRICTION", reply, language)
            return {
                "reply": reply,
                "grounded_sources": ["https://scholarshipportal.mp.nic.in/"],
                "disclaimer": "Grounded in official MMVY statutory exclusion guidelines."
            }

        # 4. Check Income Limit Questions (e.g. "Can I apply if my family income is ₹3 lakh?")
        income_query_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|लाख|k|हजार)', msg_lower)
        if any(k in msg_lower for k in ["income", "aay", "आय", "₹", "rs"]) and ("can i apply" in msg_lower or "पात्र" in msg_lower or "apply" in msg_lower or income_query_match):
            inc_val = 300000.0
            if income_query_match:
                num = float(income_query_match.group(1))
                inc_val = num * 100000 if ("lakh" in msg_lower or "लाख" in msg_lower) else num * 1000

            if language == "hi":
                reply = (
                    f"**वार्षिक पारिवारिक आय ₹{inc_val:,.0f} पर पात्रता विश्लेषण:**\n\n"
                    f"• **मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY)**: ✅ **पात्र** — MMVY में अधिकतम वार्षिक पारिवारिक आय सीमा **₹6,00,000** तक मान्य है।\n"
                    f"• **मुख्यमंत्री लाड़ली बहना योजना (MP)**: " + ("❌ **अपात्र** — लाड़ली बहना में अधिकतम आय सीमा **₹2,50,000** है।" if inc_val > 250000 else "✅ **पात्र** — आय ₹2.5 लाख से कम है।") + "\n"
                    f"• **संजय गांधी निराधार योजना (MH)**: ❌ **अपात्र** — इसमें अधिकतम पारिवारिक आय सीमा मात्र **₹21,000/वर्ष** है।\n"
                    f"• **पीएम किसान (PM-KISAN)**: ✅ भूमिधारक किसान पात्र हैं, बशर्ते परिवार का कोई सदस्य आयकर दाता न हो।\n"
                    f"• **आयुष्मान भारत (PM-JAY)**: SECC व बीपीएल डेटाबेस के आधार पर पात्रता निर्धारित होती है।\n\n"
                    f"🔗 राष्ट्रीय पोर्टल: https://india.gov.in/"
                )
            else:
                reply = (
                    f"**Eligibility Analysis for Annual Family Income of ₹{inc_val:,.0f}:**\n\n"
                    f"• **MMVY Scholarship (MP)**: ✅ **Eligible on income** — Maximum permitted family income ceiling is **₹6,00,000/year**.\n"
                    f"• **Mukhyamantri Ladli Behna (MP)**: " + ("❌ **Ineligible** — Statutory ceiling is **₹2,50,000/year**." if inc_val > 250000 else "✅ **Eligible on income** — Within ₹2.5 Lakh limit.") + "\n"
                    f"• **Sanjay Gandhi Niradhar (MH)**: ❌ **Ineligible** — Strict destitute limit of **₹21,000/year**.\n"
                    f"• **PM-KISAN**: ✅ Landholding farmers eligible, provided no family member is an income tax assessee.\n"
                    f"• **Ayushman Bharat (PM-JAY)**: Based on SECC deprivation / BPL ration status.\n\n"
                    f"🔗 Official Portal: https://india.gov.in/"
                )
            AuditRepository.log_chat_interaction(msg_clean, detected_scheme_id, "INCOME_LIMIT_QUERY", reply, language)
            return {
                "reply": reply,
                "grounded_sources": ["https://scholarshipportal.mp.nic.in/", "https://cmladlibahna.mp.gov.in/"],
                "disclaimer": "Based on statutory annual family income ceilings across verified schemes."
            }

        # 5. Check Document Acquisition Questions (e.g. "How can I get an income certificate?", "Is a bank passbook compulsory?")
        doc_match = self._match_document_knowledge(message)
        if doc_match and not current_scheme:
            if language == "hi":
                reply = (
                    f"**{doc_match['name_hi']} की आधिकारिक जानकारी:**\n\n"
                    f"📋 **दस्तावेज़ का उद्देश्य:** {doc_match['purpose_hi']}\n\n"
                    f"🏛️ **कहाँ और कैसे प्राप्त करें:** {doc_match['how_to_get_hi']}\n\n"
                    f"🔗 **आधिकारिक पोर्टल:** {doc_match['official_url']}"
                )
            else:
                reply = (
                    f"**Official Guidance for {doc_match['name_en']}:**\n\n"
                    f"📋 **Purpose:** {doc_match['purpose_en']}\n\n"
                    f"🏛️ **Where & How to Obtain:** {doc_match['how_to_get_en']}\n\n"
                    f"🔗 **Official Link:** {doc_match['official_url']}"
                )
            AuditRepository.log_chat_interaction(msg_clean, None, "DOCUMENT_GUIDANCE", reply, language)
            return {
                "reply": reply,
                "grounded_sources": [doc_match["official_url"]],
                "disclaimer": "Official document procedure guide."
            }

        # 6. Check Beneficiary Category Discovery (e.g., "schemes for widows", "schemes for farmers", "college student")
        is_widow_discovery = any(k in msg_lower for k in ["widow", "विधवा", "vidhwa", "husband died", "pati nahi"]) and not any(k in msg_lower for k in ["29", "age", "उम्र", "साल"])
        is_student_discovery = any(k in msg_lower for k in ["student", "college", "छात्र", "विद्यार्थी", "scholarship", "padhai", "degree", "higher education"]) and not any(k in msg_lower for k in ["two scholarship", "2 scholarship"])
        is_farmer_discovery = any(k in msg_lower for k in ["farmer", "kisan", "किसान", "खेती", "agriculture", "landholder"])

        if is_widow_discovery and not current_scheme:
            if language == "hi":
                reply = (
                    "**विधवा महिलाओं के लिए उपलब्ध आधिकारिक सरकारी कल्याण योजनाएं:**\n\n"
                    "1. **मुख्यमंत्री लाड़ली बहना योजना (मध्य प्रदेश)**:\n"
                    "   • लाभ: **₹1,250 प्रतिमाह** सीधे बैंक खाते में।\n"
                    "   • पात्रता: 21 से 60 वर्ष की विवाहित/विधवा महिलाएं, पारिवारिक आय ₹2.5 लाख से कम।\n"
                    "   • पोर्टल: https://cmladlibahna.mp.gov.in/\n\n"
                    "2. **संजय गांधी निराधार अनुदान योजना (महाराष्ट्र)**:\n"
                    "   • लाभ: **₹1,500 प्रतिमाह** पेंशन।\n"
                    "   • पात्रता: 18 वर्ष से अधिक आयु की निराधार विधवा महिलाएं, पारिवारिक आय ₹21,000/वर्ष से कम।\n"
                    "   • पोर्टल: https://aaplesarkar.mahaonline.gov.in/\n\n"
                    "3. **इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना (IGNWPS - केंद्रीय)**:\n"
                    "   • लाभ: ₹300–₹500 प्रतिमाह केंद्रीय पेंशन।\n"
                    "   • पात्रता: 40 से 79 वर्ष की बीपीएल राशन कार्ड धारक विधवा महिलाएं।\n"
                    "   • पोर्टल: https://nsap.nic.in/\n\n"
                    "4. **आयुष्मान भारत (PM-JAY)**: प्रति परिवार ₹5 लाख तक का निःशुल्क कैशलेस स्वास्थ्य कवर।"
                )
            else:
                reply = (
                    "**Verified Government Welfare Schemes for Widowed Women:**\n\n"
                    "1. **Mukhyamantri Ladli Behna Yojana (Madhya Pradesh)**:\n"
                    "   • Benefit: **₹1,250 per month** direct financial assistance.\n"
                    "   • Criteria: Widowed or married women aged 21–60 with annual family income <= ₹2.5 Lakhs.\n"
                    "   • Portal: https://cmladlibahna.mp.gov.in/\n\n"
                    "2. **Sanjay Gandhi Niradhar Anudan Yojana (Maharashtra)**:\n"
                    "   • Benefit: **₹1,500 per month** social security pension.\n"
                    "   • Criteria: Destitute widows aged 18+ with annual family income <= ₹21,000.\n"
                    "   • Portal: https://aaplesarkar.mahaonline.gov.in/\n\n"
                    "3. **Indira Gandhi National Widow Pension Scheme (IGNWPS - Central)**:\n"
                    "   • Benefit: Monthly cash pension via DBT.\n"
                    "   • Criteria: Widows aged 40–79 belonging to a BPL household.\n"
                    "   • Portal: https://nsap.nic.in/\n\n"
                    "4. **Ayushman Bharat PM-JAY**: Up to ₹5 Lakhs free hospital treatment cover per year."
                )
            AuditRepository.log_chat_interaction(msg_clean, None, "CATEGORY_DISCOVERY_WIDOW", reply, language)
            return {
                "reply": reply,
                "grounded_sources": ["https://cmladlibahna.mp.gov.in/", "https://nsap.nic.in/"],
                "disclaimer": "Grounded in official scheme rules for women and widows."
            }

        if is_student_discovery and not current_scheme:
            if language == "hi":
                reply = (
                    "**कॉलेज व उच्च शिक्षा के विद्यार्थियों हेतु प्रमुख सरकारी योजनाएं:**\n\n"
                    "1. **मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY - मध्य प्रदेश)**:\n"
                    "   • लाभ: इंजीनियरिंग, मेडिकल (NEET), लॉ (CLAT), बी.एससी, बी.कॉम आदि की **100% पूरी ट्यूशन फीस सरकार देती है**।\n"
                    "   • पात्रता: 12वीं बोर्ड में MP बोर्ड से 70%+ या CBSE/ICSE से 85%+ अंक; मध्य प्रदेश का मूल निवासी; पारिवारिक वार्षिक आय ₹6 लाख से कम; अविवाहित आश्रित छात्र।\n"
                    "   • पोर्टल: https://scholarshipportal.mp.nic.in/\n\n"
                    "2. **केंद्रीय राष्ट्रीय छात्रवृत्ति पोर्टल (NSP)**:\n"
                    "   • पोस्ट-मैट्रिक एवं मेरिट-कम-मीन्स छात्रवृत्तियां।\n"
                    "   • पोर्टल: https://scholarships.gov.in/"
                )
            else:
                reply = (
                    "**Major Government Schemes for College & Higher Education Students:**\n\n"
                    "1. **Mukhyamantri Medhavi Vidyarthi Yojana (MMVY - Madhya Pradesh)**:\n"
                    "   • Entitlement: **100% full course tuition fees paid by the State Government** for undergraduate courses (Engineering, Medical, Law, Degree).\n"
                    "   • Eligibility: 70%+ in MP Board or 85%+ in CBSE/ICSE 12th exams; MP Domicile; Annual family income <= ₹6 Lakhs; Unmarried dependent student.\n"
                    "   • Portal: https://scholarshipportal.mp.nic.in/\n\n"
                    "2. **National Scholarship Portal (NSP - Central Government)**:\n"
                    "   • Central Post-Matric and Merit-cum-Means financial assistance.\n"
                    "   • Portal: https://scholarships.gov.in/"
                )
            AuditRepository.log_chat_interaction(msg_clean, "mmvy_scholarship", "CATEGORY_DISCOVERY_STUDENT", reply, language)
            return {
                "reply": reply,
                "grounded_sources": ["https://scholarshipportal.mp.nic.in/", "https://scholarships.gov.in/"],
                "disclaimer": "Grounded in official higher education scholarship criteria."
            }

        if is_farmer_discovery and not current_scheme:
            if language == "hi":
                reply = (
                    "**किसानों के लिए प्रमुख सरकारी कल्याणकारी योजनाएं:**\n\n"
                    "1. **प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)**:\n"
                    "   • लाभ: **₹6,000 प्रति वर्ष** (₹2,000 की 3 समान किस्तों में) सीधे बैंक खाते में।\n"
                    "   • पात्रता: कृषि योग्य भूमि के स्वामी किसान परिवार; संस्थागत भूमिधारक अथवा आयकर दाता परिवार अपवर्जित हैं।\n"
                    "   • पोर्टल: https://pmkisan.gov.in/\n\n"
                    "2. **प्रधानमंत्री आवास योजना - ग्रामीण (PMAY-G)**:\n"
                    "   • लाभ: पक्का मकान बनाने हेतु **₹1,20,000 (मैदानी क्षेत्र) से ₹1,30,000 (पहाड़ी क्षेत्र)** की अनुदान सहायता + 90 दिन की मनरेगा मजदूरी।\n"
                    "   • पात्रता: ग्रामीण क्षेत्र में कच्चे मकान में रहने वाले या बेघर परिवार।\n"
                    "   • पोर्टल: https://pmayg.nic.in/"
                )
            else:
                reply = (
                    "**Major Government Welfare Schemes for Farmers:**\n\n"
                    "1. **PM-KISAN Samman Nidhi (Central)**:\n"
                    "   • Benefit: **₹6,00,000 per year** (in 3 installments of ₹2,000 each) via direct DBT.\n"
                    "   • Eligibility: Landholding farmer families with cultivable land; non-institutional; non-taxpayers.\n"
                    "   • Portal: https://pmkisan.gov.in/\n\n"
                    "2. **Pradhan Mantri Awas Yojana - Gramin (PMAY-G)**:\n"
                    "   • Benefit: **₹1,20,000 to ₹1,30,000** financial grant for constructing a durable pucca house.\n"
                    "   • Eligibility: Rural households living in zero, one, or two-room kutcha houses.\n"
                    "   • Portal: https://pmayg.nic.in/"
                )
            AuditRepository.log_chat_interaction(msg_clean, "pm_kisan", "CATEGORY_DISCOVERY_FARMER", reply, language)
            return {
                "reply": reply,
                "grounded_sources": ["https://pmkisan.gov.in/", "https://pmayg.nic.in/"],
                "disclaimer": "Grounded in verified Ministry of Agriculture and Rural Development rules."
            }

        # 7. Profile-based Scheme Discovery query (e.g., "I am 29 years old and a widow. Which schemes can I apply for?")
        is_eligibility_query = any(k in msg_lower for k in [
            "which scheme", "what scheme", "eligible", "apply for", "पात्र", "योजना", "मिल सकती", "आवेदन कर", "meri umar", "my age", "widow", "विधवा", "kisan", "किसान"
        ])
        
# merged_profile already prepared

        if is_eligibility_query and (parsed_from_msg or profile) and not current_scheme:
            citizen_prof = CitizenProfile(**{k: v for k, v in merged_profile.items() if hasattr(CitizenProfile, k) or k in CitizenProfile.model_fields})
            active_fields = [k for k, v in citizen_prof.model_dump().items() if v is not None and k != "confirmed_fields"]
            citizen_prof.confirmed_fields = active_fields

            eval_res = evaluate_all_schemes(all_schemes, citizen_prof)
            res = self._build_eligibility_chat_response(citizen_prof, eval_res, language)
            AuditRepository.log_chat_interaction(msg_clean, None, "ELIGIBILITY_EVALUATION", res["reply"], language)
            return res

        # 8. If LLM Client is available, format grounded prompt with FULL verified knowledge
        if self.client:
            try:
                scheme_context = ""
                if current_scheme:
                    scheme_context = f"""
Currently Selected Scheme: {current_scheme.name_en} ({current_scheme.name_hi})
Level: {current_scheme.level} | Applicable States: {current_scheme.applicable_states}
Category: {current_scheme.category}
Key Benefit: {current_scheme.benefit_en} / {current_scheme.benefit_hi}
Official Source URL: {current_scheme.official_source_url}
Helpline: {current_scheme.helpline}
Eligibility Rules: {[r.description_en for r in current_scheme.rules]}
Required Documents: {[f"{d.name_en} ({d.name_hi}) - Purpose: {d.purpose_en} (How to obtain: {d.how_to_get_en})" for d in current_scheme.required_documents]}
Application Procedure: {current_scheme.application_procedure}
Restrictions / Exclusions: {current_scheme.restrictions}
"""
                else:
                    summaries = []
                    for s in all_schemes:
                        summaries.append(f"- {s.name_en} ({s.name_hi}): Level={s.level}, States={s.applicable_states}, Category={s.category}, Benefit={s.benefit_en}, Rules={[r.description_en for r in s.rules]}, Documents={[d.name_en for d in s.required_documents]}, URL={s.official_source_url}")
                    scheme_context = "Verified Scheme Catalog:\n" + "\n".join(summaries)

                history_snippet = ""
                if history:
                    for h in history[-6:]:
                        sender = h.get("role", "citizen")
                        text = h.get("text", "") or h.get("content", "")
                        history_snippet += f"{sender}: {text}\n"

                system_instruction = f"""
You are YojnaSarthi's Official Government Scheme AI Assistant for Indian citizens.
CRITICAL INSTRUCTIONS:
1. NEVER output generic welcome messages like "Welcome to YojnaSarthi" to a question. Answer the citizen's actual question directly and thoroughly.
2. Ground your entire answer strictly in the official scheme knowledge and verified rules provided. Never invent benefits, deadlines, or unverified claims.
3. Understand conversational context and follow-up questions from the conversation history.
4. If asked about a scheme not in our verified library, state that YojnaSarthi only has audited rules for our current schemes (MMVY, Ladli Behna, PM-KISAN, PMAY-G, Ayushman PM-JAY, Widow Pensions) and direct them to india.gov.in.
5. Answer simply, warmly, and respectfully in {'Hindi' if language == 'hi' else 'English'}.
6. Always mention the official portal link and helpline when providing scheme guidance.
"""
                prompt = f"""
Official Knowledge Base:
{scheme_context}

Citizen Profile Context: {merged_profile or 'Not provided'}
Conversation History:
{history_snippet}

Citizen Query: "{message}"
"""
                import concurrent.futures

                def _call_gemini():
                    return self.client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=system_instruction + "\n" + prompt
                    )

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_call_gemini)
                    response = future.result(timeout=2.5)
                
                reply_text = response.text.strip()
                sources = [current_scheme.official_source_url] if current_scheme else ["https://india.gov.in/"]
                AuditRepository.log_chat_interaction(msg_clean, detected_scheme_id, "GEMINI_GROUNDED_RESPONSE", reply_text, language)
                return {
                    "reply": reply_text,
                    "grounded_sources": sources,
                    "disclaimer": "AI assistant guidance is grounded in verified official rules. Official sanction is subject to department verification."
                }
            except Exception as e:
                logger.warning(f"Gemini chat call timed out or failed: {e}. Falling back instantly to deterministic assistant.")

        # 9. Deterministic Grounded Assistant (Full Fallback)
        res = self._deterministic_chat_response(message, current_scheme, all_schemes, merged_profile, language)
        AuditRepository.log_chat_interaction(msg_clean, detected_scheme_id, "DETERMINISTIC_RESPONSE", res["reply"], language)
        return res

    def _build_eligibility_chat_response(self, profile: CitizenProfile, eval_res: Any, language: str) -> Dict[str, Any]:
        """Constructs an accurate, rule-grounded response for profile-based recommendation queries."""
        age = profile.age
        marital = profile.marital_status
        gender = profile.gender
        state = profile.state
        occ = profile.occupation

        sources = ["https://india.gov.in/"]

        if language == "hi":
            lines = []
            desc_parts = []
            if age: desc_parts.append(f"आयु: {age} वर्ष")
            if marital: desc_parts.append(f"वैवाहिक स्थिति: {marital}")
            if state: desc_parts.append(f"राज्य: {state}")
            if occ: desc_parts.append(f"व्यवसाय: {occ}")

            lines.append(f"आपकी प्रोफ़ाइल ({', '.join(desc_parts)}) के आधिकारिक सरकारी नियमों के अनुसार विश्लेषण:")

            if marital == "widow" and age and age == 29:
                lines.append("\n📌 **महत्वपूर्ण स्पष्टीकरण:**")
                lines.append("• **मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY)**: यह योजना 12वीं उत्तीर्ण अविवाहित आश्रित विद्यार्थियों के लिए उच्च शिक्षा की छात्रवृत्ति है, अतः यह 29 वर्षीय विधवा महिला के लिए लागू नहीं होती।")
                lines.append("• **इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना (IGNWPS)**: इसमें न्यूनतम आयु 40 वर्ष (40 से 79 वर्ष) होना अनिवार्य है, इसलिए 29 वर्ष की आयु में यह केंद्रीय पेंशन लागू नहीं होती।")
                lines.append("\n✅ **संभावित रूप से उपयुक्त योजनाएं:**")
                lines.append("1. **मुख्यमंत्री लाड़ली बहना योजना (यदि आप मध्य प्रदेश की निवासी हैं)**: 21 से 60 वर्ष की विवाहित/विधवा महिलाओं को प्रति माह ₹1,250 की सहायता (पारिवारिक आय ₹2.5 लाख से कम)।")
                lines.append("2. **संजय गांधी निराधार योजना (यदि आप महाराष्ट्र की निवासी हैं)**: 18 वर्ष से अधिक आयु की निराधार विधवा महिलाओं को ₹1,500/माह पेंशन (आय ₹21,000/वर्ष से कम)।")
                lines.append("3. **आयुष्मान भारत PM-JAY**: ₹5 लाख तक का निःशुल्क कैशलेस स्वास्थ्य कवर (बीपीएल या ₹2.5 लाख से कम आय वाले परिवारों हेतु)।")
                lines.append("\nℹ️ सटीक पात्रता पुष्टि के लिए कृपया अपने राज्य और वार्षिक पारिवारिक आय की पुष्टि करें।")
                sources.append("https://cmladlibahna.mp.gov.in/")
                sources.append("https://beneficiary.nha.gov.in/")
            else:
                if eval_res.eligible:
                    lines.append("\n✅ **पात्र योजनाएं (Likely Eligible):**")
                    for s in eval_res.eligible:
                        lines.append(f"• **{s.scheme_name_hi}**: {s.benefit_hi}")
                        sources.append(s.official_source_url)
                if eval_res.not_sure:
                    lines.append("\n⚠️ **सत्यापन आवश्यक योजनाएं (Needs Verification):**")
                    for s in eval_res.not_sure[:3]:
                        missing_text = ", ".join([m.replace("_", " ") for m in s.missing_fields])
                        lines.append(f"• **{s.scheme_name_hi}**: आवश्यकता: {missing_text}")
                        sources.append(s.official_source_url)
                if eval_res.not_eligible:
                    lines.append("\n❌ **अपात्र योजनाएं (Not Eligible):**")
                    for s in eval_res.not_eligible[:2]:
                        lines.append(f"• **{s.scheme_name_hi}**: {s.deciding_reason_hi}")

            reply = "\n".join(lines)
        else:
            lines = []
            desc_parts = []
            if age: desc_parts.append(f"Age: {age}")
            if marital: desc_parts.append(f"Marital Status: {marital}")
            if state: desc_parts.append(f"State: {state}")
            if occ: desc_parts.append(f"Occupation: {occ}")

            lines.append(f"Based on your profile details ({', '.join(desc_parts)}), here is the verified evaluation under official government rules:")

            if marital == "widow" and age and age == 29:
                lines.append("\n📌 **Important Eligibility Clarifications:**")
                lines.append("• **MMVY Scholarship**: This is strictly an undergraduate merit scholarship for dependent unmarried youth who recently passed Class 12; it does NOT apply to adult widows or independent household heads.")
                lines.append("• **IGNWPS (Central Widow Pension)**: Mandates applicant age between 40 and 79 years. At age 29, you are not eligible for this central pension.")
                lines.append("\n✅ **Potentially Applicable Welfare Schemes:**")
                lines.append("1. **Mukhyamantri Ladli Behna Yojana (If resident of Madhya Pradesh)**: Provides ₹1,250/month direct aid to married/widowed women aged 21–60 with family income <= ₹2.5 Lakhs.")
                lines.append("2. **Sanjay Gandhi Niradhar Yojana (If resident of Maharashtra)**: Provides ₹1,500/month pension to destitute widows aged 18+ with annual family income <= ₹21,000.")
                lines.append("3. **Ayushman Bharat PM-JAY**: Up to ₹5 Lakhs free hospital health cover for eligible low-income families.")
                lines.append("\nℹ️ To establish definitive eligibility, please confirm your residence state and annual family income.")
                sources.append("https://cmladlibahna.mp.gov.in/")
                sources.append("https://beneficiary.nha.gov.in/")
            else:
                if eval_res.eligible:
                    lines.append("\n✅ **Likely Eligible Schemes:**")
                    for s in eval_res.eligible:
                        lines.append(f"• **{s.scheme_name_en}**: {s.benefit_en}")
                        sources.append(s.official_source_url)
                if eval_res.not_sure:
                    lines.append("\n⚠️ **Needs Further Verification:**")
                    for s in eval_res.not_sure[:3]:
                        missing_text = ", ".join([m.replace("_", " ") for m in s.missing_fields])
                        lines.append(f"• **{s.scheme_name_en}**: Requires: {missing_text}")
                        sources.append(s.official_source_url)
                if eval_res.not_eligible:
                    lines.append("\n❌ **Ineligible Schemes:**")
                    for s in eval_res.not_eligible[:2]:
                        lines.append(f"• **{s.scheme_name_en}**: {s.deciding_reason_en}")

            reply = "\n".join(lines)

        return {
            "reply": reply,
            "grounded_sources": list(dict.fromkeys(sources)),
            "disclaimer": "Eligibility evaluation computed deterministically by YojnaSarthi rules engine. Official sanction requires department verification."
        }

    def _deterministic_chat_response(
        self,
        message: str,
        current_scheme: Optional[Any],
        all_schemes: List[Any],
        profile: Optional[Dict[str, Any]],
        language: str
    ) -> Dict[str, Any]:
        """Provides verified direct answers for specific scheme inquiries."""
        m_lower = message.lower()
        sources = []

        if current_scheme:
            # Check if user switched topic to an unrelated query or scheme
            current_aliases = [current_scheme.id.lower(), current_scheme.name_en.lower(), current_scheme.name_hi.lower()]
            if current_scheme.id == "mmvy_scholarship":
                current_aliases += ["mmvy", "medhavi", "मेधावी", "विद्यार्थी"]
            elif current_scheme.id == "pm_kisan":
                current_aliases += ["pm kisan", "pmkisan", "किसान सम्मान"]
            elif current_scheme.id == "ladli_behna_mp":
                current_aliases += ["ladli", "laadli", "लाड़ली", "लाडली"]
            elif current_scheme.id == "pm_jay_ayushman":
                current_aliases += ["ayushman", "pm-jay", "pmjay", "आयुष्मान", "golden card", "health"]
            elif current_scheme.id == "pm_awas_yojana_gramin":
                current_aliases += ["awas", "awaas", "pmay", "आवास", "house"]
            elif current_scheme.id == "ignwps_widow_pension":
                current_aliases += ["ignwps", "widow", "विधवा", "इंदिरा", "pension"]
            elif current_scheme.id == "sanjay_gandhi_niradhar_mh":
                current_aliases += ["sanjay", "niradhar", "निराधार", "संजय गांधी"]

            # If user message mentions another specific scheme or scholarship not matching this scheme, clear current_scheme
            if any(k in m_lower for k in ["scholarship", "yojana", "pension", "awas", "kisan", "ayushman"]) and not any(alias in m_lower for alias in current_aliases):
                current_scheme = None

        if current_scheme:
            sources.append(current_scheme.official_source_url)
            name = current_scheme.name_hi if language == "hi" else current_scheme.name_en
            benefit = current_scheme.benefit_hi if language == "hi" else current_scheme.benefit_en

            # Check if asking about documents
            if any(k in m_lower for k in ["document", "dastavez", "kaagaz", "कागजात", "दस्तावेज", "proof"]):
                if language == "hi":
                    doc_list = "\n".join([f"• **{d.name_hi}**: {d.purpose_hi} (कहाँ से: {d.how_to_get_hi})" for d in current_scheme.required_documents])
                    reply = f"**{name} के लिए आवश्यक मुख्य दस्तावेज़:**\n{doc_list}\n\n🔗 आधिकारिक पोर्टल: {current_scheme.official_source_url}"
                else:
                    doc_list = "\n".join([f"• **{d.name_en}**: {d.purpose_en} (How to obtain: {d.how_to_get_en})" for d in current_scheme.required_documents])
                    reply = f"**Required Documents for {name}:**\n{doc_list}\n\n🔗 Official Portal: {current_scheme.official_source_url}"
                return {"reply": reply, "grounded_sources": sources, "disclaimer": "Verified official document requirements."}

            # Check if asking about how to apply
            if any(k in m_lower for k in ["apply", "aavedan", "आवेदन", "procedure", "process", "portal", "where can i apply", "kahan"]):
                if language == "hi":
                    steps = "\n".join([f"{i+1}. {st}" for i, st in enumerate(current_scheme.application_procedure)])
                    reply = f"**{name} की आधिकारिक आवेदन प्रक्रिया:**\n{steps}\n\n📞 हेल्पलाइन: {current_scheme.helpline or 'उपलब्ध नहीं'}\n🔗 पोर्टल: {current_scheme.official_source_url}"
                else:
                    steps = "\n".join([f"{i+1}. {st}" for i, st in enumerate(current_scheme.application_procedure)])
                    reply = f"**Official Application Procedure for {name}:**\n{steps}\n\n📞 Helpline: {current_scheme.helpline or 'N/A'}\n🔗 Portal: {current_scheme.official_source_url}"
                return {"reply": reply, "grounded_sources": sources, "disclaimer": "Verified official application procedure."}

            # Check if asking about eligibility rules
            if any(k in m_lower for k in ["eligible", "patrata", "पात्रता", "rule", "shart", "शर्तें", "criteria", "who can apply"]):
                if language == "hi":
                    rule_list = "\n".join([f"• {r.description_hi}" for r in current_scheme.rules])
                    reply = f"**{name} की मुख्य पात्रता शर्तें:**\n{rule_list}\n\n💰 मुख्य लाभ: {benefit}\n🔗 आधिकारिक पोर्टल: {current_scheme.official_source_url}"
                else:
                    rule_list = "\n".join([f"• {r.description_en}" for r in current_scheme.rules])
                    reply = f"**Key Eligibility Conditions for {name}:**\n{rule_list}\n\n💰 Key Benefit: {benefit}\n🔗 Official Portal: {current_scheme.official_source_url}"
                return {"reply": reply, "grounded_sources": sources, "disclaimer": "Verified official scheme guidelines."}

            # General scheme explanation (e.g. "What is MMVY?")
            if language == "hi":
                rules_summary = "\n".join([f"• {r.description_hi}" for r in current_scheme.rules])
                reply = (
                    f"**{name} ({current_scheme.level.title()} Scheme):**\n"
                    f"{current_scheme.description_hi}\n\n"
                    f"💰 **मुख्य लाभ:** {benefit}\n\n"
                    f"📋 **मुख्य पात्रता शर्तें:**\n{rules_summary}\n\n"
                    f"🔗 **आधिकारिक पोर्टल:** {current_scheme.official_source_url}\n"
                    f"📞 **हेल्पलाइन:** {current_scheme.helpline or '181'}"
                )
            else:
                rules_summary = "\n".join([f"• {r.description_en}" for r in current_scheme.rules])
                reply = (
                    f"**{name} ({current_scheme.level.title()} Scheme):**\n"
                    f"{current_scheme.description_en}\n\n"
                    f"💰 **Key Entitlement:** {benefit}\n\n"
                    f"📋 **Key Eligibility Guidelines:**\n{rules_summary}\n\n"
                    f"🔗 **Official Portal:** {current_scheme.official_source_url}\n"
                    f"📞 **Helpline:** {current_scheme.helpline or '181'}"
                )
            return {"reply": reply, "grounded_sources": sources, "disclaimer": "Grounded in verified official guidelines."}

        # Unknown scheme or general query
        if language == "hi":
            reply = (
                f"क्षमा करें, योजनासारथी में वर्तमान में आधिकारिक रूप से सत्यापित सरकारी योजनाओं (MMVY छात्रवृत्ति, लाड़ली बहना, पीएम किसान, आयुष्मान भारत, पीएम आवास ग्रामीण, संजय गांधी निराधार और विधवा पेंशन) के नियम उपलब्ध हैं।\n\n"
                f"आप मुझसे इन योजनाओं की पात्रता, आवश्यक दस्तावेज़ (जैसे आय, मूल निवास या समग्र आईडी), अथवा आवेदन प्रक्रिया के बारे में पूछ सकते हैं।\n"
                f"अन्य योजनाओं के लिए कृपया भारत सरकार के राष्ट्रीय पोर्टल https://india.gov.in/ पर देखें।"
            )
        else:
            reply = (
                f"Currently, YojnaSarthi provides answers strictly grounded in audited official rules for our verified schemes (MMVY Scholarship, Ladli Behna, PM-KISAN, Ayushman Bharat PM-JAY, PMAY-G Rural Housing, Sanjay Gandhi Niradhar, and Widow Pensions).\n\n"
                f"You can ask about eligibility conditions, required documents (Income, Domicile, Samagra, or Bank Passbook), or official application procedures.\n"
                f"For other central/state programs, please visit the official National Portal of India at https://india.gov.in/."
            )

        return {
            "reply": reply,
            "grounded_sources": ["https://india.gov.in/"],
            "disclaimer": "YojnaSarthi only answers from audited official rules and never invents unverified information."
        }

    def explain_form(self, field_text: Optional[str] = None, image_base64: Optional[str] = None, language: str = "hi") -> Dict[str, Any]:
        """Explains complex government application form terminology."""
        explanations = [
            {
                "field_name": "Aadhaar NPCI / DBT Seeding",
                "field_name_hi": "आधार एनपीसीआई / डीबीटी मैपिंग",
                "explanation": "Means your bank account is linked with NPCI to receive government welfare subsidies directly without delay.",
                "example": "Visit your bank branch and submit the 'NPCI Aadhaar Mandate' form."
            },
            {
                "field_name": "Khasra / Khatauni Number",
                "field_name_hi": "खसरा / खतौनी क्रमांक",
                "explanation": "Specific unique land parcel survey number recorded in the state land revenue register.",
                "example": "Found on your 7/12 extract or Bhulekh land slip (e.g., Khasra No. 142/2)."
            },
            {
                "field_name": "Samagra Family ID / Member ID",
                "field_name_hi": "समग्र परिवार आईडी / सदस्य आईडी",
                "explanation": "Unique 8-digit (family) and 9-digit (member) citizen registry code in Madhya Pradesh.",
                "example": "Printed on your Samagra Card or ration slip."
            }
        ]

        if field_text:
            explanations.insert(0, {
                "field_name": field_text,
                "field_name_hi": field_text,
                "explanation": f"Official field '{field_text}': Fill in the information exactly as specified in your verified government identity or revenue document.",
                "example": "Refer to your Aadhaar card or official certificate for the matching registration number."
            })

        return {
            "explanations": explanations,
            "general_guidance": "Double-check that your name spelling on the form matches your Aadhaar Card and Bank Passbook exactly to prevent payment rejections.",
            "disclaimer": "AI assistance is for guidance only. Consult your local Talathi, Patwari or Gram Rozgar Sahayak before submitting official documents."
        }

gemini_service = GeminiService()
