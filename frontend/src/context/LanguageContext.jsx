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

  const getBilingualText = (obj, fieldBase) => {
    if (!obj) return '';
    const localized = obj[`${fieldBase}_${language}`];
    if (localized) return localized;
    return obj[`${fieldBase}_en`] || obj[`${fieldBase}_hi`] || '';
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
