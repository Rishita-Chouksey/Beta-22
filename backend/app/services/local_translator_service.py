"""
Offline, API-free translation for YojnaSarthi (English <-> Hindi <-> Bengali).

How it works (nothing leaves the server, no keys, no per-request cost):

1. Curated glossary  - official scheme names / document names from data/glossary.json
                       are swapped in verbatim, never machine translated.
2. Protected spans   - URLs, e-mails, amounts (₹6,000), numbers and ACRONYMS
                       (PM-KISAN, DBT, NPCI ...) are shielded from the MT model.
3. Offline MT        - Argos Translate (CTranslate2) models run locally. Hindi <-> Bengali
                       is pivoted through English automatically.
4. In-memory cache   - repeated strings cost nothing. Nothing is written to disk, so
                       citizen free-text is never persisted (privacy-first, zero PII).

The MT engine sits behind a tiny interface (`TranslationBackend`), so another offline
model (e.g. IndicTrans2 for Marathi) can be plugged in without touching callers.
"""
from __future__ import annotations

import json
import logging
import re
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple

logger = logging.getLogger("local_translator")

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
}

# Unicode blocks used for offline script-based language detection.
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_BENGALI = re.compile(r"[ঀ-৿]")

# Spans that must pass through translation untouched.
_PROTECT_PATTERNS = [
    re.compile(r"https?://[^\s)]+|www\.[^\s)]+"),                       # URLs
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),                            # e-mails
    re.compile(r"\b[\w-]+\.(?:gov|nic|uidai|org)\.in\b[\w/.-]*"),       # bare portals
    re.compile(r"₹\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:lakh|lakhs|crore|crores))?", re.I),
    re.compile(r"\b\d[\d,]*(?:\.\d+)?\s?%"),                            # percentages
    re.compile(r"\b[A-Z][A-Z0-9]*(?:[-/][A-Z0-9]+)+\b"),                # PM-KISAN, PMAY-G
    re.compile(r"\b[A-Z]{2,}\b"),                                       # DBT, NPCI, UIDAI
    re.compile(r"\b\d[\d,]*(?:\.\d+)?\b"),                              # plain numbers
]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?।])\s+")


# --------------------------------------------------------------------------- #
# MT backend interface + Argos implementation
# --------------------------------------------------------------------------- #
class TranslationBackend(Protocol):
    name: str

    def supports(self, source: str, target: str) -> bool: ...
    def translate(self, text: str, source: str, target: str) -> str: ...


class ArgosBackend:
    """Offline neural MT via Argos Translate. Models are installed once with
    `python -m scripts.install_translation_models` and then run fully offline."""

    name = "argos"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._translate_mod = None
        self._import_error: Optional[str] = None
        try:
            import argostranslate.translate as _t  # type: ignore

            self._translate_mod = _t
        except Exception as exc:  # package missing or broken
            self._import_error = f"{type(exc).__name__}: {exc}"

    @property
    def import_error(self) -> Optional[str]:
        return self._import_error

    def installed_pairs(self) -> List[Tuple[str, str]]:
        """Directly installed model pairs (not counting pivoting)."""
        if not self._translate_mod:
            return []
        try:
            langs = self._translate_mod.get_installed_languages()
            pairs = []
            for src in langs:
                for tgt in langs:
                    if src.code != tgt.code and src.get_translation(tgt) is not None:
                        pairs.append((src.code, tgt.code))
            return pairs
        except Exception:
            return []

    def supports(self, source: str, target: str) -> bool:
        if not self._translate_mod:
            return False
        try:
            return self._translate_mod.get_translation_from_codes(source, target) is not None
        except Exception:
            return False

    def translate(self, text: str, source: str, target: str) -> str:
        assert self._translate_mod is not None
        with self._lock:  # CTranslate2 translators are not guaranteed thread-safe
            return self._translate_mod.translate(text, source, target)


# --------------------------------------------------------------------------- #
# Glossary
# --------------------------------------------------------------------------- #
def _find_glossary_path() -> Optional[Path]:
    here = Path(__file__).resolve()
    for cand in (
        here.parents[3] / "data" / "glossary.json",
        here.parents[2] / "data" / "glossary.json",
    ):
        if cand.exists():
            return cand
    return None


