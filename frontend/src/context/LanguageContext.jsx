import React, { createContext, useContext, useState } from 'react';
import enTranslations from '../translations/en.json';
import hiTranslations from '../translations/hi.json';

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('hi'); // Default to Hindi as primary civic language

  const translations = language === 'hi' ? hiTranslations : enTranslations;

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
      return arg1[`${fieldBase}_${language === 'hi' ? 'hi' : 'en'}`] || arg1[`${fieldBase}_en`] || arg1[`${fieldBase}_hi`] || '';
    }
    // If called as getBilingualText(text_en, text_hi)
    if (typeof arg1 === 'string' && typeof arg2 === 'string') {
      return language === 'hi' ? arg2 : arg1;
    }
    return String(arg1 || arg2 || '');
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, getBilingualText }}>
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
