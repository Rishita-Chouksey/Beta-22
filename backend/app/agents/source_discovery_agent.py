import re
import uuid
import logging
from urllib.parse import urlparse, urljoin
from typing import List, Optional, Set

from bs4 import BeautifulSoup

from .models import SourceItem, SourceType, SourceStatus, AgentStatus
from .repository import AgentRepository
from .http_client import create_agent_http_client, polite_get, robots_permission

logger = logging.getLogger("source_discovery_agent")

# Official government domain patterns allowed for source expansion
GOV_DOMAIN_PATTERNS = [
    r"\.gov\.in$",
    r"\.nic\.in$",
    r"\.mp\.gov\.in$",
    r"samagra\.gov\.in$",
    r"mpedistrict\.gov\.in$",
    r"india\.gov\.in$",
    r"myscheme\.gov\.in$"
]

# Excluded domains / paths (social, trackers, static files)
EXCLUDE_EXTENSIONS = {".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf"}
EXCLUDE_DOMAINS = {"twitter.com", "facebook.com", "youtube.com", "instagram.com", "linkedin.com", "t.me", "wa.me"}

DEFAULT_SEEDS = [
    "https://www.myscheme.gov.in/"
]

class SourceDiscoveryAgent:
    """
    Agent 1: Source Discovery Agent
    Discovers, validates, and tracks official government portals, guidelines, and PDF links.
    """

    def __init__(self, allowed_patterns: Optional[List[str]] = None):
        self.allowed_patterns = allowed_patterns or GOV_DOMAIN_PATTERNS
        self.last_errors: List[Dict[str, str]] = []

    def is_official_gov_domain(self, domain: str) -> bool:
        domain_clean = domain.lower().split(":")[0]  # strip port
        if domain_clean in EXCLUDE_DOMAINS:
            return False
        for pat in self.allowed_patterns:
            if re.search(pat, domain_clean):
                return True
        return False

    def classify_source_type(self, url: str) -> SourceType:
        url_lower = url.lower()
        if url_lower.endswith(".pdf") or ".pdf?" in url_lower:
            return SourceType.PDF
        if url_lower.endswith(("/", ".html", ".htm", ".aspx", ".php", "/cms/")) or "/service" in url_lower:
            return SourceType.HTML
        return SourceType.HTML

    def normalize_url(self, raw_url: str, base_url: str) -> Optional[str]:
        if not raw_url:
            return None
        joined = urljoin(base_url, raw_url.strip())
        parsed = urlparse(joined)
        if parsed.scheme not in ("http", "https"):
            return None
        # Remove fragment
        clean_url = parsed._replace(fragment="").geturl()
        # Check file extension
        path_lower = parsed.path.lower()
        for ext in EXCLUDE_EXTENSIONS:
            if path_lower.endswith(ext):
                return None
        return clean_url

    def discover_sources(self, seed_urls: Optional[List[str]] = None, max_links_per_seed: int = 15) -> List[SourceItem]:
        """
        Discovers official government links from myScheme, filters duplicates,
        persists new sources in the SQLite database, and logs the execution run.
        """
        run_id = f"run-disc-{uuid.uuid4().hex[:8]}"
        seeds = seed_urls or DEFAULT_SEEDS
        AgentRepository.record_run_start(
            run_id,
            "source_discovery",
            f"Discovering from seeds: {', '.join(seeds)} (max {max_links_per_seed} links/seed)"
        )

        discovered_sources: List[SourceItem] = []
        self.last_errors = []
        client = create_agent_http_client(timeout_seconds=20.0)

        try:
            for seed in seeds:
                seed_domain = urlparse(seed).netloc
                # Ensure seed itself is recorded in sources table
                seed_source = AgentRepository.get_source_by_url(seed)
                if not seed_source:
                    seed_item = SourceItem(
                        id=f"src-{uuid.uuid4().hex[:10]}",
                        url=seed,
                        domain=seed_domain,
                        source_type=self.classify_source_type(seed),
                        discovered_from="initial_seed",
                        status=SourceStatus.DISCOVERED,
                        created_at=AgentRepository.now_iso()
                    )
                    AgentRepository.add_or_update_source(seed_item)
                    discovered_sources.append(seed_item)

                logger.info(f"SourceDiscoveryAgent fetching seed: {seed}")
                try:
                    allowed, policy_error = robots_permission(client, seed)
                    if not allowed:
                        self.last_errors.append({"url": seed, "error": policy_error or "Disallowed by robots.txt."})
                        continue
                    resp = polite_get(client, seed)
                    if resp.status_code != 200:
                        error = f"HTTP status code {resp.status_code}"
                        self.last_errors.append({"url": seed, "error": error})
                        logger.warning(f"Seed {seed} returned HTTP {resp.status_code}")
                        continue
                except Exception as net_err:
                    self.last_errors.append({"url": seed, "error": str(net_err)})
                    logger.warning(f"Failed to fetch seed {seed}: {net_err}")
                    continue

                # Parse HTML for links
                soup = BeautifulSoup(resp.text, "html.parser")
                found_links: Set[str] = set()

                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    norm = self.normalize_url(href, seed)
                    if not norm:
                        continue

                    parsed_norm = urlparse(norm)
                    if not self.is_official_gov_domain(parsed_norm.netloc):
                        continue

                    # Filter out obvious logout, feedback, or internal anchor links
                    if any(skip in norm.lower() for skip in ["javascript:", "mailto:", "tel:", "login", "logout"]):
                        continue

                    found_links.add(norm)
                    if len(found_links) >= max_links_per_seed:
                        break

                for link in found_links:
                    existing = AgentRepository.get_source_by_url(link)
                    if not existing:
                        domain = urlparse(link).netloc
                        source_type = self.classify_source_type(link)
                        new_source = SourceItem(
                            id=f"src-{uuid.uuid4().hex[:10]}",
                            url=link,
                            domain=domain,
                            source_type=source_type,
                            discovered_from=seed,
                            status=SourceStatus.DISCOVERED,
                            created_at=AgentRepository.now_iso()
                        )
                        AgentRepository.add_or_update_source(new_source)
                        discovered_sources.append(new_source)

            summary = f"Discovered and indexed {len(discovered_sources)} new sources from {len(seeds)} seeds."
            AgentRepository.record_run_completion(
                run_id,
                AgentStatus.COMPLETED,
                summary
            )
            return discovered_sources

        except Exception as e:
            err_msg = f"Source discovery failed: {str(e)}"
            logger.error(err_msg, exc_info=True)
            AgentRepository.record_run_completion(
                run_id,
                AgentStatus.FAILED,
                "Discovery process encountered an error",
                error_message=err_msg
            )
            return discovered_sources
        finally:
            client.close()
