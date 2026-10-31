import re
import uuid
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from .models import SourceItem, SourceType, SourceStatus, AgentStatus
from .repository import AgentRepository
from .http_client import create_agent_http_client, polite_get, robots_permission

logger = logging.getLogger("crawling_agent")

class CrawlingAgent:
    """
    Agent 2: Crawling Agent
    Fetches approved public government pages and PDFs, strips boilerplate/navigation noise,
    and returns clean textual content.
    """

    def __init__(self, timeout_seconds: float = 25.0):
        self.timeout_seconds = timeout_seconds

    def clean_html_text(self, html_content: str) -> str:
        """
        Extracts clean, readable text from HTML by removing scripts, styles,
        navbars, footers, and collapsing whitespace.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip non-content elements
        for element in soup(["script", "style", "noscript", "header", "footer", "nav", "svg", "iframe"]):
            element.decompose()

        # Try to locate main article / content container if present
        main_content = (
            soup.find("main") or
            soup.find("div", {"id": re.compile(r"content|main|article|body", re.I)}) or
            soup.find("div", {"class": re.compile(r"content|main|article|service-details", re.I)}) or
            soup.body or
            soup
        )

        text = main_content.get_text(separator="\n", strip=True)
        # Collapse multiple empty lines
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(clean_lines)

    def extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """
        Extracts textual content from PDF binary using PyMuPDF (fitz).
        """
        if not fitz:
            raise RuntimeError("PyMuPDF (fitz) is not installed in the python environment.")

        text_parts = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(page_text.strip())

        return "\n\n".join(text_parts)

    def crawl_source(self, source: SourceItem) -> Dict[str, Any]:
        """
        Crawls a single source item. Returns structured crawl dictionary.
        """
        client = create_agent_http_client(timeout_seconds=self.timeout_seconds)
        now = AgentRepository.now_iso()
        target_url = source.url

        try:
            allowed, policy_error = robots_permission(client, target_url)
            if not allowed:
                AgentRepository.update_source_status(
                    source_id=source.id,
                    status=SourceStatus.DEGRADED,
                    last_checked_at=now,
                )
                return {
                    "source_id": source.id,
                    "url": target_url,
                    "document_type": source.source_type.value,
                    "raw_text": "",
                    "status": "failed",
                    "error": policy_error or "Disallowed by robots.txt.",
                }
            resp = polite_get(client, target_url)

            # Follow a simple client-side redirect only after checking target robots policy.
            if resp.status_code == 200 and "window.location.replace(" in resp.text:
                match = re.search(r'window\.location\.replace\(["\']([^"\']+)["\']\)', resp.text)
                if match:
                    redirect_path = match.group(1)
                    target_url = urljoin(target_url, redirect_path)
                    logger.info(f"Following JS redirect to {target_url}")
                    allowed, policy_error = robots_permission(client, target_url)
                    if not allowed:
                        AgentRepository.update_source_status(
                            source_id=source.id,
                            status=SourceStatus.DEGRADED,
                            last_checked_at=now,
                        )
                        return {
                            "source_id": source.id,
                            "url": target_url,
                            "document_type": source.source_type.value,
                            "raw_text": "",
                            "status": "failed",
                            "error": policy_error or "Redirect target disallowed by robots.txt.",
                        }
                    resp = polite_get(client, target_url)

            if resp.status_code != 200:
                AgentRepository.update_source_status(
                    source_id=source.id,
                    status=SourceStatus.FAILED,
                    last_checked_at=now
                )
                return {
                    "source_id": source.id,
                    "url": target_url,
                    "document_type": source.source_type.value,
                    "raw_text": "",
                    "status": "failed",
                    "error": f"HTTP status code {resp.status_code}"
                }

            content_type = resp.headers.get("content-type", "").lower()
            is_pdf = "application/pdf" in content_type or target_url.lower().endswith(".pdf")

            if is_pdf:
                raw_text = self.extract_pdf_text(resp.content)
                doc_type = "PDF"
            else:
                raw_text = self.clean_html_text(resp.text)
                doc_type = "HTML"

            # Update source in DB with successful crawl
            AgentRepository.update_source_status(
                source_id=source.id,
                status=SourceStatus.CRAWLED,
                last_checked_at=now,
                last_successful_fetch_at=now
            )

            return {
                "source_id": source.id,
                "url": target_url,
                "document_type": doc_type,
                "raw_text": raw_text,
                "status": "success",
                "error": None
            }

        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Error crawling {target_url}: {err_msg}")
            AgentRepository.update_source_status(
                source_id=source.id,
                status=SourceStatus.FAILED,
                last_checked_at=now
            )
            return {
                "source_id": source.id,
                "url": target_url,
                "document_type": source.source_type.value,
                "raw_text": "",
                "status": "failed",
                "error": err_msg
            }
        finally:
            client.close()

    def crawl_sources(self, sources: List[SourceItem]) -> List[Dict[str, Any]]:
        """
        Crawls a list of sources, records agent execution run, and returns all results.
        """
        run_id = f"run-crawl-{uuid.uuid4().hex[:8]}"
        AgentRepository.record_run_start(
            run_id,
            "crawling",
            f"Crawling {len(sources)} sources"
        )

        results = []
        success_count = 0
        failed_count = 0

        for src in sources:
            res = self.crawl_source(src)
            results.append(res)
            if res["status"] == "success":
                success_count += 1
            else:
                failed_count += 1

        summary = f"Crawled {len(sources)} sources: {success_count} succeeded, {failed_count} failed."
        status = AgentStatus.COMPLETED if failed_count == 0 or success_count > 0 else AgentStatus.FAILED
        AgentRepository.record_run_completion(run_id, status, summary)
        return results
