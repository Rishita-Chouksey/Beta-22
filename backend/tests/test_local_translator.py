"""Tests for the offline translator. A deterministic fake MT backend stands in for Argos so
the protection / glossary / caching / localisation logic is verified without model files."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.local_translator_service import LocalTranslatorService, Glossary
from app.routes import translator as translator_route


class FakeBackend:
    """Pretends to be MT: wraps text as <lang:...>. Keeps ZQnX tokens intact like a good model."""
    name = "fake"

    def __init__(self, pairs=None, drop_tokens=False):
        self.pairs = pairs if pairs is not None else {("en", "hi"), ("en", "bn"), ("hi", "en"), ("bn", "en"), ("hi", "bn"), ("bn", "hi")}
        self.calls = 0
        self.drop_tokens = drop_tokens

    def supports(self, s, t):
        return (s, t) in self.pairs

    def translate(self, text, s, t):
        import re
        self.calls += 1
        if self.drop_tokens and "ZQ" in text:
            text = re.sub(r"ZQ\d+X", "", text)
        return f"<{t}:{text}>"


@pytest.fixture
def svc():
    return LocalTranslatorService(backend=FakeBackend(), glossary=Glossary())


def test_identity_and_empty(svc):
    assert svc.translate("hello", "en", "en")["translated_text"] == "hello"
    assert svc.translate("   ", "en", "hi")["translated_text"] == ""


def test_unsupported_target(svc):
    r = svc.translate("hello", "en", "fr")
    assert r["success"] is False and "Unsupported" in r["error"]


def test_script_detection(svc):
    assert svc.detect_language("योजना") == "hi"
    assert svc.detect_language("প্রকল্প") == "bn"
    assert svc.detect_language("scheme") == "en"
    r = svc.translate("किसान योजना", "auto", "en")
    assert r["source_language"] == "hi" and r["translated_text"].startswith("<en:")


def test_amounts_urls_acronyms_survive(svc):
    r = svc.translate("Get ₹6,000 via DBT, see https://pmkisan.gov.in/apply now.", "en", "hi")
    out = r["translated_text"]
    assert "₹6,000" in out and "DBT" in out and "https://pmkisan.gov.in/apply" in out
    assert "ZQ" not in out


def test_glossary_uses_curated_translation(svc):
    out = svc.translate("Bring your Aadhaar and Khasra.", "en", "hi")["translated_text"]
    assert "आधार कार्ड" in out and "खसरा" in out


def test_token_loss_falls_back_without_leaking_tokens():
    svc = LocalTranslatorService(backend=FakeBackend(drop_tokens=True), glossary=Glossary())
    out = svc.translate("Pay ₹500 today", "en", "hi")["translated_text"]
    assert "ZQ" not in out


def test_cache_prevents_second_mt_call(svc):
    svc.translate("Apply online", "en", "hi")
    n = svc.backend.calls
    r = svc.translate("Apply online", "en", "hi")
    assert r["cached"] is True and svc.backend.calls == n


def test_missing_models_reports_clean_error():
    svc = LocalTranslatorService(backend=FakeBackend(pairs=set()), glossary=Glossary())
    r = svc.translate("hello", "en", "hi")
    assert r["success"] is False and "install_translation_models" in r["error"]
    assert r["translated_text"] == "hello"  # graceful: original text returned
    assert svc.get_status()["status"] == "models_not_installed"


def test_localize_fills_only_missing_fields(svc):
    scheme = {
        "name_en": "New Dynamic Scheme", "name_hi": "नई योजना", "name_bn": "",
        "benefit_en": "Get ₹1,000 monthly", "benefit_hi": "", "benefit_bn": "",
        "why_template": {"en": "Income must be below {value}.", "hi": "", "bn": ""},
        "rules": [{"description_en": "Must be a farmer", "description_hi": "किसान", "description_bn": ""}],
    }
    out = svc.localize(scheme, "bn")
    assert out["name_bn"].startswith("<bn:")
    assert out["name_hi"] == "नई योजना"                      # curated value untouched
    assert out["why_template"]["bn"].startswith("<bn:")
    assert out["rules"][0]["description_bn"].startswith("<bn:")
    assert "₹1,000" in svc.localize(scheme, "hi")["benefit_hi"]


def test_localize_does_not_mutate_input(svc):
    scheme = {"name_en": "X", "name_bn": ""}
    svc.localize(scheme, "bn")
    assert scheme["name_bn"] == ""


# ---- HTTP layer ---------------------------------------------------------------
@pytest.fixture
def client(monkeypatch):
    fake = LocalTranslatorService(backend=FakeBackend(), glossary=Glossary())
    monkeypatch.setattr(translator_route, "local_translator", fake)
    return TestClient(app)


def test_translate_endpoint_and_alias_fields(client):
    r = client.post("/api/translate", json={"text": "Hello", "sourceLanguage": "en", "targetLanguage": "bn"})
    assert r.status_code == 200
    d = r.json()
    assert d["translated_text"] == d["translatedText"] and d["service"] == "local_offline_mt"


def test_translate_endpoint_rejects_bad_language(client):
    r = client.post("/api/translate", json={"text": "Hello", "targetLanguage": "xx"})
    assert r.status_code == 400


def test_batch_endpoint(client):
    r = client.post("/api/translate/batch", json={"texts": ["a", "b", ""], "target_language": "hi", "source_language": "en"})
    assert r.status_code == 200
    items = r.json()["translations"]
    assert len(items) == 3 and items[2]["translated_text"] == ""


def test_batch_limit(client):
    r = client.post("/api/translate/batch", json={"texts": ["x"] * 201, "target_language": "hi"})
    assert r.status_code == 422


def test_status_has_no_external_api(client):
    d = client.get("/api/translate/status").json()
    assert d["is_external_api"] is False and "supported_languages" in d


def test_schemes_lang_param_localizes(monkeypatch):
    from app.routes import schemes as schemes_route
    fake = LocalTranslatorService(backend=FakeBackend(), glossary=Glossary())
    monkeypatch.setattr(schemes_route, "local_translator", fake)
    c = TestClient(app)
    base = c.get("/api/schemes/pm_kisan").json()
    loc = c.get("/api/schemes/pm_kisan?lang=bn").json()
    if not base["name_bn"]:
        assert loc["name_bn"]  # filled on the fly, using the curated glossary form for the scheme name
    else:
        assert loc["name_bn"] == base["name_bn"]  # curated value is never overwritten
    assert loc["name_hi"] == base["name_hi"]
    assert loc["id"] == "pm_kisan"
