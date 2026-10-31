import re
import hashlib
from html.parser import HTMLParser
from typing import Tuple, Dict, Any

class HTMLContentCleaner(HTMLParser):
    """
    Standard-library HTML cleaner that ignores structural chrome:
    scripts, styles, headers, footers, navbars, and comments.
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.ignore_tags = {"script", "style", "nav", "header", "footer", "aside", "noscript", "iframe"}
        self.current_ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.ignore_tags:
            self.current_ignored += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.ignore_tags and self.current_ignored > 0:
            self.current_ignored -= 1

    def handle_data(self, d):
        if self.current_ignored == 0:
            self.fed.append(d)

    def get_cleaned_text(self) -> str:
        return " ".join(self.fed)

def sanitize_extracted_text(raw_html_or_text: str) -> str:
    """
    Extracts core textual content, strips transient timestamps,
    dynamic session tokens, CSRF tokens, and collapses whitespace.
    """
    if not raw_html_or_text:
        return ""

    # Parse and clean HTML tags if HTML is present
    if "<" in raw_html_or_text and ">" in raw_html_or_text:
        parser = HTMLContentCleaner()
        try:
            parser.feed(raw_html_or_text)
            text = parser.get_cleaned_text()
        except Exception:
            # Fallback regex strip if HTML is malformed
            text = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", raw_html_or_text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
    else:
        text = raw_html_or_text

    # Strip dynamic timestamps and session patterns that create false change alerts
    # e.g., "Page generated at 31/10/2026 14:30:22", "Timestamp: 1698745234"
    patterns_to_remove = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}(:\d{2})?\b",  # Date-time
        r"\b(current\s+time|last\s+updated|generated\s+on|page\s+load\s+time)[:\s]+[^\n,\.]{1,40}",  # Timestamps
        r"\b(csrf[-_]?token|session[-_]?id|auth[-_]?token)[=:][\s]*[a-zA-Z0-9_\-]{8,}\b",  # Tokens
        r"&[a-z]{2,8};|&#\d+;",  # HTML entities
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def calculate_content_fingerprint(sanitized_text: str) -> str:
    """Computes a deterministic SHA-256 fingerprint for cleaned text."""
    if not sanitized_text:
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # Hash of empty string
    return hashlib.sha256(sanitized_text.encode("utf-8")).hexdigest()

def detect_meaningful_difference(old_text: str, new_text: str) -> Tuple[bool, str]:
    """
    Determines if difference between old and new content represents a meaningful
    change in scheme rules, deadlines, benefits, or documents rather than minor layout fluff.
    Returns: (is_meaningful, summary_or_diff)
    """
    clean_old = sanitize_extracted_text(old_text)
    clean_new = sanitize_extracted_text(new_text)

    if clean_old == clean_new:
        return False, "No meaningful textual changes detected."

    # Extract clean tokens without trailing punctuation
    tokens_old = set([re.sub(r"^[^\w\d]+|[^\w\d]+$", "", w).lower() for w in clean_old.split() if w.strip()])
    tokens_new = set([re.sub(r"^[^\w\d]+|[^\w\d]+$", "", w).lower() for w in clean_new.split() if w.strip()])

    added_tokens = tokens_new - tokens_old
    removed_tokens = tokens_old - tokens_new

    # Check for critical civic keywords (numbers, income limits, ages, dates, eligibility terms)
    critical_keywords = {
        "rupees", "रुपये", "lakh", "लाख", "crore", "eligible", "पात्र", "ineligible", "अपात्र",
        "deadline", "अंतिम", "tithi", "document", "दस्तावेज़", "certificate", "प्रमाण",
        "age", "आयु", "income", "आय", "annual", "वार्षिक", "land", "भूमि", "hectare", "हेक्टेयर",
        "portal", "apply", "आवेदन", "bank", "dbt", "aadhar", "aadhaar", "आधार"
    }

    critical_added = [w for w in added_tokens if w in critical_keywords or re.match(r"^\d+(?:\.\d+)?$", w)]
    critical_removed = [w for w in removed_tokens if w in critical_keywords or re.match(r"^\d+(?:\.\d+)?$", w)]

    # If critical civic keywords or numbers changed, or significant length delta
    if critical_added or critical_removed or abs(len(clean_new) - len(clean_old)) > 80:
        summary = (
            f"Meaningful content update detected. "
            f"Added terms/numbers: {', '.join(critical_added[:6]) or 'None'}. "
            f"Removed terms/numbers: {', '.join(critical_removed[:6]) or 'None'}. "
            f"Net text delta: {len(clean_new) - len(clean_old):+d} characters."
        )
        return True, summary

    return False, "Insignificant layout or formatting variation."
