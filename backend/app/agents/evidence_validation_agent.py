import re
import logging
from urllib.parse import urlparse
from typing import Dict, Any, List

from .models import ExtractedSchemeData

logger = logging.getLogger("evidence_validation_agent")

OFFICIAL_GOV_SUFFIXES = [".gov.in", ".nic.in", ".mp.gov.in"]

class EvidenceValidationAgent:
    """
    Agent 6: Evidence Validation Agent
    Validates that every extracted fact, criterion, and benefit change is grounded
    in verifiable textual evidence from official government sources.
    Flags missing or speculative criteria as UNKNOWN.
    """

    def is_trusted_url(self, url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url)
        domain = parsed.netloc.lower().split(":")[0]
        return any(domain.endswith(suffix) or domain == suffix.lstrip(".") for suffix in OFFICIAL_GOV_SUFFIXES)

    def validate_evidence(self, extracted: ExtractedSchemeData, raw_text: str, source_url: str) -> Dict[str, Any]:
        """
        Validates evidence citations and computes confidence score.
        """
        raw_text_lower = raw_text.lower()
        verified_evidence: Dict[str, str] = {}
        unverified_claims: List[str] = []

        # 1. URL trustworthiness
        url_trusted = self.is_trusted_url(source_url)
        if not url_trusted:
            unverified_claims.append(f"Source URL domain is not in verified official government domains: {source_url}")

        # 2. Check each evidence excerpt against raw text
        for claim_field, excerpt in extracted.evidence_excerpts.items():
            if not excerpt or excerpt == "UNKNOWN":
                continue
            excerpt_clean = excerpt.strip().lower()
            # Normalize whitespace
            excerpt_clean = " ".join(excerpt_clean.split())
            raw_text_normalized = " ".join(raw_text_lower.split())

            if excerpt_clean and excerpt_clean in raw_text_normalized:
                verified_evidence[claim_field] = excerpt
            else:
                unverified_claims.append(f"Excerpt for '{claim_field}' not found verbatim in crawled source.")

        # 3. Check for UNKNOWN or missing critical fields
        # If income criteria is missing, ensure it's not hallucinated
        if not extracted.income_criteria and extracted.eligibility_conditions.get("income_limit") is None:
            verified_evidence["income_limit"] = "UNKNOWN (Not specified in source)"

        if not extracted.deadline:
            verified_evidence["deadline"] = "UNKNOWN (Open / Not specified)"

        # 4. Calculate Confidence Score
        confidence = extracted.confidence
        if not url_trusted:
            confidence = max(0.1, confidence - 0.4)
        if unverified_claims:
            confidence = max(0.2, confidence - (0.15 * len(unverified_claims)))

        is_valid = (len(unverified_claims) == 0) and url_trusted and (confidence >= 0.60)

        return {
            "is_valid": is_valid,
            "confidence": round(confidence, 2),
            "verified_evidence": verified_evidence,
            "unverified_claims": unverified_claims,
            "reason": "Evidence verified against official source." if is_valid else f"Validation failed: {'; '.join(unverified_claims)}"
        }
