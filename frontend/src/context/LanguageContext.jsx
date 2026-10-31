import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import enTranslations from '../translations/en.json';
import hiTranslations from '../translations/hi.json';
import bnTranslations from '../translations/bn.json';
import { translateBatch, fetchTranslatorStatus } from '../services/api';

const LanguageContext = createContext();

/**
 * UI chrome strings: en.json is the single source of truth. hi.json / bn.json are optional
 * hand-curated overrides - any key (or any brand-new string) missing there is translated
 * on the fly by the backend's offline translator, so adding a language string never needs
 * a new static file.
 */
const curated = { en: enTranslations, hi: hiTranslations, bn: bnTranslations };

export const SUPPORTED_LANGUAGES = [
  { code: 'hi', label: 'हिन्दी', nativeName: 'हिन्दी' },
  { code: 'en', label: 'English', nativeName: 'English' },
  { code: 'bn', label: 'বাংলা', nativeName: 'বাংলা' },
];

const FLUSH_DELAY_MS = 40;
const MAX_BATCH = 100; // backend accepts 200

const isBlank = (v) => v === undefined || v === null || (typeof v === 'string' && v.trim() === '');

export function LanguageProvider({ children }) {
  // Default to Hindi as primary civic language
  const [language, setLanguage] = useState('hi');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translatorStatus, setTranslatorStatus] = useState(null);
  const [version, setVersion] = useState(0); // bump to re-render when dynamic translations arrive

  // In-memory only: dynamic text may include citizen input, so it is never persisted.
  const cache = useRef(new Map()); // `${lang}\u0000${text}` -> translated
  const pending = useRef(new Map()); // lang -> Set(text)
  const inflight = useRef(new Set()); // keys being fetched
  const timer = useRef(null);

  useEffect(() => {
    let alive = true;
    fetchTranslatorStatus()
      .then((s) => alive && setTranslatorStatus(s))
      .catch(() => alive && setTranslatorStatus({ status: 'unreachable' }));
    return () => {
      alive = false;
    };
  }, []);

  const flush = useCallback(async () => {
    timer.current = null;
    const jobs = Array.from(pending.current.entries());
    pending.current = new Map();
    for (const [lang, set] of jobs) {
      const texts = Array.from(set);
      for (let i = 0; i < texts.length; i += MAX_BATCH) {
        const chunk = texts.slice(i, i + MAX_BATCH);
        setIsTranslating(true);
        try {
          const results = await translateBatch(chunk, lang, 'auto');
          chunk.forEach((text, idx) => {
            const r = results[idx];
            // On failure keep the original so we never retry in a loop.
            cache.current.set(`${lang}\u0000${text}`, r && r.success && r.translated_text ? r.translated_text : text);
          });
        } catch {
          chunk.forEach((text) => cache.current.set(`${lang}\u0000${text}`, text));
        } finally {
          chunk.forEach((text) => inflight.current.delete(`${lang}\u0000${text}`));
        }
      }
    }
    setIsTranslating(false);
    setVersion((v) => v + 1);
  }, []);

  /** Synchronous lookup. Returns the translation if known, otherwise the original text
   *  now and schedules a batched fetch that re-renders the UI when it lands. */
  const tr = useCallback(
    (text, targetLang = null) => {
      const lang = targetLang || language;
      if (Array.isArray(text)) return text.map((x) => tr(x, targetLang));
      if (isBlank(text) || typeof text !== 'string') return text;
      if (lang === 'en' && !/[ऀ-ॿঀ-৿]/.test(text)) return text;
      const key = `${lang}\u0000${text}`;
      const hit = cache.current.get(key);
      if (hit !== undefined) return hit;
      if (!inflight.current.has(key)) {
        inflight.current.add(key);
        if (!pending.current.has(lang)) pending.current.set(lang, new Set());
        pending.current.get(lang).add(text);
        if (!timer.current) timer.current = setTimeout(flush, FLUSH_DELAY_MS);
      }
      return text;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [language, flush]
  );

  /** UI chrome string by key: curated -> offline MT of the English source -> key. */
  const t = (key) => {
    const own = curated[language]?.[key];
    if (!isBlank(own)) return own;
    const en = enTranslations[key];
    if (isBlank(en)) return key;
    return language === 'en' ? en : tr(en);
  };

  /**
   * Inline literal helper, replacing `language === 'hi' ? 'हिंदी' : 'English'`.
   *   lt(english, hindi, bengali?)  - Bengali (or any other language) is generated offline
   *   from the English text when no hand-written version is supplied.
   */
  const lt = (en, hi, bn) => {
    if (language === 'en') return en;
    if (language === 'hi') return !isBlank(hi) ? hi : tr(en);
    if (language === 'bn' && !isBlank(bn)) return bn;
    return tr(en);
  };

  /**
   * Pick the right language from dynamic backend data.
   *   getBilingualText(obj, 'name')       -> obj.name_<lang>, else offline-translated from name_en/hi
   *   getBilingualText(textEn, textHi)    -> literal pair
   * Arrays (e.g. examples) are handled element-wise. Works for schemes published after
   * build time because nothing is pre-translated.
   */
  const getBilingualText = (arg1, arg2) => {
    if (arg1 && typeof arg1 === 'object' && !Array.isArray(arg1)) {
      const base = arg2;
      const localized = arg1[`${base}_${language}`];
      const present = Array.isArray(localized) ? localized.length > 0 : !isBlank(localized);
      if (present) return localized;
      const source = arg1[`${base}_en`] ?? arg1[`${base}_hi`] ?? arg1[`${base}_bn`];
      if (Array.isArray(source)) return source.map((x) => tr(x));
      return isBlank(source) ? '' : tr(source);
    }
    if (typeof arg1 === 'string' || typeof arg2 === 'string') {
      return lt(arg1 || '', arg2 || '');
    }
    return String(arg1 || arg2 || '');
  };

  /** Async variant for code paths that need the final string (chat, alerts, speech). */
  const translateDynamic = async (text, targetLang = null) => {
    const target = targetLang || language;
    if (isBlank(text) || typeof text !== 'string') return text;
    const key = `${target}\u0000${text}`;
    if (cache.current.has(key)) return cache.current.get(key);
    try {
      setIsTranslating(true);
      const [r] = await translateBatch([text], target, 'auto');
      const out = r && r.success && r.translated_text ? r.translated_text : text;
      cache.current.set(key, out);
      return out;
    } catch {
      return text;
    } finally {
      setIsTranslating(false);
    }
  };

  const translatorReady = !translatorStatus || translatorStatus.status === 'active';

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t,
      lt,
      tr,
      getBilingualText,
      translateDynamic,
      isTranslating,
      translatorReady,
      supportedLanguages: SUPPORTED_LANGUAGES,
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [language, isTranslating, translatorReady, tr, version]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

/** <Tr>any dynamic text</Tr> - renders it in the active language. */
export function Tr({ children }) {
  const { tr } = useLanguage();
  return <>{typeof children === 'string' ? tr(children) : children}</>;
}
