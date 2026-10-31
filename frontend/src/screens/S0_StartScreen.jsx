import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchRulesStatus } from '../services/api';
import {
  ClipboardList,
  Mic,
  FileText,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Lock,
  Languages,
  BookOpenCheck,
  FileCheck2
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S0_StartScreen() {
  const { language, t } = useLanguage();
  const { setCurrentScreen, setProfile } = useSession();
  const [rulesStatus, setRulesStatus] = useState(null);

  useEffect(() => {
    fetchRulesStatus()
      .then((data) => setRulesStatus(data))
      .catch((err) => console.warn('Rules status error:', err));
  }, []);

  const handleDemoPersona = (personaType) => {
    if (personaType === 'farmer') {
      setProfile({
        age: 48,
        gender: 'male',
        marital_status: 'married',
        state: 'Madhya Pradesh',
        residence_type: 'rural',
        occupation: 'farmer',
        landholding_hectares: 1.5,
        annual_income: 65000,
        is_institutional_landholder: false,
        holds_constitutional_post: false,
        has_pucca_house: false,
        bpl_card_holder: true,
        confirmed_fields: ['age', 'gender', 'marital_status', 'state', 'residence_type', 'occupation', 'landholding_hectares', 'annual_income', 'is_institutional_landholder', 'holds_constitutional_post', 'has_pucca_house', 'bpl_card_holder']
      });
      setCurrentScreen('S3');
    } else if (personaType === 'widow') {
      setProfile({
        age: 52,
        gender: 'female',
        marital_status: 'widow',
        state: 'Madhya Pradesh',
        residence_type: 'rural',
        occupation: 'homemaker',
        annual_income: 24000,
        bpl_card_holder: true,
        holds_constitutional_post: false,
        landholding_hectares: 0.0,
        confirmed_fields: ['age', 'gender', 'marital_status', 'state', 'residence_type', 'occupation', 'annual_income', 'bpl_card_holder', 'holds_constitutional_post']
      });
      setCurrentScreen('S3');
    } else if (personaType === 'student') {
      setProfile({
        age: 19,
        gender: 'female',
        marital_status: 'single',
        state: 'Madhya Pradesh',
        residence_type: 'urban',
        occupation: 'student',
        student_class12_marks_percent: 86.0,
        enrolled_higher_education: true,
        annual_income: 450000,
        holds_constitutional_post: false,
        confirmed_fields: ['age', 'gender', 'marital_status', 'state', 'occupation', 'student_class12_marks_percent', 'enrolled_higher_education', 'annual_income', 'holds_constitutional_post']
      });
      setCurrentScreen('S3');
    }
  };

  return (
    <div className="space-y-10 animate-fade-in">
      {/* 1. Hero Section */}
      <section className="bg-gradient-to-b from-white to-blue-50/50 border border-slate-200/80 rounded-2xl p-6 sm:p-10 shadow-xs relative overflow-hidden">
        <div className="max-w-3xl space-y-4">
          {/* Trust Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-900 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>
              {language === 'hi'
                ? 'सत्यापित सरकारी कल्याण पोर्टल • 100% सटीक नियम'
                : 'Verified Government Scheme Guide • 100% Deterministic Rules'}
            </span>
          </div>

          {/* Heading with Speaker */}
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
              {language === 'hi'
                ? 'सरकारी योजनाओं में अपने अधिकार और पात्रता जानें'
                : 'Discover Government Schemes You May Be Eligible For'}
            </h1>
            <AudioSpeaker
              text={
                language === 'hi'
                  ? 'सरकारी योजनाओं में अपने अधिकार और पात्रता जानें। 2 मिनट से भी कम समय में अपने अधिकार, आवश्यक दस्तावेज़ और आवेदन प्रक्रिया जानें।'
                  : 'Discover Government Schemes You May Be Eligible For in less than 2 minutes.'
              }
              className="mt-1"
            />
          </div>

          {/* Subtitle */}
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-2xl">
            {language === 'hi'
              ? 'आधिकारिक सरकारी नियमों के आधार पर तुरंत अपनी पात्रता जांचें। कोई लॉगिन आवश्यक नहीं, न ही कोई डेटा सहेजा जाता है।'
              : 'Find out your exact entitlement, required documents, and application procedure in less than 2 minutes. Guidance is strictly based on verified official criteria.'}
          </p>

          {/* CTA & Trust note */}
          <div className="pt-2 flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <button
              onClick={() => setCurrentScreen('S1')}
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-700 hover:bg-blue-800 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all min-h-[48px]"
            >
              <span>{language === 'hi' ? 'पात्रता जांच शुरू करें' : 'Get Started Now'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <span className="text-xs text-slate-500 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>
                {language === 'hi'
                  ? 'आधिकारिक सरकारी नियमों पर आधारित • 100% सुरक्षित'
                  : 'Based strictly on verified official guidelines • Zero data stored'}
              </span>
            </span>
          </div>
        </div>
      </section>

      {/* 2. Main Feature Selection (3 Balanced Cards) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">
            {language === 'hi' ? 'अपनी सुविधा अनुसार विकल्प चुनें' : 'Choose How You Want to Begin'}
          </h2>
          <span className="text-xs text-slate-500 hidden sm:inline">
            {language === 'hi' ? 'सरल एवं पारदर्शी प्रक्रिया' : 'Simple, transparent assistance'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Feature Card 1: Questionnaire */}
          <div
            onClick={() => setCurrentScreen('S1')}
            className="premium-card premium-card-hover p-6 flex flex-col justify-between group"
            role="button"
            tabIndex={0}
          >
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100/80 text-blue-800 flex items-center justify-center group-hover:scale-105 transition-transform">
                <ClipboardList className="w-6 h-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="font-bold text-slate-900 text-base group-hover:text-blue-700 transition-colors">
                  {t('start_questionnaire')}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {t('start_questionnaire_desc')}
                </p>
              </div>
            </div>

            <div className="pt-6 mt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-blue-700 group-hover:underline flex items-center gap-1">
                <span>{language === 'hi' ? 'प्रश्नावली शुरू करें' : 'Start Questionnaire'}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                ⚡ ~8 Qs
              </span>
            </div>
          </div>

          {/* Feature Card 2: Voice or Text */}
          <div
            onClick={() => setCurrentScreen('S2')}
            className="premium-card premium-card-hover p-6 flex flex-col justify-between group"
            role="button"
            tabIndex={0}
          >
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-teal-100/80 text-teal-800 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Mic className="w-6 h-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="font-bold text-slate-900 text-base group-hover:text-teal-700 transition-colors">
                  {t('start_voice_text')}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {t('start_voice_text_desc')}
                </p>
              </div>
            </div>

            <div className="pt-6 mt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-teal-700 group-hover:underline flex items-center gap-1">
                <span>{language === 'hi' ? 'बोलें या लिखें' : 'Speak or Type'}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                🎙️ AI Assisted
              </span>
            </div>
          </div>

          {/* Feature Card 3: Form Field Explainer */}
          <div
            onClick={() => setCurrentScreen('S7')}
            className="premium-card premium-card-hover p-6 flex flex-col justify-between group"
            role="button"
            tabIndex={0}
          >
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-amber-100/80 text-amber-900 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FileText className="w-6 h-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="font-bold text-slate-900 text-base group-hover:text-amber-800 transition-colors">
                  {t('form_help_title')}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {language === 'hi'
                    ? 'सरकारी आवेदन फॉर्म के कठिन शब्दों जैसे खसरा, समग्र आईडी, डीबीटी को सरल भाषा में समझें।'
                    : 'Understand complicated terminology and fields on official government application forms.'}
                </p>
              </div>
            </div>

            <div className="pt-6 mt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-amber-800 group-hover:underline flex items-center gap-1">
                <span>{language === 'hi' ? 'फॉर्म शब्द समझें' : 'Explore Form Terms'}</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                🔍 Helper
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Demo Persona Instant Testing Section */}
      <section className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>{language === 'hi' ? 'त्वरित डेमो परीक्षण (Demo Personas)' : 'Quick Demo Personas (Instant Evaluation)'}</span>
            </h3>
            <p className="text-xs text-slate-500">
              {language === 'hi'
                ? 'हैकथॉन मूल्यांकन हेतु एक क्लिक में तीनों प्रमुख प्रोफाइल का परीक्षण करें:'
                : 'Click any profile below to instantly test the full end-to-end evaluation journey:'}
            </p>
          </div>
          {rulesStatus && (
            <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-lg flex items-center gap-1.5 self-start sm:self-auto">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold">
                {language === 'hi'
                  ? `${rulesStatus.verified_schemes} सत्यापित सरकारी योजनाएं सक्रिय`
                  : `${rulesStatus.verified_schemes} Verified Schemes Active`}
              </span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          {/* Persona 1: Farmer */}
          <button
            onClick={() => handleDemoPersona('farmer')}
            className="p-4 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 text-left transition-all hover:shadow-sm group min-h-[52px]"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-2xl">🌾</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                {language === 'hi' ? 'किसान' : 'Farmer'}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-emerald-800 transition-colors">
              {language === 'hi' ? 'ग्रामीण किसान' : 'Rural Farmer'}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {language === 'hi' ? '48 वर्ष, 1.5 हेक्टेयर भूमि, मध्य प्रदेश' : '48y, 1.5 ha land, MP resident'}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-emerald-700 flex items-center gap-1">
              <span>{language === 'hi' ? 'पात्र: PM-Kisan, PMAY-G' : 'Eligible: PM-Kisan, PMAY-G'}</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>

          {/* Persona 2: Widow */}
          <button
            onClick={() => handleDemoPersona('widow')}
            className="p-4 rounded-xl border border-slate-200 hover:border-rose-400 hover:bg-rose-50/20 text-left transition-all hover:shadow-sm group min-h-[52px]"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-2xl">👩</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                {language === 'hi' ? 'विधवा' : 'Widow'}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-rose-800 transition-colors">
              {language === 'hi' ? 'विधवा महिला' : 'Widowed Woman'}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {language === 'hi' ? '52 वर्ष, BPL राशन कार्ड, मध्य प्रदेश' : '52y, BPL card, MP resident'}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-rose-700 flex items-center gap-1">
              <span>{language === 'hi' ? 'पात्र: IGNWPS, लाड़ली बहना' : 'Eligible: IGNWPS, Ladli Behna'}</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>

          {/* Persona 3: Student */}
          <button
            onClick={() => handleDemoPersona('student')}
            className="p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/20 text-left transition-all hover:shadow-sm group min-h-[52px]"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-2xl">🎓</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                {language === 'hi' ? 'विद्यार्थी' : 'Student'}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-blue-800 transition-colors">
              {language === 'hi' ? 'कॉलेज छात्र' : 'College Student'}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {language === 'hi' ? '19 वर्ष, 86% 12वीं बोर्ड, मध्य प्रदेश' : '19y, 86% marks, MP domicile'}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-blue-700 flex items-center gap-1">
              <span>{language === 'hi' ? 'पात्र: MMVY छात्रवृत्ति' : 'Eligible: MMVY Scholarship'}</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>
        </div>
      </section>

      {/* 4. Trust and Assistance Pillars */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <Languages className="w-5 h-5 text-blue-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {language === 'hi' ? 'द्विभाषी सहायता' : 'Bilingual Support'}
          </h5>
          <p className="text-[11px] text-slate-500">
            {language === 'hi' ? 'हिन्दी और अंग्रेजी' : 'Hindi & English'}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <BookOpenCheck className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {language === 'hi' ? 'आधिकारिक स्रोत' : 'Official Sources'}
          </h5>
          <p className="text-[11px] text-slate-500">
            {language === 'hi' ? 'सत्यापित नियम' : 'Verified Guidelines'}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <FileCheck2 className="w-5 h-5 text-indigo-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {language === 'hi' ? 'दस्तावेज़ चेकलिस्ट' : 'Document Checklist'}
          </h5>
          <p className="text-[11px] text-slate-500">
            {language === 'hi' ? 'एकीकृत एवं प्रिंट' : 'De-duplicated & Print'}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <Lock className="w-5 h-5 text-amber-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {language === 'hi' ? 'गोपनीयता की गारंटी' : 'Privacy Guarantee'}
          </h5>
          <p className="text-[11px] text-slate-500">
            {language === 'hi' ? 'शून्य डेटा संचयन' : 'Zero Data Retention'}
          </p>
        </div>
      </section>
    </div>
  );
}
