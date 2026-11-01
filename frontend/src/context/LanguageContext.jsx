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

// Common profile attribute labels across all 4 languages
const FIELD_LABELS = {
  residence_type: { hi: 'निवास क्षेत्र', mr: 'निवास प्रकार', bn: 'বাসস্থানের ধরন', en: 'residence type' },
  annual_income: { hi: 'वार्षिक आय', mr: 'वार्षिक उत्पन्न', bn: 'বার্ষিক আয়', en: 'annual income' },
  income_band: { hi: 'आय वर्ग', mr: 'उत्पन्न गट', bn: 'আয় সীমা', en: 'income band' },
  age: { hi: 'आयु', mr: 'वय', bn: 'বয়স', en: 'age' },
  gender: { hi: 'लिंग', mr: 'लिंग', bn: 'লিঙ্গ', en: 'gender' },
  marital_status: { hi: 'वैवाहिक स्थिति', mr: 'वैवाहिक स्थिती', bn: 'বৈবাহিক অবস্থা', en: 'marital status' },
  occupation: { hi: 'व्यवसाय', mr: 'व्यवसाय', bn: 'পেশা', en: 'occupation' },
  landholding_hectares: { hi: 'कृषि भूमि (हेक्टेयर)', mr: 'शेतजमीन (हेक्टर)', bn: 'জমির পরিমাণ (হেক্টর)', en: 'landholding' },
  has_pucca_house: { hi: 'पक्का मकान', mr: 'पक्के घर', bn: 'পাকা বাড়ি', en: 'pucca house' },
  bpl_card_holder: { hi: 'बीपीएल राशन कार्ड', mr: 'दारिद्र्यरेषेखालील (BPL) कार्ड', bn: 'বিপিএল কার্ড', en: 'BPL card' },
  holds_constitutional_post: { hi: 'संवैधानिक पद', mr: 'घटनात्मक पद', bn: 'সাংবিধানিক পদ', en: 'constitutional post' },
  enrolled_higher_education: { hi: 'उच्च शिक्षा में प्रवेश', mr: 'उच्च शिक्षणात प्रवेश', bn: 'উচ্চশিক্ষায় ভর্তি', en: 'higher education' },
  student_class12_marks_percent: { hi: '12वीं कक्षा के अंक %', mr: 'इयत्ता १२वी टक्केवारी', bn: 'দ্বাদশ শ্রেণির প্রাপ্ত নম্বর %', en: 'Class 12 marks %' },
  disability_percent: { hi: 'दिव्यांगता प्रतिशत', mr: 'दिव्यांगत्व टक्केवारी', bn: 'প্রতিবন্ধকতার হার %', en: 'disability percent' },
  social_category: { hi: 'सामाजिक श्रेणी', mr: 'सामाजिक प्रवर्ग', bn: 'সামাজিক শ্রেণী', en: 'social category' },
  state: { hi: 'राज्य', mr: 'राज्य', bn: 'রাজ্য', en: 'state' },
};

