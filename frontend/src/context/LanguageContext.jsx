import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import i18n from '../i18n';
import enTranslations from '../translations/en.json';
import hiTranslations from '../translations/hi.json';
import mrTranslations from '../translations/mr.json';
import bnTranslations from '../translations/bn.json';
import catalog from '../translations/catalog.json';

const LanguageContext = createContext();

export const SUPPORTED_LANGUAGES = [
  { code: 'hi', label: 'हिन्दी', nativeName: 'हिन्दी' },
  { code: 'en', label: 'English', nativeName: 'English' },
  { code: 'mr', label: 'मराठी', nativeName: 'मराठी' },
  { code: 'bn', label: 'বাংলা', nativeName: 'বাংলা' },
];

const dictionaries = {
  hi: hiTranslations,
  en: enTranslations,
  mr: mrTranslations,
  bn: bnTranslations,
};

const cleanKey = (s) => (typeof s === 'string' ? s.trim().toLowerCase().replace(/[\s•\-\.\,]+/g, ' ') : '');
const isBlank = (v) => v === undefined || v === null || (typeof v === 'string' && v.trim() === '');

// Build ultra-fast bidirectional indexed memory lookup map for all translations
const textIndex = new Map();

const registerEntry = (enText, hiText, mrText, bnText) => {
  const item = { en: enText, hi: hiText, mr: mrText, bn: bnText };
  if (enText && typeof enText === 'string') {
    textIndex.set(enText, item);
    textIndex.set(cleanKey(enText), item);
  }
  if (hiText && typeof hiText === 'string') {
    textIndex.set(hiText, item);
    textIndex.set(cleanKey(hiText), item);
  }
  if (mrText && typeof mrText === 'string') {
    textIndex.set(mrText, item);
    textIndex.set(cleanKey(mrText), item);
  }
  if (bnText && typeof bnText === 'string') {
    textIndex.set(bnText, item);
    textIndex.set(cleanKey(bnText), item);
  }
};

// 1. Index full catalog
Object.entries(catalog).forEach(([enStr, trs]) => {
  registerEntry(enStr, trs.hi, trs.mr, trs.bn);
});

// 2. Index core 95 UI dictionary strings
Object.keys(enTranslations).forEach((key) => {
  registerEntry(enTranslations[key], hiTranslations[key], mrTranslations[key], bnTranslations[key]);
});

/**
 * Universal lookup helper for any string into target language.
 */
const lookup = (text, targetLang) => {
  if (isBlank(text) || typeof text !== 'string') return null;
  const direct = textIndex.get(text) || textIndex.get(cleanKey(text));
  if (direct && !isBlank(direct[targetLang])) {
    return direct[targetLang];
  }
  // Check core dictionaries by key
  if (dictionaries[targetLang]?.[text]) {
    return dictionaries[targetLang][text];
  }
  return null;
};

