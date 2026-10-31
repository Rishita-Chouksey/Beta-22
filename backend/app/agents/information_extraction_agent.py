import os
import re
import json
import uuid
import logging
from typing import Dict, Any, Optional, List

from .models import ExtractedSchemeData, DiscoveredScheme, AgentStatus
from .repository import AgentRepository
from ..config import settings

logger = logging.getLogger("information_extraction_agent")

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

SCHEME_KEYWORDS = [
    r"yojana", r"scheme", r"kalyan", r"sahayata", r"anudan", r"subsidy",
    r"eligibility", r"patrata", r"benefit", r"pension", r"scholarship",
    r"samagra", r"eseva", r"seva", r"parivahan", r"krishi", r"kisan",
    r"yojna", r"योजना", r"पात्रता", r"लाभ", r"दस्तावेज"
]

class InformationExtractionAgent:
    """
    Agent 4: Information Extraction Agent
    Extracts structured scheme eligibility criteria, benefits, documents, and application steps.
    Uses Gemini when configured, with a deterministic regex/rule-based fallback.
    Never invents unverified fields.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        if HAS_GENAI and self.api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client for extraction: {e}")

    def contains_scheme_signals(self, text: str) -> bool:
        text_lower = text.lower()
        matches = 0
        for kw in SCHEME_KEYWORDS:
            if re.search(kw, text_lower):
                matches += 1
                if matches >= 2:
                    return True
        return False

    def extract_with_gemini(self, text: str, source_url: str) -> Optional[ExtractedSchemeData]:
        """
        Uses Gemini LLM for structured scheme extraction with strict groundedness and evidence citations.
        """
        if not self.gemini_client:
            return None

        # Truncate text to fit context if very long
        sample_text = text[:15000]

        prompt = f"""
You are an expert Government Scheme Information Extraction Agent for Indian public services.
Analyze the following official text retrieved from {source_url}.
Extract structured scheme information according to these strict rules:
1. Only extract information explicitly stated in the text.
2. DO NOT invent, assume, or hallucinate missing criteria or details.
3. If an attribute (e.g., income ceiling, deadline) is not stated, return null.
4. For every extracted claim, provide a short verbatim excerpt from the text in "evidence_excerpts".

Return a valid JSON object matching this structure:
{{
  "scheme_name": "Full official name of the scheme",
  "department": "Ministry or department name, or null",
  "classification": "central" or "state",
  "state": "Name of state (e.g. Madhya Pradesh) or 'All'",
  "description": "Clear 2-3 sentence summary of what the scheme is",
  "intended_beneficiaries": "Target group (e.g. farmers, college students, destitute widows)",
  "eligibility_conditions": {{
    "min_age": integer or null,
    "max_age": integer or null,
    "income_limit": integer or null,
    "gender": "male" / "female" / "transgender" / "all" or null,
    "caste_category": ["SC", "ST", "OBC", "General", "EWS"] or null,
    "domicile_state": "state name or null"
  }},
  "age_criteria": "Readable age rule description or null",
  "income_criteria": "Readable income rule description or null",
  "gender_category_criteria": "Readable gender or caste criteria or null",
  "benefits": "Exact monetary or in-kind benefits described",
  "required_documents": ["List of mandatory documents mentioned"],
  "application_process": ["Step 1...", "Step 2..."],
  "deadline": "Deadline or validity date if stated, else null",
  "official_application_url": "Portal link if mentioned, else null",
  "official_guideline_url": "Guideline or circular link if mentioned, else null",
  "evidence_excerpts": {{
    "scheme_name": "verbatim text quote",
    "eligibility": "verbatim text quote",
    "benefits": "verbatim text quote",
    "documents": "verbatim text quote"
  }},
  "confidence": 0.95
}}