const getLocalizedField = (field, targetLang) => {
  if (!field) return '';
  const clean = String(field).replace(/['"`]/g, '').trim();
  const found = FIELD_LABELS[clean];
  if (found && found[targetLang]) return found[targetLang];
  return clean;
};

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

// 2. Index core UI dictionary strings
Object.keys(enTranslations).forEach((key) => {
  registerEntry(enTranslations[key], hiTranslations[key], mrTranslations[key], bnTranslations[key]);
});

/**
 * High-performance rule & condition pattern matcher.
 * Automatically translates dynamic engine evaluation outputs into Marathi or Bengali.
 */
const matchRulePattern = (text, targetLang) => {
  if (isBlank(text) || typeof text !== 'string') return null;
  const str = text.trim();

  // 1. Missing field pattern: Information for 'x' has not been provided yet. / 'x' के लिए जानकारी अभी प्रदान नहीं की गई है।
  let m = str.match(/Information for ['"]?([a-zA-Z0-9_]+)['"]? has not been provided yet/i) ||
          str.match(/['"]?([a-zA-Z0-9_]+)['"]? के लिए जानकारी अभी प्रदान नहीं की गई/i) ||
          str.match(/['"]?([a-zA-Z0-9_]+)['"]? ची माहिती अद्याप दिलेली नाही/i) ||
          str.match(/['"]?([a-zA-Z0-9_]+)['"]?-এর তথ্য এখনও প্রদান করা হয়নি/i);
  if (m) {
    const f = m[1];
    if (targetLang === 'mr') return `'${getLocalizedField(f, 'mr')}' ची माहिती अद्याप दिलेली नाही.`;
    if (targetLang === 'bn') return `'${getLocalizedField(f, 'bn')}'-এর তথ্য এখনও প্রদান করা হয়নি।`;
    if (targetLang === 'hi') return `'${getLocalizedField(f, 'hi')}' के लिए जानकारी अभी प्रदान नहीं की गई है।`;
    if (targetLang === 'en') return `Information for '${getLocalizedField(f, 'en')}' has not been provided yet.`;
  }

  // 2. Unconfirmed field pattern: Value for 'x' is extracted but not yet confirmed / 'x' का मान निकाला गया है लेकिन नागरिक द्वारा पुष्टि नहीं की गई है।
  m = str.match(/Value for ['"]?([a-zA-Z0-9_]+)['"]? is extracted but not yet confirmed/i) ||
      str.match(/['"]?([a-zA-Z0-9_]+)['"]? का मान निकाला गया है लेकिन/i) ||
      str.match(/['"]?([a-zA-Z0-9_]+)['"]? चे मूल्य काढले आहे परंतु/i) ||
      str.match(/['"]?([a-zA-Z0-9_]+)['"]?-এর মান পাওয়া গেছে কিন্তু/i);
  if (m) {
    const f = m[1];
    if (targetLang === 'mr') return `'${getLocalizedField(f, 'mr')}' चे मूल्य प्राप्त झाले आहे परंतु नागरिकाने अद्याप पुष्टी केलेली नाही.`;
    if (targetLang === 'bn') return `'${getLocalizedField(f, 'bn')}'-এর মান পাওয়া গেছে কিন্তু নাগরিক এখনও নিশ্চিত করেননি।`;
    if (targetLang === 'hi') return `'${getLocalizedField(f, 'hi')}' का मान निकाला गया है लेकिन नागरिक द्वारा पुष्टि नहीं की गई है।`;
    if (targetLang === 'en') return `Value for '${getLocalizedField(f, 'en')}' is extracted but not yet confirmed by citizen.`;
  }

  // 3. Satisfies maximum limit
  m = str.match(/Satisfies maximum limit:\s*(.*)/i) ||
      str.match(/अधिकतम सीमा (?:को\s*)?(?:पूरी|पूरा) करता है:\s*(.*)/i) ||
      str.match(/कमाल मर्यादा पूर्ण करते:\s*(.*)/i) ||
      str.match(/সর্বোচ্চ সীমা পূরণ করেছে:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `कमाल मर्यादा पूर्ण करते: ${rest}`;
    if (targetLang === 'bn') return `সর্বোচ্চ সীমা পূরণ করেছে: ${rest}`;
    if (targetLang === 'hi') return `अधिकतम सीमा को पूरा करता है: ${rest}`;
    if (targetLang === 'en') return `Satisfies maximum limit: ${rest}`;
  }

  // 4. Exceeds maximum limit
  m = str.match(/Exceeds maximum permissible limit:\s*(.*)/i) ||
      str.match(/अधिकतम अनुमेय सीमा से अधिक है:\s*(.*)/i) ||
      str.match(/कमाल परवानगी मर्यादेपेक्षा जास्त आहे:\s*(.*)/i) ||
      str.match(/সর্বোচ্চ অনুমোদনযোগ্য সীমার বেশি:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `कमाल परवानगी मर्यादेपेक्षा जास्त आहे: ${rest}`;
    if (targetLang === 'bn') return `সর্বোচ্চ অনুমোদনযোগ্য সীমার বেশি: ${rest}`;
    if (targetLang === 'hi') return `अधिकतम अनुमेय सीमा से अधिक है: ${rest}`;
    if (targetLang === 'en') return `Exceeds maximum permissible limit: ${rest}`;
  }

  // 5. Meets minimum threshold
  m = str.match(/Meets minimum threshold:\s*(.*)/i) ||
      str.match(/न्यूनतम सीमा को पूरा करता है:\s*(.*)/i) ||
      str.match(/किमान मर्यादा पूर्ण करते:\s*(.*)/i) ||
      str.match(/ন্যূনতম প্রয়োজনীয়তা পূরণ করেছে:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `किमान मर्यादा पूर्ण करते: ${rest}`;
    if (targetLang === 'bn') return `ন্যূনতম প্রয়োজনীয়তা পূরণ করেছে: ${rest}`;
    if (targetLang === 'hi') return `न्यूनतम सीमा को पूरा करता है: ${rest}`;
    if (targetLang === 'en') return `Meets minimum threshold: ${rest}`;
  }

  // 6. Below minimum threshold
  m = str.match(/Below minimum required threshold:\s*(.*)/i) ||
      str.match(/आवश्यक न्यूनतम सीमा से कम है:\s*(.*)/i) ||
      str.match(/आवश्यक किमान मर्यादेपेक्षा कमी आहे:\s*(.*)/i) ||
      str.match(/প্রয়োজনীয় ন্যূনতম সীমার নিচে:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `आवश्यक किमान मर्यादेपेक्षा कमी आहे: ${rest}`;
    if (targetLang === 'bn') return `প্রয়োজনীয় ন্যূনতম সীমার নিচে: ${rest}`;
    if (targetLang === 'hi') return `आवश्यक न्यूनतम सीमा से कम है: ${rest}`;
    if (targetLang === 'en') return `Below minimum required threshold: ${rest}`;
  }

  // 7. Matches requirement
  m = str.match(/Matches requirement:\s*(.*)/i) ||
      str.match(/आवश्यकता से मेल खाता है:\s*(.*)/i) ||
      str.match(/आवश्यकतेनुसार जुळते:\s*(.*)/i) ||
      str.match(/প্রয়োজনীয় শর্ত পূরণ হয়েছে:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `आवश्यकतेनुसार जुळते: ${rest}`;
    if (targetLang === 'bn') return `প্রয়োজনীয় শর্ত পূরণ হয়েছে: ${rest}`;
    if (targetLang === 'hi') return `आवश्यकता से मेल खाता है: ${rest}`;
    if (targetLang === 'en') return `Matches requirement: ${rest}`;
  }

  // 8. Does not match requirement
  m = str.match(/Does not match requirement:\s*(.*)/i) ||
      str.match(/आवश्यकता से मेल नहीं खाता:\s*(.*)/i) ||
      str.match(/आवश्यकतेनुसार जुळत नाही:\s*(.*)/i) ||
      str.match(/প্রয়োজনীয় শর্ত পূরণ হয়নি:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `आवश्यकतेनुसार जुळत नाही: ${rest}`;
    if (targetLang === 'bn') return `প্রয়োজনীয় শর্ত পূরণ হয়নি: ${rest}`;
    if (targetLang === 'hi') return `आवश्यकता से मेल नहीं खाता: ${rest}`;
    if (targetLang === 'en') return `Does not match requirement: ${rest}`;
  }

  // 9. Value not in allowed categories
  m = str.match(/Value ['"]?([^'"]+)['"]? is not in allowed categories:\s*(.*)/i) ||
      str.match(/मान ['"]?([^'"]+)['"]? अनुमत श्रेणियों में नहीं है:\s*(.*)/i);
  if (m) {
    const val = m[1];
    const desc = m[2];
    if (targetLang === 'mr') return `मूल्य '${val}' अनुमत श्रेणीत नाही: ${desc}`;
    if (targetLang === 'bn') return `মান '${val}' অনুমোদিত শ্রেণীতে নেই: ${desc}`;
    if (targetLang === 'hi') return `मान '${val}' अनुमत श्रेणियों में नहीं है: ${desc}`;
    if (targetLang === 'en') return `Value '${val}' is not in allowed categories: ${desc}`;
  }

  // 10. State unknown
  m = str.match(/Scheme applies specifically to residents of ([A-Z]+)\. Citizen state is unknown or not provided/i) ||
      str.match(/यह योजना केवल ([A-Z]+|[^क-ह\s]+) के निवासियों के लिए है। नागरिक का राज्य अज्ञात या प्रदान नहीं किया गया/i);
  if (m) {
    const st = m[1];
    if (targetLang === 'mr') return `ही योजना केवळ ${st} च्या रहिवाशांसाठी लागू आहे. नागरिकाचे राज्य अज्ञात आहे किंवा प्रदान केलेले नाही.`;
    if (targetLang === 'bn') return `এই প্রকল্পটি বিশেষভাবে ${st} এর বাসিন্দাদের জন্য প্রযোজ্য। नागरिकের राज्य অজানা বা প্রদান করা হয়নি।`;
    if (targetLang === 'hi') return `यह योजना केवल ${st} के निवासियों के लिए है। नागरिक का राज्य अज्ञात या प्रदान नहीं किया गया है।`;
    if (targetLang === 'en') return `Scheme applies specifically to residents of ${st}. Citizen state is unknown or not provided.`;
  }

  // 11. State residency satisfied
  m = str.match(/Satisfies state residency requirement \((.*?)\)/i) ||
      str.match(/राज्य निवास की आवश्यकता पूरी करता है \((.*?)\)/i);
  if (m) {
    const st = m[1];
    if (targetLang === 'mr') return `राज्य निवासाची आवश्यकता पूर्ण करते (${st}).`;
    if (targetLang === 'bn') return `রাজ্যের স্থায়ী বসবাসের শর্ত পূরণ করে (${st})।`;
    if (targetLang === 'hi') return `राज्य निवास की आवश्यकता पूरी करता है (${st})।`;
    if (targetLang === 'en') return `Satisfies state residency requirement (${st}).`;
  }

  // 12. All criteria satisfied
  m = str.match(/All (\d+) eligibility criteria satisfied based on confirmed profile/i) ||
      str.match(/पुष्ट प्रोफ़ाइल के आधार पर सभी (\d+) पात्रता मानदंड पूरे हुए/i);
  if (m) {
    const num = m[1];
    if (targetLang === 'mr') return `पुष्टी केलेल्या प्रोफाइलवर आधारित सर्व ${num} पात्रता निकष पूर्ण झाले आहेत.`;
    if (targetLang === 'bn') return `নিশ্চিত প্রোফাইলের ভিত্তিতে সমস্ত ${num} যোগ্যতার মানদণ্ড পূরণ হয়েছে।`;
    if (targetLang === 'hi') return `पुष्ट प्रोफ़ाइल के आधार पर सभी ${num} पात्रता मानदंड पूरे हुए।`;
    if (targetLang === 'en') return `All ${num} eligibility criteria satisfied based on confirmed profile.`;
  }

  // 13. External official verification required
  m = str.match(/External official verification required:\s*(.*)/i) ||
      str.match(/बाहरी आधिकारिक सत्यापन आवश्यक:\s*(.*)/i);
  if (m) {
    const rest = m[1];
    if (targetLang === 'mr') return `बाह्य अधिकृत पडताळणी आवश्यक: ${rest}`;
    if (targetLang === 'bn') return `বাহ্যিক অফিসিয়াল যাচাইকরণ প্রয়োজন: ${rest}`;
    if (targetLang === 'hi') return `बाहरी आधिकारिक सत्यापन आवश्यक: ${rest}`;
    if (targetLang === 'en') return `External official verification required: ${rest}`;
  }

  return null;
};

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
  // Check dynamic rule patterns
  const patternMatch = matchRulePattern(text, targetLang);
  if (patternMatch) return patternMatch;

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

    // Allow object: lt({ en: '...', hi: '...', mr: '...', bn: '...' })
    if (typeof en === 'object' && en !== null && !Array.isArray(en)) {
      return en[language] || en.hi || en.en || '';
    }

    // Allow array: translate each item in array for mr / bn
    if (Array.isArray(en)) {
      const baseArr = Array.isArray(hi) ? hi : en;
      if (language === 'hi') return Array.isArray(hi) ? hi : en;
      if (language === 'en') return en;
      return baseArr.map((item) => {
        if (typeof item === 'string') {
          const hit = lookup(item, language);
          return !isBlank(hit) ? hit : item;
        }
        return item;
      });
    }

    let mrArg = null;
    let bnArg = null;

    if (arg4 !== undefined) {
      mrArg = arg3;
      bnArg = arg4;
    } else if (arg3 !== undefined) {
      // Check if arg3 has Bengali Unicode script [\u0980-\u09FF]
      if (/[\u0980-\u09FF]/.test(arg3)) {
        bnArg = arg3;
      } else {
        mrArg = arg3;
      }
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
   */
  const getBilingualText = (arg1, arg2) => {
    if (arg1 && typeof arg1 === 'object' && !Array.isArray(arg1)) {
      const base = arg2;

      // Handle conditions arrays: satisfied_conditions, unknown_conditions, failed_conditions
      if (['satisfied_conditions', 'unknown_conditions', 'failed_conditions'].includes(base)) {
        const directList = arg1[`${base}_${language}`];
        if (Array.isArray(directList) && directList.length > 0) {
          return directList;
        }
        // Fallback to en or hi or default array, then translate each element
        const fallbackList = arg1[`${base}_en`] || arg1[`${base}_hi`] || arg1[base] || [];
        if (Array.isArray(fallbackList) && fallbackList.length > 0) {
          return fallbackList.map((item) => {
            if (typeof item === 'string') {
              const hit = lookup(item, language);
              return !isBlank(hit) ? hit : item;
            }
            return item;
          });
        }
        return [];
      }

      // 1. Direct language field: e.g. scheme_name_mr, name_mr, benefit_mr, deciding_reason_mr
      let localized = arg1[`${base}_${language}`];
      if (isBlank(localized) && base === 'scheme_name') {
        localized = arg1[`name_${language}`];
      } else if (isBlank(localized) && base === 'name') {
        localized = arg1[`scheme_name_${language}`];
      }
      if (!isBlank(localized)) return localized;

      const enVal = arg1[`${base}_en`] || (base === 'scheme_name' ? arg1.name_en : '') || '';
      const hiVal = arg1[`${base}_hi`] || (base === 'scheme_name' ? arg1.name_hi : '') || '';

      // 2. Lookup / Pattern translate into active language
      const hit = (enVal && lookup(enVal, language)) || (hiVal && lookup(hiVal, language));
      if (!isBlank(hit)) return hit;

      // 3. Fallbacks
      if (language === 'hi') return hiVal || enVal || arg1[base] || '';
      if (language === 'mr' || language === 'bn') {
        // Return English over Hindi if untranslated to avoid language confusion
        return enVal || hiVal || arg1[base] || '';
      }
      return enVal || hiVal || arg1[base] || '';
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
