import pytest
from unittest.mock import patch, MagicMock
from updater.fetch import (
    PoliteFetcher,
    SSRFBlockedException,
    PageTooLargeException,
    FetchResult
)
from updater.registry import AllowedDomainsConfig

def test_ssrf_validation_rejects_private_and_loopback_ips():
    fetcher = PoliteFetcher()

    # Test loopback IP resolution
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 443))]):
        with pytest.raises(SSRFBlockedException):
            fetcher.validate_ssrf("internal.gov.in")

    # Test RFC 1918 private IP resolution
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("10.0.0.5", 443))]):
        with pytest.raises(SSRFBlockedException):
            fetcher.validate_ssrf("admin.nic.in")

    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("192.168.1.100", 443))]):
        with pytest.raises(SSRFBlockedException):
            fetcher.validate_ssrf("portal.gov.in")

    # Test cloud metadata link-local IP resolution
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("169.254.169.254", 443))]):
        with pytest.raises(SSRFBlockedException):
            fetcher.validate_ssrf("metadata.nic.in")

    # Test valid public IP
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("164.100.12.34", 443))]):
        # Should not raise
        fetcher.validate_ssrf("pmkisan.gov.in")

def test_fetch_rejects_denied_domains_and_ssrf():
    fetcher = PoliteFetcher()

    # myscheme denylist check
    res = fetcher.fetch("https://myscheme.gov.in/schemes/pm-kisan")
    assert "Domain policy violation" in res.error
    assert "denylist" in res.error

    # non-allowed domain check
    res_bad = fetcher.fetch("https://unauthorized-domain.com/details")
    assert "Domain policy violation" in res_bad.error

def test_fetch_handles_304_not_modified():
    fetcher = PoliteFetcher()

    with patch.object(fetcher, "validate_ssrf"):
        with patch.object(fetcher, "check_robots_txt", return_value=True):
            with patch("httpx.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_resp = MagicMock()
                mock_resp.status_code = 304
                mock_resp.headers = {"etag": '"etag-12345"'}
                mock_client.get.return_value = mock_resp
                mock_client.__enter__.return_value = mock_client
                mock_client_cls.return_value = mock_client

                res = fetcher.fetch(
                    "https://pmkisan.gov.in/",
                    etag='"etag-12345"',
                    check_robots=False
                )
                assert res.status_code == 304
                assert res.not_modified is True
                assert res.etag == '"etag-12345"'

def test_fetch_enforces_size_cap():
    fetcher = PoliteFetcher(max_bytes=1000) # Small 1KB limit for test

    with patch.object(fetcher, "validate_ssrf"):
        with patch.object(fetcher, "check_robots_txt", return_value=True):
            with patch("httpx.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                # Stream 5000 bytes, exceeding 1000 bytes limit
                mock_resp.iter_bytes.return_value = [b"A" * 500, b"B" * 600]
                mock_resp.headers = {"content-type": "text/html"}
                mock_client.get.return_value = mock_resp
                mock_client.__enter__.return_value = mock_client
                mock_client_cls.return_value = mock_client

                res = fetcher.fetch("https://pmkisan.gov.in/", check_robots=False)
                assert res.error is not None
                assert "exceeded" in res.error