Official Text:
{sample_text}
"""
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            data = json.loads(response.text)
            now = AgentRepository.now_iso()
            return ExtractedSchemeData(
                scheme_name=data.get("scheme_name", "Unknown Scheme"),
                department=data.get("department"),
                classification=data.get("classification", "central"),
                state=data.get("state"),
                description=data.get("description"),
                intended_beneficiaries=data.get("intended_beneficiaries"),
                eligibility_conditions=data.get("eligibility_conditions") or {},
                age_criteria=data.get("age_criteria"),
                income_criteria=data.get("income_criteria"),
                gender_category_criteria=data.get("gender_category_criteria"),
                benefits=data.get("benefits"),
                required_documents=data.get("required_documents") or [],
                application_process=data.get("application_process") or [],
                deadline=data.get("deadline"),
                official_application_url=data.get("official_application_url") or source_url,
                official_guideline_url=data.get("official_guideline_url"),
                extraction_timestamp=now,
                evidence_excerpts=data.get("evidence_excerpts") or {},
                confidence=float(data.get("confidence", 0.90))
            )
        except Exception as e:
            logger.warning(f"Gemini extraction failed: {e}. Falling back to deterministic extractor.")
            return None

    def extract_with_rules(self, text: str, source_url: str) -> ExtractedSchemeData:
        """
        Deterministic regex and keyword-based extraction fallback.
        Ensures the system continues functioning without external LLM dependencies.
        """
        now = AgentRepository.now_iso()

        # Scheme name heuristic: First prominent title line or line containing 'Yojana' / 'Scheme'
        scheme_name = "Government Scheme"
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines[:10]:
            if len(line) > 5 and len(line) < 100:
                if any(w in line.lower() for w in ["yojana", "scheme", "seva", "sewa", "portal", "योजना", "सेवा"]):
                    scheme_name = line
                    break
        if scheme_name == "Government Scheme" and lines:
            scheme_name = lines[0][:80]

        # Classification & State heuristic
        state = None
        classification = "central"
        if "mp.gov.in" in source_url or "madhya pradesh" in text.lower() or "मध्य प्रदेश" in text:
            state = "Madhya Pradesh"
            classification = "state"
        elif "data.gov.in" in source_url:
            classification = "central"

        # Evidence excerpts container
        evidence = {}

        # Eligibility section extraction
        elig_conditions: Dict[str, Any] = {}
        age_match = re.search(r"(?:age|आयु|उम्र)[\s\:\-]+([0-9]{1,2})\s*(?:to|से|-)\s*([0-9]{1,2})", text, re.I)
        if age_match:
            elig_conditions["min_age"] = int(age_match.group(1))
            elig_conditions["max_age"] = int(age_match.group(2))
            evidence["age"] = age_match.group(0)

        income_match = re.search(r"(?:income|आय)[\s\:\-₹rs\.]*([0-9\,]+)", text, re.I)
        if income_match:
            evidence["income"] = income_match.group(0)

        # Documents extraction
        docs = []
        doc_keywords = ["aadhaar", "samagra", "ration card", "income certificate", "domicile", "bank passbook", "pan card"]
        for dkw in doc_keywords:
            if dkw in text.lower():
                docs.append(dkw.title())

        # Benefits extraction
        benefits = None
        benefit_match = re.search(r"(?:benefit|लाभ|सहायता राशि|grant)[\s\:\-₹rs\.]*([^\n\.\;]{10,120})", text, re.I)
        if benefit_match:
            benefits = benefit_match.group(0).strip()
            evidence["benefits"] = benefits

        # Application Process extraction
        app_steps = []
        for line in lines:
            if re.match(r"^(?:step\s*[0-9]|चरण\s*[0-9]|[0-9]+\.)\s*", line, re.I):
                app_steps.append(line)
            if len(app_steps) >= 5:
                break

        # Deadline
        deadline = None
        date_match = re.search(r"(?:deadline|last date|अंतिम तिथि)[\s\:\-]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})", text, re.I)
        if date_match:
            deadline = date_match.group(1)
            evidence["deadline"] = date_match.group(0)

        return ExtractedSchemeData(
            scheme_name=scheme_name,
            department=None,
            classification=classification,
            state=state,
            description=lines[1] if len(lines) > 1 else lines[0] if lines else None,
            intended_beneficiaries=None,
            eligibility_conditions=elig_conditions,
            age_criteria=evidence.get("age"),
            income_criteria=evidence.get("income"),
            gender_category_criteria=None,
            benefits=benefits,
            required_documents=docs,
            application_process=app_steps,
            deadline=deadline,
            official_application_url=source_url,
            official_guideline_url=None,
            extraction_timestamp=now,
            evidence_excerpts=evidence,
            confidence=0.80 if evidence else 0.65
        )

    def extract_and_store(self, source_id: str, source_url: str, text: str) -> Optional[ExtractedSchemeData]:
        """
        Executes extraction pipeline, stores discovered scheme record, and logs run.
        """
        if not self.contains_scheme_signals(text):
            logger.info(f"Source {source_url} does not contain scheme signals. Skipping extraction.")
            return None

        # Attempt Gemini extraction first
        extracted = None
        if self.gemini_client:
            extracted = self.extract_with_gemini(text, source_url)

        # Fallback to rule engine if Gemini not available or failed
        if not extracted:
            extracted = self.extract_with_rules(text, source_url)

        # Persist into discovered_schemes table
        scheme_id = "disc-" + uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"{source_id}:{extracted.scheme_name.casefold()}"
        ).hex[:24]
        now = AgentRepository.now_iso()

        disc_scheme = DiscoveredScheme(
            id=scheme_id,
            scheme_name=extracted.scheme_name,
            department=extracted.department,
            state=extracted.state,
            source_id=source_id,
            source_url=source_url,
            extracted_data=extracted.model_dump(),
            verification_status="unverified",
            first_discovered_at=now,
            last_updated_at=now
        )
        AgentRepository.add_or_update_discovered_scheme(disc_scheme)

        return extracted
