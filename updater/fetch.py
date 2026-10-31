import time
import socket
import logging
import ipaddress
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

import httpx

from .config import (
    USER_AGENT,
    PER_DOMAIN_DELAY_SECONDS,
    FETCH_TIMEOUT_SECONDS,
    MAX_PAGE_BYTES
)
from .registry import is_url_allowed, load_allowed_domains, AllowedDomainsConfig

logger = logging.getLogger("updater.fetch")

class SSRFBlockedException(Exception):
    pass

class PageTooLargeException(Exception):
    pass

class DomainNotAllowedException(Exception):
    pass

@dataclass
class FetchResult:
    url: str
    status_code: int = 0
    content_bytes: bytes = b""
    content_type: str = ""
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    not_modified: bool = False
    error: Optional[str] = None

class PoliteFetcher:
    def __init__(
        self,
        allowed_config: Optional[AllowedDomainsConfig] = None,
        delay_seconds: float = PER_DOMAIN_DELAY_SECONDS,
        timeout_seconds: float = FETCH_TIMEOUT_SECONDS,
        max_bytes: int = MAX_PAGE_BYTES,
        user_agent: str = USER_AGENT
    ):
        self.config = allowed_config or load_allowed_domains()
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.user_agent = user_agent
        self._last_request_time: Dict[str, float] = {}
        self._robots_cache: Dict[str, RobotFileParser] = {}

    def validate_ssrf(self, host: str) -> None:
        if not self.config.reject_private_ips:
            return

        try:
            addr_info = socket.getaddrinfo(host, None)
        except socket.gaierror as e:
            raise SSRFBlockedException(f"DNS resolution failed for host {host}: {e}")

        for entry in addr_info:
            ip_str = entry[4][0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if (
                    ip_obj.is_private
                    or ip_obj.is_loopback
                    or ip_obj.is_link_local
                    or ip_obj.is_reserved
                    or ip_obj.is_multicast
                ):
                    raise SSRFBlockedException(
                        f"Host '{host}' resolves to restricted/private IP: {ip_str}"
                    )
            except ValueError:
                continue

    def _wait_for_domain(self, domain: str) -> None:
        last_time = self._last_request_time.get(domain)
        if last_time is not None:
            elapsed = time.time() - last_time
            if elapsed < self.delay_seconds:
                sleep_needed = self.delay_seconds - elapsed
                logger.debug(f"Rate limiting {domain}: sleeping {sleep_needed:.2f}s")
                time.sleep(sleep_needed)
        self._last_request_time[domain] = time.time()

    def check_robots_txt(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.split(":")[0].lower()
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"

        if domain in self._robots_cache:
            return self._robots_cache[domain].can_fetch(self.user_agent, url)

        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            # We fetch robots.txt directly using httpx with short timeout
            self.validate_ssrf(domain)
            with httpx.Client(timeout=5.0, headers={"User-Agent": self.user_agent}) as client:
                res = client.get(robots_url)
                if res.status_code == 200:
                    parser.parse(res.text.splitlines())
                else:
                    # If 404 or not found, crawling is generally permitted
                    parser.allow_all = True
        except Exception as e:
            logger.debug(f"Could not load robots.txt for {domain}: {e}")
            parser.allow_all = True

        self._robots_cache[domain] = parser
        return parser.can_fetch(self.user_agent, url)

    def fetch(
        self,
        url: str,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
        check_robots: bool = True
    ) -> FetchResult:
        # 1. Allowlist check
        allowed, reason = is_url_allowed(url, self.config)
        if not allowed:
            return FetchResult(url=url, error=f"Domain policy violation: {reason}")

        parsed = urlparse(url)
        host = parsed.netloc.split(":")[0].lower()

        # 2. SSRF check
        try:
            self.validate_ssrf(host)
        except SSRFBlockedException as e:
            return FetchResult(url=url, error=f"SSRF blocked: {e}")

        # 3. Robots.txt check
        if check_robots and not self.check_robots_txt(url):
            return FetchResult(url=url, error="Disallowed by robots.txt")

        # 4. Domain rate limiting
        self._wait_for_domain(host)

        # 5. Build headers (Conditional GET)
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8"
        }
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        # 6. Fetch request with redirect inspection and size capping
        current_url = url
        redirect_count = 0
        max_redirects = 5

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=False,
                headers=headers
            ) as client:
                while True:
                    response = client.get(current_url)

                    # Handle 304 Not Modified
                    if response.status_code == 304:
                        return FetchResult(
                            url=current_url,
                            status_code=304,
                            not_modified=True,
                            etag=response.headers.get("etag") or etag,
                            last_modified=response.headers.get("last-modified") or last_modified
                        )

                    # Handle Redirects manually to enforce allowlist & SSRF on every hop
                    if response.status_code in (301, 302, 303, 307, 308):
                        redirect_count += 1
                        if redirect_count > max_redirects:
                            return FetchResult(url=current_url, error="Too many redirects")
                        loc = response.headers.get("location")
                        if not loc:
                            return FetchResult(url=current_url, error="Redirect with missing location header")
                        next_url = urljoin(current_url, loc)

                        # Validate redirect destination
                        allowed_r, reason_r = is_url_allowed(next_url, self.config)
                        if not allowed_r:
                            return FetchResult(
                                url=next_url,
                                error=f"Redirect target violates domain policy: {reason_r}"
                            )
                        next_host = urlparse(next_url).netloc.split(":")[0].lower()
                        self.validate_ssrf(next_host)
                        self._wait_for_domain(next_host)
                        current_url = next_url
                        continue

                    # Read body with size capping
                    content_bytes = bytearray()
                    for chunk in response.iter_bytes(chunk_size=65536):
                        content_bytes.extend(chunk)
                        if len(content_bytes) > self.max_bytes:
                            raise PageTooLargeException(
                                f"Page payload exceeded {self.max_bytes} bytes"
                            )

                    content_type = response.headers.get("content-type", "").lower()
                    new_etag = response.headers.get("etag")
                    new_last_modified = response.headers.get("last-modified")

                    return FetchResult(
                        url=current_url,
                        status_code=response.status_code,
                        content_bytes=bytes(content_bytes),
                        content_type=content_type,
                        etag=new_etag,
                        last_modified=new_last_modified,
                        not_modified=False
                    )

        except PageTooLargeException as e:
            return FetchResult(url=current_url, error=str(e))
        except SSRFBlockedException as e:
            return FetchResult(url=current_url, error=f"SSRF blocked: {e}")
        except httpx.TimeoutException:
            return FetchResult(url=current_url, error=f"Timeout after {self.timeout_seconds}s")
        except Exception as e:
            return FetchResult(url=current_url, error=f"HTTP fetch error: {str(e)}")

default_fetcher = PoliteFetcher()
