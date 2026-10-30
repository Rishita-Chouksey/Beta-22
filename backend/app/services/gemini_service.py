import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from ..config import settings
from .scheme_service import scheme_service

logger = logging.getLogger("gemini_service")

# Try importing google.genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

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
        """
        Extracts permitted profile fields from citizen's natural language input.
        Returns extracted_profile dict, detected_language, and bilingual summaries.
        """
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
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                resp_text = response.text.strip()
                # Clean markdown backticks if present
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
                logger.warning(f"Gemini parsing failed or timed out: {e}. Using deterministic fallback parser.")

        # Fallback deterministic keyword & regex parser
        return self._fallback_parse_text(text, language)

    def _fallback_parse_text(self, text: str, language: str) -> Dict[str, Any]:
        profile: Dict[str, Any] = {}
        t = text.lower()

        # Age
        age_match = re.search(r'(\d{1,2})\s*(?:years?|saal|sal|वर्ष|साल)', t)
        if age_match:
            profile["age"] = int(age_match.group(1))

        # Gender
        if any(w in t for w in ["महिला", "aurat", "female", "woman", "girl", "ladki", "विधवा"]):
            profile["gender"] = "female"
        elif any(w in t for w in ["पुरुष", "purush", "male", "man", "ladka", "admi"]):
            profile["gender"] = "male"

        # Marital status
        if any(w in t for w in ["विधवा", "widow", "vidhwa", "pati nahi"]):
            profile["marital_status"] = "widow"
            profile["gender"] = "female"
        elif any(w in t for w in ["विवाहित", "married", "shaadi", "shadi"]):
            profile["marital_status"] = "married"
        elif any(w in t for w in ["अविवाहित", "single", "unmarried", "kunwara"]):
            profile["marital_status"] = "single"

        # State
        if any(w in t for w in ["मध्य प्रदेश", "madhya pradesh", "mp", "bhopal", "indore", "jabalpur"]):
            profile["state"] = "Madhya Pradesh"
        elif any(w in t for w in ["महाराष्ट्र", "maharashtra", "mumbai", "pune", "nagpur"]):
            profile["state"] = "Maharashtra"

        # Occupation
        if any(w in t for w in ["किसान", "kisan", "farmer", "kheti", "खेती"]):
            profile["occupation"] = "farmer"
        elif any(w in t for w in ["छात्र", "विद्यार्थी", "student", "college", "padhai", "कॉलेज"]):
            profile["occupation"] = "student"
            profile["enrolled_higher_education"] = True
        elif any(w in t for w in ["मजदूर", "laborer", "majdoor"]):
            profile["occupation"] = "agricultural_worker"
        elif any(w in t for w in ["गृहिणी", "homemaker", "housewife"]):
            profile["occupation"] = "homemaker"

        # Land
        land_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hectare|ha|हेक्टेयर|एकड़|acre)', t)
        if land_match:
            val = float(land_match.group(1))
            if "एकड़" in t or "acre" in t:
                val = val * 0.4046  # convert acre to hectare
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
        if any(w in t for w in ["bpl", "बीपीएल", "गरीबी रेखा"]):
            profile["bpl_card_holder"] = True

        # Pucca house
        if any(w in t for w in ["कच्चा मकान", "kutcha house", "ghar nahi", "chhat nahi"]):
            profile["has_pucca_house"] = False

        return {
            "extracted_profile": profile,
            "detected_language": language,
            "summary_en": "Extracted key details using offline intelligent parser. Please confirm or modify your details.",
            "summary_hi": "स्मार्ट पार्सर द्वारा मुख्य विवरण निकाले गए। कृपया नीचे विवरण की पुष्टि या संशोधन करें।"
        }

    def chat_grounded_response(self, message: str, current_scheme_id: Optional[str] = None, profile: Optional[Dict[str, Any]] = None, language: str = "hi") -> Dict[str, Any]:
        """
        Provides answers strictly grounded in official scheme rules and procedures.
        Admits frankly when information is unavailable.
        """
        all_schemes = scheme_service.get_all_schemes()
        scheme_context = ""
        current_scheme = None
        if current_scheme_id:
            current_scheme = scheme_service.get_scheme_by_id(current_scheme_id)

        if current_scheme:
            scheme_context = f"""
Currently Selected Scheme: {current_scheme.name_en} ({current_scheme.name_hi})
Level: {current_scheme.level} | States: {current_scheme.applicable_states}
Benefit: {current_scheme.benefit_en}
Official Portal: {current_scheme.official_source_url}
Helpline: {current_scheme.helpline}
Rules: {[r.description_en for r in current_scheme.rules]}
Required Documents: {[d.name_en for d in current_scheme.required_documents]}
Application Procedure: {current_scheme.application_procedure}
"""
        else:
            scheme_context = f"Available Verified Schemes: {', '.join([s.name_en for s in all_schemes])}"

        if self.client:
            try:
                system_instruction = f"""
You are YojnaSarthi's Official Government Scheme AI Assistant.
Rules:
1. Answer the citizen's question strictly grounded in the official scheme knowledge provided.
2. If the user asks about an unknown scheme or something not verified, frankly say you do not have verified rules for it.
3. Answer politely in the user's requested language ({'Hindi' if language == 'hi' else 'English'}).
4. Keep explanations concise, practical, and easy for rural/semi-urban citizens to understand.
5. End with the official source or helpline if available.
"""
                prompt = f"""
Knowledge Context:
{scheme_context}

User Profile State: {profile or 'Not provided'}
Citizen Question: "{message}"
"""
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=system_instruction + "\n" + prompt
                )
                
                return {
                    "reply": response.text.strip(),
                    "grounded_sources": [current_scheme.official_source_url] if current_scheme else ["https://india.gov.in/"],
                    "disclaimer": "AI assistant guidance is grounded in official scheme rules. For official sanctions, visit the relevant department portal."
                }
            except Exception as e:
                logger.warning(f"Gemini chat failed: {e}. Using rule fallback.")

        # Deterministic Grounded Chat Fallback
        reply_en = ""
        reply_hi = ""
        sources = []

        if current_scheme:
            sources.append(current_scheme.official_source_url)
            if "document" in message.lower() or "dastavez" in message.lower() or "कागजात" in message or "दस्तावेज" in message:
                docs = ", ".join([f"{d.name_hi} ({d.name_en})" for d in current_scheme.required_documents])
                reply_hi = f"{current_scheme.name_hi} के लिए आवश्यक मुख्य दस्तावेज़ हैं: {docs}। आप इन दस्तावेज़ों को अपने नजदीकी लोक सेवा केंद्र या संबंधित पोर्टल से प्राप्त कर सकते हैं।"
                reply_en = f"The primary documents required for {current_scheme.name_en} are: {', '.join([d.name_en for d in current_scheme.required_documents])}."
            elif "apply" in message.lower() or "aavedan" in message.lower() or "आवेदन" in message or "पोर्टल" in message:
                reply_hi = f"आप {current_scheme.name_hi} के लिए आधिकारिक पोर्टल {current_scheme.official_source_url} पर या अपने नजदीकी सीएससी (कॉमन सर्विस सेंटर) पर जाकर आवेदन कर सकते हैं। हेल्पलाइन: {current_scheme.helpline}।"
                reply_en = f"You can apply for {current_scheme.name_en} on the official portal: {current_scheme.official_source_url} or visit your nearest CSC center. Helpline: {current_scheme.helpline}."
            else:
                reply_hi = f"{current_scheme.name_hi}: {current_scheme.benefit_hi}। आधिकारिक जानकारी के लिए {current_scheme.official_source_url} देखें या हेल्पलाइन {current_scheme.helpline} पर संपर्क करें।"
                reply_en = f"{current_scheme.name_en}: {current_scheme.benefit_en}. For official inquiries, visit {current_scheme.official_source_url} or call {current_scheme.helpline}."
        else:
            reply_hi = "योजनासारथी में आपका स्वागत है। आप मुझसे किसी भी सरकारी योजना की पात्रता, आवश्यक दस्तावेज़ या आवेदन प्रक्रिया के बारे में पूछ सकते हैं।"
            reply_en = "Welcome to YojnaSarthi. You can ask me about scheme eligibility rules, required documents, or official application procedures."
            sources.append("https://india.gov.in/")

        return {
            "reply": reply_hi if language == "hi" else reply_en,
            "grounded_sources": sources,
            "disclaimer": "AI guidance based on verified government rules. Does not replace official government sanction."
        }

    def explain_form(self, field_text: Optional[str] = None, image_base64: Optional[str] = None, language: str = "hi") -> Dict[str, Any]:
        """
        Explains complex government application form terminology.
        Never permanently stores images.
        """
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
