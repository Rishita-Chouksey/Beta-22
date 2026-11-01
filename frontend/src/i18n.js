import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './translations/en.json';
import hi from './translations/hi.json';
import mr from './translations/mr.json';
import bn from './translations/bn.json';
import catalog from './translations/catalog.json';

const catalogEn = {};
const catalogHi = {};
const catalogMr = {};
const catalogBn = {};

Object.entries(catalog).forEach(([enText, trs]) => {
  catalogEn[enText] = enText;
  catalogHi[enText] = trs.hi || enText;
  catalogMr[enText] = trs.mr || trs.hi || enText;
  catalogBn[enText] = trs.bn || trs.hi || enText;
});

const resources = {
  en: { translation: { ...en, ...catalogEn } },
  hi: { translation: { ...hi, ...catalogHi } },
  mr: { translation: { ...mr, ...catalogMr } },
  bn: { translation: { ...bn, ...catalogBn } },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'hi', // Default civic language
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false, // React already protects against XSS
    },
  });

export default i18n;
