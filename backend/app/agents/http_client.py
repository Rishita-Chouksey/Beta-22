import httpx
import logging
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger("agent_http_client")
_robots_cache = {}
_last_domain_request = {}
POLITE_DOMAIN_DELAY_SECONDS = 1.0
ROBOTS_CACHE_SECONDS = 6 * 60 * 60

def create_agent_http_client(timeout_seconds: float = 25.0) -> httpx.Client:
    """
    Creates a polite HTTPX client with normal certificate verification enabled.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 YojnaSarthi/2.0"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Connection": "keep-alive"
    }
    return httpx.Client(
        headers=headers,
        verify=True,
        follow_redirects=True,
        timeout=httpx.Timeout(timeout_seconds, connect=15.0)
    )


def polite_get(client: httpx.Client, url: str) -> httpx.Response:
    """Serialize requests to each host with a conservative one-second gap."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    elapsed = time.monotonic() - _last_domain_request.get(domain, 0.0)
    if elapsed < POLITE_DOMAIN_DELAY_SECONDS:
        time.sleep(POLITE_DOMAIN_DELAY_SECONDS - elapsed)
    response = client.get(url)
    _last_domain_request[domain] = time.monotonic()
    return response


def robots_permission(client: httpx.Client, url: str) -> tuple[bool, str | None]:
    """Check robots.txt before fetching a page; fail closed if policy is unknown."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    cache_entry = _robots_cache.get(origin)
    if cache_entry and time.monotonic() - cache_entry[0] < ROBOTS_CACHE_SECONDS:
        parser = cache_entry[1]
        allowed = parser.can_fetch(client.headers.get("User-Agent", "*"), url)
        return allowed, None if allowed else "Disallowed by robots.txt."

    try:
        response = polite_get(client, f"{origin}/robots.txt")
        if response.status_code in (404, 410):
            parser = RobotFileParser()
            parser.parse([])
        elif response.status_code == 200:
            parser = RobotFileParser()
            parser.set_url(f"{origin}/robots.txt")
            parser.parse(response.text.splitlines())
        else:
            return False, f"robots.txt returned HTTP {response.status_code}; access not attempted."
        _robots_cache[origin] = (time.monotonic(), parser)
        allowed = parser.can_fetch(client.headers.get("User-Agent", "*"), url)
        return allowed, None if allowed else "Disallowed by robots.txt."
    except Exception as exc:
        logger.warning("Could not check robots.txt for %s: %s", origin, exc)
        return False, f"robots.txt could not be checked: {exc}"