export function LanguageProvider({ children }) {
  // Default to Hindi as primary civic language
  const [language, setLanguageState] = useState(i18n.language || 'hi');

  const setLanguage = (lang) => {
    if (!dictionaries[lang]) return;
    setLanguageState(lang);
    i18n.changeLanguage(lang);
  };

  useEffect(() => {
    if (i18n.language !== language) {
      i18n.changeLanguage(language);
    }
  }, [language]);

  /** UI chrome string by key using local i18n library */
  const t = (key, options = {}) => {
    if (!key) return '';
    // Primary: i18next translation
    if (i18n.exists(key)) {
      return i18n.t(key, options);
    }
    const hit = lookup(key, language);
    if (!isBlank(hit)) return hit;
    // Fallback: direct dictionary lookup
    const direct = dictionaries[language]?.[key] || dictionaries.hi?.[key] || dictionaries.en?.[key];
    if (direct) return direct;
    return key;
  };

  /**
   * Inline literal helper:
   * lt(en, hi, mr, bn) or lt(en, hi, bn) or lt(en, hi)
   * Resolves instantly with accurate language text (never falls back to Hindi for Marathi or Bengali).
   */
  const lt = (en, hi, arg3, arg4) => {
    if (language === 'en') return en || '';
    if (language === 'hi') return !isBlank(hi) ? hi : (en || '');

    let mrArg = null;
    let bnArg = null;
    if (arg4 !== undefined) {
      mrArg = arg3;
      bnArg = arg4;
    } else if (arg3 !== undefined) {
      bnArg = arg3;
    }

    if (language === 'mr') {
      if (!isBlank(mrArg)) return mrArg;
      const hit = lookup(en, 'mr') || lookup(hi, 'mr');
      if (!isBlank(hit)) return hit;
      return en || hi || '';
    }

    if (language === 'bn') {
      if (!isBlank(bnArg)) return bnArg;
      const hit = lookup(en, 'bn') || lookup(hi, 'bn');
      if (!isBlank(hit)) return hit;
      return en || hi || '';
    }

    return en || '';
  };

  /**
   * Pick the right language from dynamic backend data.
   * e.g., getBilingualText(scheme, 'name')
   * or getBilingualText(name_en, name_hi)
   * or getBilingualText(['Wheat', 'Rice'])
   */
  const getBilingualText = (arg1, arg2) => {
    // Array of objects or strings
    if (Array.isArray(arg1)) {
      return arg1.map((item) =>
        typeof item === 'string'
          ? (lookup(item, language) || item)
          : getBilingualText(item, arg2)
      );
    }

    if (arg1 && typeof arg1 === 'object') {
      const base = arg2;
      // 1. Direct language field: e.g. name_mr, benefit_mr, title_mr, label_mr, name_bn
      const localized = arg1[`${base}_${language}`];
      if (Array.isArray(localized) ? localized.length > 0 : !isBlank(localized)) {
        return localized;
      }

      const enVal = arg1[`${base}_en`];
      const hiVal = arg1[`${base}_hi`];

      // Array values (like examples, rules, procedures)
      if (Array.isArray(enVal) || Array.isArray(hiVal)) {
        const srcArray = Array.isArray(enVal) && enVal.length > 0 ? enVal : (Array.isArray(hiVal) ? hiVal : []);
        return srcArray.map((item) => (typeof item === 'string' ? (lookup(item, language) || item) : item));
      }

      // 2. Language is Marathi ('mr')
      if (language === 'mr') {
        const hit = (enVal && lookup(enVal, 'mr')) || (hiVal && lookup(hiVal, 'mr'));
        if (!isBlank(hit)) return hit;
        return enVal || hiVal || arg1[base] || '';
      }

      // 3. Language is Bengali ('bn')
      if (language === 'bn') {
        const hit = (enVal && lookup(enVal, 'bn')) || (hiVal && lookup(hiVal, 'bn'));
        if (!isBlank(hit)) return hit;
        return enVal || hiVal || arg1[base] || '';
      }

      // 4. Language is Hindi ('hi')
      if (language === 'hi') {
        if (!isBlank(hiVal)) return hiVal;
        return enVal || arg1[base] || '';
      }

      // 5. English ('en')
      if (!isBlank(enVal)) return enVal;
      return hiVal || arg1[base] || '';
    }

    // If called as getBilingualText(text_en, text_hi)
    if (typeof arg1 === 'string' || typeof arg2 === 'string') {
      const en = arg1 || '';
      const hi = arg2 || '';
      if (language === 'en') return en || hi;
      if (language === 'hi') return hi || en;
      if (language === 'mr') {
        const hit = lookup(en, 'mr') || lookup(hi, 'mr');
        return !isBlank(hit) ? hit : (en || hi);
      }
      if (language === 'bn') {
        const hit = lookup(en, 'bn') || lookup(hi, 'bn');
        return !isBlank(hit) ? hit : (en || hi);
      }
      return en || hi;
    }

    return String(arg1 || arg2 || '');
  };

  /** Synchronous translation helper using local i18n dictionary */
  const tr = (text, targetLang = null) => {
    if (!text || typeof text !== 'string') return text;
    const lang = targetLang || language;
    const hit = lookup(text, lang);
    return !isBlank(hit) ? hit : text;
  };

  /** Async dynamic translation using local i18n (zero external network calls) */
  const translateDynamic = async (text, targetLang = null) => {
    return tr(text, targetLang);
  };

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t,
      lt,
      tr,
      getBilingualText,
      translateDynamic,
      isTranslating: false,
      translatorReady: true,
      supportedLanguages: SUPPORTED_LANGUAGES,
    }),
    [language]
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
