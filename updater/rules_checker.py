import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from pydantic import BaseModel

logger = logging.getLogger("updater.rules_checker")

@dataclass
class CheckerResult:
    value: Optional[Any]
    unit: Optional[str]
    evidence_snippet: Optional[str]
    confidence: float
    raw_match: Optional[str] = None
    checker_name: str = "rules_checker"

def parse_indian_number(text: str) -> Optional[float]:
    """
    Parses numbers with Indian comma notation and words like lakh, crore, thousand.
    e.g. '₹6,000' -> 6000.0
         '₹ 2.5 lakh' -> 250000.0
         '6,00,000' -> 600000.0
         '1.2 करोड़' -> 12000000.0
    """
    if not text:
        return None

    clean = text.replace("₹", "").replace("Rs.", "").replace("Rs", "").replace("/-", "").strip()

    # Look for multiplier words
    multiplier = 1.0
    m_lakh = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|लाख|লাখ)", clean, re.IGNORECASE)
    if m_lakh:
        return float(m_lakh.group(1)) * 100000.0

    m_crore = re.search(r"(\d+(?:\.\d+)?)\s*(?:crore|cr|करोड़|কোটি)", clean, re.IGNORECASE)
    if m_crore:
        return float(m_crore.group(1)) * 10000000.0

    m_k = re.search(r"(\d+(?:\.\d+)?)\s*(?:thousand|हजार|হাজার)", clean, re.IGNORECASE)
    if m_k:
        return float(m_k.group(1)) * 1000.0

    # Extract digits with optional commas and decimals
    digits_m = re.search(r"\b(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)\b", clean)
    if digits_m:
        raw_num = digits_m.group(1).replace(",", "")
        try:
            return float(raw_num)
        except ValueError:
            return None
    return None

