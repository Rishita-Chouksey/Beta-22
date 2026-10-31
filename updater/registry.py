import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urlparse
from pydantic import BaseModel, Field, HttpUrl

from .config import ALLOWED_DOMAINS_PATH, SOURCE_REGISTRY_PATH

logger = logging.getLogger("updater.registry")

class AllowedDomainsConfig(BaseModel):
    allow_suffixes: List[str] = Field(default_factory=list)
    deny_hosts: List[str] = Field(default_factory=list)
    require_https: bool = True
    reject_private_ips: bool = True

class SourceEntry(BaseModel):
    scheme_id: str
    name_en: str
    official_source_url: str
    level: str = "central"
    state: Optional[str] = None
    personas: List[str] = Field(default_factory=list)
    category: str = "General"
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    last_sha256: Optional[str] = None
    last_checked_at: Optional[str] = None
    active: bool = True

def load_allowed_domains(path: Path = ALLOWED_DOMAINS_PATH) -> AllowedDomainsConfig:
    if not path.exists():
        logger.warning(f"Allowed domains file not found at {path}, using defaults.")
        return AllowedDomainsConfig(
            allow_suffixes=["gov.in", "nic.in", "india.gov.in", "scholarships.gov.in", "uidai.gov.in"],
            deny_hosts=["myscheme.gov.in", "www.myscheme.gov.in"],
            require_https=True,
            reject_private_ips=True
        )
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AllowedDomainsConfig(**data)

def is_url_allowed(url: str, config: Optional[AllowedDomainsConfig] = None) -> Tuple[bool, Optional[str]]:
    if config is None:
        config = load_allowed_domains()

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL structure: {e}"

    if not parsed.scheme or not parsed.netloc:
        return False, "Missing URL scheme or netloc"

    if config.require_https and parsed.scheme.lower() != "https":
        return False, f"HTTPS is required by policy, got scheme: {parsed.scheme}"

    host = parsed.netloc.split(":")[0].lower()

    # Check denylist first
    for denied in config.deny_hosts:
        if host == denied.lower() or host.endswith("." + denied.lower()):
            return False, f"Host '{host}' is in denylist ({denied})"

    # Check allowlist suffixes
    allowed = False
    for suffix in config.allow_suffixes:
        clean_suffix = suffix.lower().lstrip(".")
        if host == clean_suffix or host.endswith("." + clean_suffix):
            allowed = True
            break

    if not allowed:
        return False, f"Host '{host}' does not match any allowed domain suffix ({config.allow_suffixes})"

    return True, None

def load_source_registry(path: Path = SOURCE_REGISTRY_PATH) -> List[SourceEntry]:
    if not path.exists():
        logger.warning(f"Source registry not found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    raw_sources = data.get("sources", [])
    return [SourceEntry(**s) for s in raw_sources]

def save_source_registry(sources: List[SourceEntry], path: Path = SOURCE_REGISTRY_PATH) -> None:
    data = {
        "version": "1.0",
        "updated_at": None,
        "sources": [s.model_dump() for s in sources]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
