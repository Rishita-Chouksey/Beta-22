import React, { createContext, useContext, useState } from 'react';
import enTranslations from '../translations/en.json';
import hiTranslations from '../translations/hi.json';
import bnTranslations from '../translations/bn.json';
import mrTranslations from '../translations/mr.json';
import { translateWithAzure } from '../services/api';

const LanguageContext = createContext();

const translationsMap = {
  hi: hiTranslations,
  en: enTranslations,
  bn: bnTranslations,
  mr: mrTranslations,
};

export const SUPPORTED_LANGUAGES = [
  { code: 'hi', label: 'हिन्दी', nativeName: 'हिन्दी' },
  { code: 'en', label: 'English', nativeName: 'English' },
  { code: 'mr', label: 'मराठी', nativeName: 'मराठी' },
  { code: 'bn', label: 'বাংলা', nativeName: 'বাংলা' },
];

export function LanguageProvider({ children }) {
  // Default to Hindi as primary civic language
  const [language, setLanguage] = useState('hi');
  const [isTranslating, setIsTranslating] = useState(false);

  const translations = translationsMap[language] || enTranslations;

  const t = (key) => {
    return translations[key] || enTranslations[key] || key;
  };

  const getBilingualText = (arg1, arg2) => {
    if (!arg1 && !arg2) return '';
    // If called as getBilingualText(obj, 'fieldName')
    if (typeof arg1 === 'object' && arg1 !== null) {
      const fieldBase = arg2;
      const localized = arg1[`${fieldBase}_${language}`];
      if (localized) return localized;
      // Graceful civic fallbacks: try hi, then en, then whatever exists
      return arg1[`${fieldBase}_hi`] || arg1[`${fieldBase}_en`] || '';
    }
    // If called as getBilingualText(text_en, text_hi)
    if (typeof arg1 === 'string' && typeof arg2 === 'string') {
      if (language === 'hi' || language === 'mr') return arg2 || arg1;
      if (language === 'en') return arg1;
      // Bengali defaults to Hindi if available or English
      return arg2 || arg1;
    }
    return String(arg1 || arg2 || '');
  };

  /**
   * Dynamically translate arbitrary text using Microsoft Azure AI Translator REST API v3.0
   */
  const translateDynamic = async (text, targetLang = null, sourceLang = null) => {
    if (!text || typeof text !== 'string') return text;
    const target = targetLang || language;
    const source = sourceLang || (target === 'en' ? 'hi' : 'en');
    
    if (source === target) return text;

    try {
      setIsTranslating(true);
      const res = await translateWithAzure(text, source, target);
      return res.translated_text || res.translatedText || text;
    } catch (err) {
      console.warn('Azure AI Translator dynamic translation notice:', err.message || err);
      return text;
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        getBilingualText,
        translateDynamic,
        isTranslating,
        supportedLanguages: SUPPORTED_LANGUAGES,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
