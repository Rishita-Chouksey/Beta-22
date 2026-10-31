import asyncio
import time
import logging
import urllib.robotparser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, Tuple
import httpx

from .models import SourceDefinition, SourceType, AccessibilityStatus
from .fingerprint import sanitize_extracted_text, calculate_content_fingerprint

logger = logging.getLogger("scheme_crawler")

CIVIC_USER_AGENT = "YojnaSarthi-SchemeMonitor/1.0 (+https://yojnasarthi.in/civic-bot; contact@yojnasarthi.in)"

# In-memory domain rate limiter and robots.txt cache
_domain_last_request_time: Dict[str, float] = {}
_robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
POLITE_DOMAIN_DELAY_SECONDS = 1.0

class OfficialSchemeCrawler:
    """
    Polite, respectful public web fetcher for Indian official scheme portals.
    Adheres strictly to robots.txt, respects site terms, uses polite delays,
    and isolates failures so one slow or unavailable portal never breaks the system.
    """

    @staticmethod
    async def check_robots_permission(url: str) -> bool:
        """
        Parses and verifies robots.txt for the given official domain.
        Defaults to permitted if robots.txt is missing or unreachable.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain in _robots_cache:
                rp = _robots_cache[domain]
                return rp.can_fetch(CIVIC_USER_AGENT, url)

            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)

            async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
                resp = await client.get(robots_url, headers={"User-Agent": CIVIC_USER_AGENT})
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                    _robots_cache[domain] = rp
                    return rp.can_fetch(CIVIC_USER_AGENT, url)
                else:
                    # No robots.txt or returned 404 -> generally permitted
                    return True
        except Exception as e:
            logger.debug(f"robots.txt check skipped for {url}: {e}")
            return True

    @staticmethod
    async def fetch_source_content(source: SourceDefinition) -> Tuple[Optional[str], Optional[str], AccessibilityStatus, Optional[str]]:
        """
        Fetches the public content from an official government source.
        Returns: (extracted_text, content_hash, accessibility_status, error_details)
        """
        parsed = urlparse(source.official_url)
        domain = parsed.netloc

        # 1. Polite rate limiting per domain
        last_time = _domain_last_request_time.get(domain, 0.0)
        elapsed = time.time() - last_time
        if elapsed < POLITE_DOMAIN_DELAY_SECONDS:
            await asyncio.sleep(POLITE_DOMAIN_DELAY_SECONDS - elapsed)
        _domain_last_request_time[domain] = time.time()

        # 2. Check robots.txt permission
        is_allowed = await OfficialSchemeCrawler.check_robots_permission(source.official_url)
        if not is_allowed:
            return None, None, AccessibilityStatus.DEGRADED, "Automated monitoring disallowed by official portal robots.txt."

        headers = {
            "User-Agent": CIVIC_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,hi;q=0.7",
        }

        # 3. HTTP Request with retries & graceful timeout handling
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # verify=False is used specifically for some Indian state portals with self-signed departmental certificates
                async with httpx.AsyncClient(timeout=12.0, verify=False, follow_redirects=True) as client:
                    resp = await client.get(source.official_url, headers=headers)
                    
                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "").lower()
                        raw_bytes = resp.content

                        # A. PDF Content Handling
                        if "pdf" in content_type or source.source_type == SourceType.PDF or source.official_url.lower().endswith(".pdf"):
                            extracted_text = OfficialSchemeCrawler._extract_pdf_text(raw_bytes)
                            clean_text = sanitize_extracted_text(extracted_text)
                            h = calculate_content_fingerprint(clean_text)
                            return clean_text, h, AccessibilityStatus.HEALTHY, None

                        # B. RSS / Atom Feed Handling
                        elif "xml" in content_type or "rss" in content_type or source.source_type == SourceType.RSS:
                            extracted_text = OfficialSchemeCrawler._extract_rss_text(resp.text)
                            clean_text = sanitize_extracted_text(extracted_text)
                            h = calculate_content_fingerprint(clean_text)
                            return clean_text, h, AccessibilityStatus.HEALTHY, None

                        # C. HTML Webpage Handling
                        else:
                            clean_text = sanitize_extracted_text(resp.text)
                            h = calculate_content_fingerprint(clean_text)
                            return clean_text, h, AccessibilityStatus.HEALTHY, None

                    elif resp.status_code in [403, 401]:
                        return None, None, AccessibilityStatus.DEGRADED, f"HTTP {resp.status_code} Access Restricted by portal firewall."
                    elif resp.status_code in [404, 410]:
                        return None, None, AccessibilityStatus.UNAVAILABLE, f"HTTP {resp.status_code} Official page moved or not found."
                    elif resp.status_code >= 500:
                        if attempt < max_retries:
                            await asyncio.sleep(1.0 * (attempt + 1))
                            continue
                        return None, None, AccessibilityStatus.UNAVAILABLE, f"HTTP {resp.status_code} Government server error."

            except httpx.TimeoutException:
                if attempt < max_retries:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                return None, None, AccessibilityStatus.UNAVAILABLE, "Official portal request timed out (server unreachable)."
            except Exception as e:
                if attempt < max_retries:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                return None, None, AccessibilityStatus.UNAVAILABLE, f"Connection failed: {str(e)[:150]}"

        return None, None, AccessibilityStatus.UNAVAILABLE, "Failed to connect after retries."

    @staticmethod
    def _extract_pdf_text(raw_bytes: bytes) -> str:
        """
        Extracts textual content from PDF bytes using PyMuPDF/pypdf if installed,
        or safe binary text stream parsing as fallback.
        """
        # Try PyMuPDF or pypdf if available in environment
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
            return text
        except ImportError:
            pass

        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        except ImportError:
            pass

        # Fallback: extract readable ASCII / UTF-8 strings from uncompressed PDF streams
        try:
            # Extract printable text blocks between BT and ET operators or literal parentheses
            text_blocks = []
            latin_text = raw_bytes.decode("latin-1", errors="ignore")
            # Look for /Title, /Author, and literal text strings
            import re
            matches = re.findall(r"\(([^\)]{3,100})\)", latin_text)
            for m in matches[:200]:
                if any(c.isalnum() for c in m):
                    text_blocks.append(m)
            return " ".join(text_blocks)
        except Exception:
            return f"PDF Document ({len(raw_bytes)} bytes)"

    @staticmethod
    def _extract_rss_text(xml_string: str) -> str:
        """Extracts titles, descriptions, and publish dates from RSS/Atom feeds."""
        try:
            root = ET.fromstring(xml_string)
            items_text = []
            # RSS channel/item
            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                desc = item.findtext("description", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                items_text.append(f"{title} - {desc} {link} {pub_date}")

            # Atom feed/entry
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
                items_text.append(f"{title} - {summary}")

            return "\n".join(items_text)
        except Exception as e:
            return xml_string[:2000]