class Glossary:
    """term (any language form) -> {lang: curated translation}."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.entries: List[Dict[str, str]] = []
        path = path or _find_glossary_path()
        if path:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for key, forms in data.get("protected_terms", {}).items():
                    entry = {k: v for k, v in forms.items() if k in SUPPORTED_LANGUAGES and v}
                    entry.setdefault("en", key)
                    entry["_aliases"] = key  # the glossary key is also an English surface form
                    self.entries.append(entry)
                for forms in data.get("states", {}).values():
                    entry = {k: v for k, v in forms.items() if k in SUPPORTED_LANGUAGES and v}
                    if "en" in entry:
                        self.entries.append(entry)
            except Exception as exc:
                logger.warning("Could not load glossary: %s", exc)
        # Longest surface forms first so "Aadhaar Card" wins over "Aadhaar".
        self._compiled: Dict[str, List[Tuple[re.Pattern, Dict[str, str]]]] = {}
        for lang in SUPPORTED_LANGUAGES:
            items: List[Tuple[str, Dict[str, str]]] = []
            for entry in self.entries:
                for form in {entry.get(lang), *entry.get("_aliases", "").split("|")} if lang == "en" else {entry.get(lang)}:
                    if form:
                        items.append((form, entry))
            items.sort(key=lambda it: len(it[0]), reverse=True)
            self._compiled[lang] = [
                (re.compile(r"(?<!\w)" + re.escape(form) + r"(?!\w)", re.I if lang == "en" else 0), entry)
                for form, entry in items
            ]

    def patterns_for(self, source: str):
        return self._compiled.get(source, [])


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #
class LocalTranslatorService:
    def __init__(self, backend: Optional[TranslationBackend] = None,
                 glossary: Optional[Glossary] = None, cache_size: int = 5000) -> None:
        self.backend: TranslationBackend = backend if backend is not None else ArgosBackend()
        self.glossary = glossary if glossary is not None else Glossary()
        self._cache: "OrderedDict[Tuple[str, str, str], str]" = OrderedDict()
        self._cache_size = cache_size
        self._cache_lock = threading.Lock()

    # ----- status ---------------------------------------------------------- #
    def pair_available(self, source: str, target: str) -> bool:
        return source == target or self.backend.supports(source, target)

    def get_status(self) -> Dict[str, Any]:
        langs = list(SUPPORTED_LANGUAGES)
        pairs = {
            f"{s}->{t}": self.backend.supports(s, t)
            for s in langs for t in langs if s != t
        }
        ready = any(pairs.values())
        status: Dict[str, Any] = {
            "name": "Offline translator (local, no external API)",
            "engine": getattr(self.backend, "name", "custom"),
            "is_external_api": False,
            "status": "active" if ready else "models_not_installed",
            "pairs": pairs,
            "supported_languages": [{"code": c, "name": n} for c, n in SUPPORTED_LANGUAGES.items()],
            "glossary_terms": len(self.glossary.entries),
            "cache_entries": len(self._cache),
            "message": (
                "Offline machine translation ready."
                if ready else
                "Offline translation models not installed. Run: python -m scripts.install_translation_models"
            ),
        }
        err = getattr(self.backend, "import_error", None)
        if err:
            status["engine_error"] = err
        return status

    # ----- language detection --------------------------------------------- #
    @staticmethod
    def detect_language(text: str) -> str:
        if _BENGALI.search(text):
            return "bn"
        if _DEVANAGARI.search(text):
            return "hi"
        return "en"

    # ----- cache ----------------------------------------------------------- #
    def _cache_get(self, key):
        with self._cache_lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
        return None

    def _cache_put(self, key, value):
        with self._cache_lock:
            self._cache[key] = value
            self._cache.move_to_end(key)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)

    # ----- protection ------------------------------------------------------ #
    def _shield(self, text: str, source: str, target: str):
        """Replace glossary terms and protected spans with opaque tokens.
        Returns (shielded_text, {token: final_replacement})."""
        replacements: Dict[str, str] = {}
        counter = [0]

        def make_token(final: str) -> str:
            tok = f"ZQ{counter[0]}X"
            counter[0] += 1
            replacements[tok] = final
            return tok

        # 1. curated glossary (translated forms)
        for pattern, entry in self.glossary.patterns_for(source):
            target_form = entry.get(target)
            if not target_form:
                continue
            text = pattern.sub(lambda m, tf=target_form: make_token(tf), text)

        # 2. protected spans (kept verbatim)
        for pattern in _PROTECT_PATTERNS:
            def _sub(m):
                span = m.group(0)
                if re.fullmatch(r"ZQ\d+X", span):
                    return span
                return make_token(span)
            text = pattern.sub(_sub, text)
        return text, replacements

    @staticmethod
    def _unshield(text: str, replacements: Dict[str, str]) -> Optional[str]:
        """Restore tokens. Returns None if the MT engine dropped/mangled any token."""
        for tok in replacements:
            if tok not in text:
                # tolerate whitespace inserted inside the token
                loose = re.compile(r"\s*".join(re.escape(c) for c in tok))
                if not loose.search(text):
                    return None
        for tok, final in replacements.items():
            loose = re.compile(r"\s*".join(re.escape(c) for c in tok))
            text = loose.sub(lambda _m, f=final: f, text, count=1)
        return text

    # ----- core ------------------------------------------------------------ #
    def _translate_sentence(self, sentence: str, source: str, target: str) -> str:
        if not sentence.strip():
            return sentence
        shielded, repl = self._shield(sentence, source, target)

        # Entire sentence is just protected content -> nothing for MT to do.
        if not re.sub(r"ZQ\d+X|[\s\W_]", "", shielded):
            restored = self._unshield(shielded, repl)
            return restored if restored is not None else sentence

        out = self.backend.translate(shielded, source, target)
        restored = self._unshield(out, repl)
        if restored is not None:
            return restored

        # MT mangled a token: retry with no protection, then re-apply glossary-free output.
        logger.debug("token loss in MT output; retrying unshielded")
        return self.backend.translate(sentence, source, target)

    def translate(self, text: str, source: str = "auto", target: str = "hi") -> Dict[str, Any]:
        source = (source or "auto").lower()
        target = (target or "hi").lower()
        clean = text.strip() if text else ""

        def result(translated, src, ok=True, error=None, cached=False):
            return {
                "translated_text": translated,
                "source_language": src,
                "target_language": target,
                "cached": cached,
                "service": "local_offline_mt",
                "success": ok,
                "error": error,
            }

        if not clean:
            return result("", source if source != "auto" else "en")
        if target not in SUPPORTED_LANGUAGES:
            return result(clean, source, False,
                          f"Unsupported target language '{target}'. Supported: {list(SUPPORTED_LANGUAGES)}")
        if source == "auto":
            source = self.detect_language(clean)
        if source not in SUPPORTED_LANGUAGES:
            return result(clean, source, False, f"Unsupported source language '{source}'.")
        if source == target:
            return result(clean, source)

        key = (source, target, clean)
        hit = self._cache_get(key)
        if hit is not None:
            return result(hit, source, cached=True)

        if not self.pair_available(source, target):
            return result(clean, source, False,
                          f"Offline model for {source}->{target} is not installed. "
                          "Run: python -m scripts.install_translation_models")
        try:
            parts = _SENTENCE_SPLIT.split(clean)
            translated = " ".join(self._translate_sentence(p, source, target) for p in parts)
        except Exception as exc:  # never break the UI because MT failed
            logger.error("Offline translation failed: %s", type(exc).__name__)
            return result(clean, source, False, f"Offline translation failed: {type(exc).__name__}")

        self._cache_put(key, translated)
        return result(translated, source)

    def translate_batch(self, texts: Sequence[str], source: str = "auto", target: str = "hi") -> List[Dict[str, Any]]:
        return [self.translate(t, source, target) for t in texts]

    # ----- dynamic data localisation -------------------------------------- #
    def localize(self, obj: Any, lang: str) -> Any:
        """Walk arbitrary JSON-like data and fill in any missing `<field>_<lang>` value
        from `<field>_en` (or the other available language). Lets newly published /
        agent-discovered schemes work in every language with no hand-made translation file."""
        if lang not in SUPPORTED_LANGUAGES or lang == "en":
            return obj
        suffix_re = re.compile(r"^(?P<base>.+)_(?P<lang>en|hi|bn)$")

        def fill(node: Any) -> Any:
            if isinstance(node, list):
                return [fill(x) for x in node]
            if not isinstance(node, dict):
                return node
            out = {k: fill(v) for k, v in node.items()}

            # {en:..., hi:..., bn:...} template dicts
            if set(out) & set(SUPPORTED_LANGUAGES) and all(
                isinstance(out.get(k), str) for k in out if k in SUPPORTED_LANGUAGES
            ) and set(out) <= set(SUPPORTED_LANGUAGES):
                if not out.get(lang):
                    src = next((c for c in ("en", "hi", "bn") if out.get(c)), None)
                    if src:
                        res = self.translate(out[src], src, lang)
                        if res["success"]:
                            out[lang] = res["translated_text"]
                return out

            # name_en / name_hi / name_bn style siblings
            bases: Dict[str, Dict[str, str]] = {}
            for k, v in node.items():
                m = suffix_re.match(k)
                if m and isinstance(v, str):
                    bases.setdefault(m["base"], {})[m["lang"]] = v
            for base, forms in bases.items():
                if forms.get(lang):
                    continue
                src = "en" if forms.get("en") else next((c for c in ("hi", "bn") if forms.get(c)), None)
                if not src:
                    continue
                res = self.translate(forms[src], src, lang)
                if res["success"]:
                    out[f"{base}_{lang}"] = res["translated_text"]
            return out

        return fill(obj)


local_translator = LocalTranslatorService()
