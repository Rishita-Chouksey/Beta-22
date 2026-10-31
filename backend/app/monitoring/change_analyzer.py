import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger("change_analyzer")

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class SchemeChangeAnalyzer:
    """
    AI-Assisted Scheme Change Analyzer.
    Uses Google Gemini 2.5 Flash to analyze text deltas between old and new government portal versions.
    Identifies potential revisions to eligibility criteria, income thresholds, age brackets, deadlines, and benefits.
    Includes a deterministic fallback analyzer if Gemini API is unconfigured or offline.
    
    CRITICAL RULE: AI only generates diff explanations and proposals; it NEVER approves or modifies rules directly.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if HAS_GENAI and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client for change analyzer: {e}")

    async def analyze_diff(
        self,
        scheme_id: str,
        scheme_name: str,
        source_url: str,
        old_text: str,
        new_text: str,
        detected_summary: str
    ) -> Dict[str, Any]:
        """
        Generates a human-readable summary of differences and proposed rule adjustments.
        """
        # If Gemini is available, use structured prompt
        if self.client:
            try:
                prompt = f"""
You are an expert Government Policy Analyst for the Indian Civic System YojnaSarthi.
Analyze the following change detected on an official government portal.

Scheme: {scheme_name} (ID: {scheme_id})
Official Source URL: {source_url}
Deterministic Diff Summary: {detected_summary}

--- PREVIOUS VERIFIED PORTAL TEXT (Excerpt) ---
{old_text[:2500]}

--- NEW DETECTED PORTAL TEXT (Excerpt) ---
{new_text[:2500]}

Your task:
1. Identify any potential changes to:
   - Eligibility conditions (who qualifies vs who is disqualified)
   - Income limits / landholding criteria
   - Age thresholds
   - Application deadlines / active dates
   - Required documents
   - Financial or material benefits
2. Explain the changes clearly in simple, citizen-centric terms.
3. State whether the change appears to alter legal eligibility or is just an operational/wording update.
4. Mention that this proposal requires human review and authorization by an administrative officer.

Output format:
Keep it concise, objective, and cite the official portal source. Do not invent any rules not present in the new text.
"""
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    ai_text = response.text.strip()
                    return {
                        "ai_summary": ai_text,
                        "analysis_method": "gemini-2.5-flash",
                        "requires_manual_review": True
                    }
            except Exception as e:
                logger.warning(f"Gemini change analysis call failed: {e}. Falling back to deterministic analysis.")

        # Deterministic Fallback Diff Analysis
        return {
            "ai_summary": (
                f"Automated Diff Analysis for {scheme_name}:\n"
                f"• Official Source: {source_url}\n"
                f"• Detected Modification: {detected_summary}\n"
                f"• Note: Text content length updated from {len(old_text)} to {len(new_text)} characters.\n"
                f"• Policy Impact: Requires manual verification by an authorized policy reviewer before any rules are updated."
            ),
            "analysis_method": "deterministic_diff_engine",
            "requires_manual_review": True
        }

change_analyzer = SchemeChangeAnalyzer()

