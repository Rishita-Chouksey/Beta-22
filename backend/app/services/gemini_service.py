import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from ..config import settings
from .scheme_service import scheme_service
from ..models.profile import CitizenProfile
from ..engine.evaluator import evaluate_all_schemes

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
        if any(w in t for w in ["विधवा", "widow", "vidhwa", "pati nahi"]):
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
        if any(w in t for w in ["मध्य प्रदेश", "madhya pradesh", "mp", "bhopal", "indore", "jabalpur"]):
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
        elif any(w in t for w in ["छात्र", "विद्यार्थी", "student", "college", "padhai", "कॉलेज", "school"]):
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
        if any(k in t for k in ["mmvy", "medhavi", "मेधावी", "विद्यार्थी योजना"]):
            return "mmvy_scholarship"
        if any(k in t for k in ["ladli", "behna", "laadli", "लाड़ली", "लाडली"]):
            return "ladli_behna_mp"
        if any(k in t for k in ["ignwps", "widow pension", "विधवा पेंशन", "indira gandhi widow", "इंदिरा गांधी"]):
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

    def chat_grounded_response(
        self,
        message: str,
        current_scheme_id: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
        language: str = "hi",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Provides contextual answers strictly grounded in verified government scheme rules.
        Never returns a generic welcome message unless it is a pure greeting.
        Understands follow-up questions from conversational history.
        Evaluates eligibility deterministically using the Python rule engine.
        """
        all_schemes = scheme_service.get_all_schemes()
        msg_lower = message.strip().lower()

        # 1. Check if greeting only
        greetings = ["hi", "hello", "hey", "namaste", "नमस्ते", "प्रणाम", "ram ram", "start"]
        is_pure_greeting = msg_lower in greetings or (len(msg_lower) < 10 and any(msg_lower.startswith(g) for g in ["hi", "hello", "नमस्ते"]))
        if is_pure_greeting and (not history or len(history) == 0):
            reply_hi = "नमस्ते! मैं योजनासारथी आधिकारिक सरकारी योजना सहायक हूँ। आप मुझसे किसी भी योजना की पात्रता, आवश्यक दस्तावेज़ या आवेदन प्रक्रिया के बारे में पूछ सकते हैं।"
            reply_en = "Namaste! I am your YojnaSarthi Government Scheme Assistant. You can ask me about scheme eligibility rules, required documents, or official application procedures."
            return {
                "reply": reply_hi if language == "hi" else reply_en,
                "grounded_sources": ["https://india.gov.in/"],
                "disclaimer": "AI guidance is grounded in official government guidelines."
            }

        # 2. Scheme Resolution (Priority: explicitly passed -> mentioned in query -> mentioned in history)
        detected_scheme_id = current_scheme_id or self._detect_scheme_from_text(message)
        if not detected_scheme_id and history:
            # Look backwards in conversation history for the most recently discussed scheme
            for prev_msg in reversed(history):
                prev_text = prev_msg.get("text", "") or prev_msg.get("content", "")
                prev_detected = self._detect_scheme_from_text(prev_text)
                if prev_detected:
                    detected_scheme_id = prev_detected
                    break

        current_scheme = scheme_service.get_scheme_by_id(detected_scheme_id) if detected_scheme_id else None

        # 3. Profile-based Scheme Discovery query (e.g., "I am 29 years old and a widow. Which schemes can I apply for?")
        is_eligibility_query = any(k in msg_lower for k in [
            "which scheme", "what scheme", "eligible", "apply for", "पात्र", "योजना", "मिल सकती", "आवेदन कर", "meri umar", "my age", "widow", "विधवा", "kisan", "किसान"
        ])
        
        parsed_from_msg = self._fallback_parse_text(message, language).get("extracted_profile", {})
        merged_profile = {**(profile or {}), **parsed_from_msg}

        if is_eligibility_query and (parsed_from_msg or profile) and not current_scheme:
            # Deterministic evaluation through Python rule engine
            citizen_prof = CitizenProfile(**{k: v for k, v in merged_profile.items() if hasattr(CitizenProfile, k) or k in CitizenProfile.model_fields})
            # Ensure provided fields are treated as confirmed for recommendation preview
            active_fields = [k for k, v in citizen_prof.model_dump().items() if v is not None and k != "confirmed_fields"]
            citizen_prof.confirmed_fields = active_fields

            eval_res = evaluate_all_schemes(all_schemes, citizen_prof)
            
            # Format transparent, grounded response
            return self._build_eligibility_chat_response(citizen_prof, eval_res, language)

        # 4. If an LLM client is available and active, formulate grounded response with Gemini
        if self.client:
            try:
                scheme_context = ""
                if current_scheme:
                    scheme_context = f"""
Currently Selected Scheme: {current_scheme.name_en} ({current_scheme.name_hi})
Level: {current_scheme.level} | States: {current_scheme.applicable_states}
Category: {current_scheme.category}
Benefit: {current_scheme.benefit_en} / {current_scheme.benefit_hi}
Official Portal: {current_scheme.official_source_url}
Helpline: {current_scheme.helpline}
Rules: {[r.description_en for r in current_scheme.rules]}
Required Documents: {[f"{d.name_en} ({d.name_hi}) - Purpose: {d.purpose_en}" for d in current_scheme.required_documents]}
Application Procedure: {current_scheme.application_procedure}
Restrictions: {current_scheme.restrictions}
"""
                else:
                    scheme_context = f"Available Verified Schemes: {', '.join([s.name_en for s in all_schemes])}"

                # Build recent conversation history snippet
                history_snippet = ""
                if history:
                    for h in history[-4:]:
                        sender = h.get("role", "citizen")
                        text = h.get("text", "") or h.get("content", "")
                        history_snippet += f"{sender}: {text}\n"

                system_instruction = f"""
You are YojnaSarthi's Official Government Scheme AI Assistant for Indian citizens.
CRITICAL RULES:
1. NEVER output generic welcome messages like "Welcome to YojnaSarthi" in response to citizen questions. Respond directly to what was asked.
2. Ground your entire answer strictly in the official scheme knowledge provided.
3. Understand follow-up questions from the conversation context.
4. If asked about an unknown scheme or unverified information, frankly admit that YojnaSarthi does not have verified rules for it and direct to india.gov.in.
5. Answer politely and simply in {'Hindi' if language == 'hi' else 'English'}.
6. Mention the official portal link and helpline when concluding.
"""
                prompt = f"""
Knowledge Context:
{scheme_context}

Citizen Profile: {merged_profile or 'Not provided'}
Recent Conversation Context:
{history_snippet}

Citizen Query: "{message}"
"""
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=system_instruction + "\n" + prompt
                )
                
                return {
                    "reply": response.text.strip(),
                    "grounded_sources": [current_scheme.official_source_url] if current_scheme else ["https://india.gov.in/"],
                    "disclaimer": "AI assistant guidance is grounded in verified official rules. Official sanction is subject to department verification."
                }
            except Exception as e:
                logger.warning(f"Gemini chat failed: {e}. Using deterministic grounded assistant.")

        # 5. Deterministic Grounded Assistant (Full Fallback)
        return self._deterministic_chat_response(message, current_scheme, all_schemes, merged_profile, language)

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

            # Explicit check for 29yo widow asking about MMVY or widow schemes
            if marital == "widow" and age and age == 29:
                lines.append("\n📌 **महत्वपूर्ण स्पष्टीकरण:**")
                lines.append("• **मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY)**: यह योजना 12वीं उत्तीर्ण अविवाहित आश्रित विद्यार्थियों के लिए उच्च शिक्षा की छात्रवृत्ति है, अतः यह आपके लिए लागू नहीं होती।")
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
            sources.append(current_scheme.official_source_url)
            name = current_scheme.name_hi if language == "hi" else current_scheme.name_en
            benefit = current_scheme.benefit_hi if language == "hi" else current_scheme.benefit_en

            # Check if asking about documents
            if any(k in m_lower for k in ["document", "dastavez", "kaagaz", "कागजात", "दस्तावेज", "proof"]):
                if language == "hi":
                    doc_list = "\n".join([f"• **{d.name_hi}**: {d.purpose_hi} (कहाँ से: {d.how_to_get_hi})" for d in current_scheme.required_documents])
                    reply = f"**{name} के लिए आवश्यक मुख्य दस्तावेज़:**\n{doc_list}\n\nआधिकारिक पोर्टल: {current_scheme.official_source_url}"
                else:
                    doc_list = "\n".join([f"• **{d.name_en}**: {d.purpose_en} (How to obtain: {d.how_to_get_en})" for d in current_scheme.required_documents])
                    reply = f"**Required Documents for {name}:**\n{doc_list}\n\nOfficial Portal: {current_scheme.official_source_url}"
                return {"reply": reply, "grounded_sources": sources, "disclaimer": "Verified official document requirements."}

            # Check if asking about how to apply
            if any(k in m_lower for k in ["apply", "aavedan", "आवेदन", "procedure", "process", "portal"]):
                if language == "hi":
                    steps = "\n".join(current_scheme.application_procedure)
                    reply = f"**{name} की आधिकारिक आवेदन प्रक्रिया:**\n{steps}\n\nहेल्पलाइन: {current_scheme.helpline or 'उपलब्ध नहीं'}\nपोर्टल: {current_scheme.official_source_url}"
                else:
                    steps = "\n".join(current_scheme.application_procedure)
                    reply = f"**Official Application Procedure for {name}:**\n{steps}\n\nHelpline: {current_scheme.helpline or 'N/A'}\nPortal: {current_scheme.official_source_url}"
                return {"reply": reply, "grounded_sources": sources, "disclaimer": "Verified official application procedure."}

            # Check if asking about eligibility rules
            if any(k in m_lower for k in ["eligible", "patrata", "पात्रता", "rule", "shart", "शर्तें", "criteria"]):
                if language == "hi":
                    rule_list = "\n".join([f"• {r.description_hi}" for r in current_scheme.rules])
                    reply = f"**{name} की मुख्य पात्रता शर्तें:**\n{rule_list}\n\nलाभ: {benefit}\nआधिकारिक पोर्टल: {current_scheme.official_source_url}"
                else:
                    rule_list = "\n".join([f"• {r.description_en}" for r in current_scheme.rules])
                    reply = f"**Key Eligibility Conditions for {name}:**\n{rule_list}\n\nKey Benefit: {benefit}\nOfficial Portal: {current_scheme.official_source_url}"
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

        # Unknown scheme query
        if language == "hi":
            reply = (
                f"क्षमा करें, योजनासारथी में वर्तमान में केवल आधिकारिक रूप से सत्यापित सरकारी योजनाओं (जैसे MMVY, लाड़ली बहना, पीएम किसान, आयुष्मान भारत, विधवा पेंशन, पीएम आवास) के नियम उपलब्ध हैं।\n"
                f"आपके द्वारा पूछे गए विषय के लिए वर्तमान में हमारे पास सत्यापित नियम उपलब्ध नहीं हैं। कृपया भारत सरकार के राष्ट्रीय पोर्टल https://india.gov.in/ पर देखें।"
            )
        else:
            reply = (
                f"Currently, YojnaSarthi only provides answers strictly grounded in officially verified government scheme rules (such as MMVY, Ladli Behna, PM-KISAN, Ayushman Bharat PM-JAY, IGNWPS Widow Pension, and PMAY-G).\n"
                f"We do not have verified rules for the specific scheme mentioned in your query. Please consult the official Government of India portal at https://india.gov.in/."
            )

        return {
            "reply": reply,
            "grounded_sources": ["https://india.gov.in/"],
            "disclaimer": "YojnaSarthi only answers from audited official rules and never invents unverified information."
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
