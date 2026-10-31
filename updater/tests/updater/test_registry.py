import pytest
from updater.registry import (
    load_allowed_domains,
    is_url_allowed,
    load_source_registry,
    AllowedDomainsConfig,
    SourceEntry
)

def test_load_allowed_domains():
    config = load_allowed_domains()
    assert "gov.in" in config.allow_suffixes
    assert "myscheme.gov.in" in config.deny_hosts
    assert config.require_https is True
    assert config.reject_private_ips is True

def test_is_url_allowed_positive():
    config = load_allowed_domains()
    allowed, err = is_url_allowed("https://pmkisan.gov.in/", config)
    assert allowed is True
    assert err is None

    allowed2, _ = is_url_allowed("https://scholarships.gov.in/fresh/instructions.html", config)
    assert allowed2 is True

    allowed3, _ = is_url_allowed("https://pmayg.nic.in/netiay/home.aspx", config)
    assert allowed3 is True

def test_is_url_allowed_blocks_myscheme():
    config = load_allowed_domains()
    # myscheme.gov.in is strictly forbidden by project rules
    allowed, err = is_url_allowed("https://myscheme.gov.in/schemes/pm-kisan", config)
    assert allowed is False
    assert "denylist" in err.lower()

    allowed_www, _ = is_url_allowed("https://www.myscheme.gov.in/schemes", config)
    assert allowed_www is False

def test_is_url_allowed_rejects_non_https():
    config = load_allowed_domains()
    allowed, err = is_url_allowed("http://pmkisan.gov.in/", config)
    assert allowed is False
    assert "https is required" in err.lower()

def test_is_url_allowed_rejects_arbitrary_domains():
    config = load_allowed_domains()
    allowed, err = is_url_allowed("https://evil-portal.com/scam", config)
    assert allowed is False
    assert "does not match any allowed domain suffix" in err.lower()

def test_source_registry_seeded_properly():
    sources = load_source_registry()
    assert len(sources) >= 7
    scheme_ids = [s.scheme_id for s in sources]
    assert "pm_kisan" in scheme_ids
    assert "mmvy_scholarship" in scheme_ids
    assert "ladli_behna_mp" in scheme_ids
    assert "ignwps_widow_pension" in scheme_ids

    # Ensure all sources in registry pass allowlist check
    config = load_allowed_domains()
    for s in sources:
        allowed, err = is_url_allowed(s.official_source_url, config)
        assert allowed is True, f"Source URL {s.official_source_url} rejected: {err}"
