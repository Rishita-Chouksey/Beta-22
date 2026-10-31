from __future__ import annotations
import io
import re
import hashlib
import unicodedata
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    from selectolax.parser import HTMLParser
    HAS_SELECTOLAX = True
except ImportError:
    HAS_SELECTOLAX = False

from bs4 import BeautifulSoup
import pypdf

logger = logging.getLogger("updater.extract_text")

Tuple_Text_Scanned = Tuple[str, bool]

@dataclass
class ExtractedDocument:
    raw_text: str
    clean_text: str
    sha256: str
    is_pdf: bool = False
    is_scanned_pdf: bool = False
    word_count: int = 0

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Unicode normalize
    text = unicodedata.normalize("NFKC", text)

    # Standardize currency and common terms
    text = text.replace("Rs.", "₹").replace("Rs ", "₹ ").replace("INR", "₹")

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def calculate_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def extract_from_html(content_bytes: bytes, encoding: str = "utf-8") -> str:
    try:
        html_str = content_bytes.decode(encoding, errors="replace")
    except Exception:
        html_str = str(content_bytes)

    if HAS_SELECTOLAX:
        tree = HTMLParser(html_str)
        # Strip boilerplate tags
        for tag in tree.css("script, style, nav, footer, header, aside, noscript, iframe, svg, form"):
            tag.decompose()

        # Find main content container if available
        main_node = tree.css_first("main") or tree.css_first("article") or tree.css_first("[role='main']") or tree.body
        if main_node:
            text = main_node.text(separator="\n", strip=True)
        else:
            text = tree.text(separator="\n", strip=True)
        return text
    else:
        # Fallback to BeautifulSoup
        soup = BeautifulSoup(html_str, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "svg", "form"]):
            tag.decompose()
        main_tag = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"}) or soup.body
        if main_tag:
            return main_tag.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)

def extract_from_pdf(content_bytes: bytes, max_pages: int = 30) -> Tuple_Text_Scanned:
    stream = io.BytesIO(content_bytes)
    try:
        reader = pypdf.PdfReader(stream)
        num_pages = min(len(reader.pages), max_pages)
        pages_text = []
        for i in range(num_pages):
            p_text = reader.pages[i].extract_text() or ""
            if p_text:
                pages_text.append(p_text)

        full_text = "\n\n".join(pages_text).strip()
        is_scanned = len(full_text) < 50
        return full_text, is_scanned
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return "", True

# Helper type
Tuple_Text_Scanned = tuple[str, bool]

def process_document(
    content_bytes: bytes,
    content_type: str = "text/html",
    url: str = ""
) -> ExtractedDocument:
    is_pdf = "pdf" in content_type.lower() or url.lower().endswith(".pdf")
    is_scanned = False

    if is_pdf:
        raw_text, is_scanned = extract_from_pdf(content_bytes)
    else:
        raw_text = extract_from_html(content_bytes)

    clean_text = normalize_text(raw_text)
    sha256_hash = calculate_sha256(clean_text)
    word_count = len(clean_text.split())

    return ExtractedDocument(
        raw_text=raw_text,
        clean_text=clean_text,
        sha256=sha256_hash,
        is_pdf=is_pdf,
        is_scanned_pdf=is_scanned,
        word_count=word_count
    )