class RulesChecker:
    """
    Deterministic AST & regex rules checker (Checker 1).
    Pure AI-free parser extracting official scheme parameters from page text.
    """

    def extract_income_limit(self, text: str) -> CheckerResult:
        """
        Extracts annual/family income limit.
        e.g. 'income not exceeding ₹6,00,000 per annum'
             'वार्षिक आय ₹2.5 लाख से अधिक नहीं'
             'family income up to ₹2,00,000'
        """
        num_pattern = r"(\d+(?:\.\d+)?\s*(?:lakh|lac|लाख|লাখ|crore|करोड़|thousand|हजार|হাজার)|\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)"

        patterns = [
            rf"([^\.\n।]*?(?:annual|family|household|माता-पिता|परिवार|वार्षिक|পারিবারিক|বার্ষিক)[^\.\n।]*?(?:आय|income|আয়)[^\.\n।]*?(?:₹|Rs\.?)\s*{num_pattern}[^\.\n।]*\b)",
            rf"([^\.\n।]*?(?:income|आय|আয়)[^\.\n।]*?(?:limit|ceiling|upto|up to|exceeding|अधिक नहीं|বেশি নয়)[^\.\n।]*?(?:₹|Rs\.?)\s*{num_pattern}[^\.\n।]*\b)",
            rf"([^\.\n।]*?(?:₹|Rs\.?)\s*{num_pattern}\s*(?:per annum|per year|वार्षिक|বার্ষিক)[^\.\n।]*\b)"
        ]

        matches = []
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                snippet = match.group(1).strip()
                num_str = match.group(2)
                val = parse_indian_number(num_str)
                if val is not None and 10000 <= val <= 2000000:
                    matches.append((val, snippet))

        if not matches:
            return CheckerResult(value=None, unit="INR", evidence_snippet=None, confidence=0.0)

        # Disambiguation: check if all unique values agree
        unique_vals = list({m[0] for m in matches})
        if len(unique_vals) == 1:
            val = unique_vals[0]
            snippet = matches[0][1]
            return CheckerResult(
                value=float(val),
                unit="INR",
                evidence_snippet=snippet,
                confidence=1.0,
                raw_match=str(val)
            )
        else:
            # Ambiguous: multiple different income values mentioned
            logger.warning(f"Multiple ambiguous income limits detected: {unique_vals}")
            return CheckerResult(value=None, unit="INR", evidence_snippet=None, confidence=0.0)

    def extract_benefit_amount(self, text: str) -> CheckerResult:
        """
        Extracts monetary benefit amount.
        e.g. '₹6,000 per year' (PM-KISAN), '₹1,250 per month' (Ladli Behna).
        """
        patterns = [
            r"([^\.\n]*?(?:₹|Rs\.?)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:lakh|lac|लाख|লাখ)?)\s*(?:per year|annually|प्रति वर्ष|প্রতি বছর|per month|प्रति माह|প্রতি মাস)[^\.\n]*)",
            r"([^\.\n]*?(?:financial assistance|grant|किस्त|सहायता|অনুদান)\s*(?:of|की|র)?\s*(?:₹|Rs\.?)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)[^\.\n]*)"
        ]

        matches = []
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                snippet = match.group(1).strip()
                num_str = match.group(2)
                val = parse_indian_number(num_str)
                if val is not None and 500 <= val <= 10000000:
                    matches.append((val, snippet))

        if not matches:
            return CheckerResult(value=None, unit="INR", evidence_snippet=None, confidence=0.0)

        unique_vals = list({m[0] for m in matches})
        if len(unique_vals) == 1:
            return CheckerResult(
                value=float(unique_vals[0]),
                unit="INR",
                evidence_snippet=matches[0][1],
                confidence=1.0,
                raw_match=str(unique_vals[0])
            )
        return CheckerResult(value=None, unit="INR", evidence_snippet=None, confidence=0.0)

    def extract_age_range(self, text: str) -> CheckerResult:
        """
        Extracts age requirement.
        e.g. 'age between 21 and 60 years' -> min_age=21, max_age=60
             'age 40 years and above' -> min_age=40, max_age=None
        """
        between_pat = r"([^\.\n]*?(?:age|आयु|বয়স)\s*(?:between|of|from)?\s*(\d{1,2})\s*(?:to|and|-|से)\s*(\d{1,2})\s*(?:years|वर्ष|বছর)[^\.\n]*)"
        m_between = re.search(between_pat, text, re.IGNORECASE)
        if m_between:
            min_age = int(m_between.group(2))
            max_age = int(m_between.group(3))
            return CheckerResult(
                value={"min_age": min_age, "max_age": max_age},
                unit="years",
                evidence_snippet=m_between.group(1).strip(),
                confidence=1.0,
                raw_match=f"{min_age}-{max_age}"
            )

        min_pat = r"([^\.\n]*?(?:age|आयु|বয়স)\s*(?:above|at least|minimum|कम से कम|ন্যূনতম)?\s*(\d{1,2})\s*(?:years|वर्ष|বছর)\s*(?:or above|and above|अधिक)[^\.\n]*)"
        m_min = re.search(min_pat, text, re.IGNORECASE)
        if m_min:
            min_age = int(m_min.group(2))
            return CheckerResult(
                value={"min_age": min_age, "max_age": None},
                unit="years",
                evidence_snippet=m_min.group(1).strip(),
                confidence=1.0,
                raw_match=f"{min_age}+"
            )

        return CheckerResult(value=None, unit="years", evidence_snippet=None, confidence=0.0)

    def extract_land_limit(self, text: str) -> CheckerResult:
        """
        Extracts landholding limits and normalizes to hectares.
        1 acre = 0.404686 hectares.
        """
        pat_ha = r"([^\.\n]*?(\d+(?:\.\d+)?)\s*(?:hectares?|हेक्टेयर|হেক্টর)[^\.\n]*)"
        m_ha = re.search(pat_ha, text, re.IGNORECASE)
        if m_ha:
            val = float(m_ha.group(2))
            return CheckerResult(
                value=round(val, 2),
                unit="hectares",
                evidence_snippet=m_ha.group(1).strip(),
                confidence=1.0,
                raw_match=f"{val} ha"
            )

        pat_acre = r"([^\.\n]*?(\d+(?:\.\d+)?)\s*(?:acres?|एकड़|একর)[^\.\n]*)"
        m_acre = re.search(pat_acre, text, re.IGNORECASE)
        if m_acre:
            val = float(m_acre.group(2))
            val_ha = round(val * 0.404686, 2)
            return CheckerResult(
                value=val_ha,
                unit="hectares",
                evidence_snippet=m_acre.group(1).strip(),
                confidence=1.0,
                raw_match=f"{val} acre -> {val_ha} ha"
            )

        return CheckerResult(value=None, unit="hectares", evidence_snippet=None, confidence=0.0)

    def check(self, extractor_kind: str, text: str) -> CheckerResult:
        if not text:
            return CheckerResult(value=None, unit=None, evidence_snippet=None, confidence=0.0)

        if extractor_kind in ("income_limit", "annual_income"):
            return self.extract_income_limit(text)
        elif extractor_kind in ("amount_inr", "benefit_amount"):
            return self.extract_benefit_amount(text)
        elif extractor_kind in ("age_range", "age"):
            return self.extract_age_range(text)
        elif extractor_kind in ("land_area", "landholding_hectares"):
            return self.extract_land_limit(text)
        else:
            logger.warning(f"Unknown extractor kind: {extractor_kind}")
            return CheckerResult(value=None, unit=None, evidence_snippet=None, confidence=0.0)

rules_checker = RulesChecker()
