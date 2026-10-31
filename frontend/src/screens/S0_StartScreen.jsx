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
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen, setProfile, openDocumentGuide } = useSession();
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
    <div className="space-y-8 animate-fade-in">
      {/* 1. Civic Hero Section (Navy & Warm Off-White Civic Direction) */}
      <section className="bg-gradient-to-br from-[#0c1a38] via-[#102450] to-[#0a1630] text-white border border-blue-900/60 rounded-3xl p-6 sm:p-10 shadow-lg relative overflow-hidden">
        {/* Decorative civic backdrop glow */}
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-16 w-80 h-80 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-8 space-y-4">
            {/* Trust Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-950/80 border border-blue-700/60 text-blue-200 text-xs font-semibold backdrop-blur-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>
                {lt('Verified Government Scheme Guide • 100% Deterministic Rules', 'सत्यापित सरकारी कल्याण पोर्टल • 100% सटीक नियम')}
              </span>
            </div>

            {/* Heading with Speaker */}
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                {lt('Discover Government Schemes You May Be Eligible For', 'सरकारी योजनाओं में अपने अधिकार और पात्रता जानें')}
              </h1>
              <AudioSpeaker
                text={
                  lt('Discover Government Schemes You May Be Eligible For in less than 2 minutes.', 'सरकारी योजनाओं में अपने अधिकार और पात्रता जानें। 2 मिनट से भी कम समय में अपने अधिकार, आवश्यक दस्तावेज़ और आवेदन प्रक्रिया जानें।')
                }
                className="mt-1 flex-shrink-0 bg-blue-900/60 border-blue-700 text-white hover:bg-blue-800"
              />
            </div>

            {/* Subtitle */}
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              {lt('Find out your exact entitlement, required documents with illustrative sample previews, and application procedure in less than 2 minutes. Guidance is strictly based on verified official criteria.', 'आधिकारिक सरकारी नियमों के आधार पर तुरंत अपनी पात्रता जांचें, आवश्यक दस्तावेज़ों का आधिकारिक नमूना देखें और सीधे अधिकृत पोर्टल पर आवेदन करें। कोई लॉगिन आवश्यक नहीं, न ही कोई डेटा सहेजा जाता है।')}
            </p>

            {/* Hero Quick Metrics */}
            <div className="pt-2 flex flex-wrap items-center gap-4 text-xs text-slate-300">
              <span className="flex items-center gap-1.5 bg-blue-950/60 px-3 py-1.5 rounded-lg border border-blue-800/40">
                <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>
                  {lt('Deterministic Rules', 'सत्यापित नियम')}
                </span>
              </span>
              <span className="flex items-center gap-1.5 bg-blue-950/60 px-3 py-1.5 rounded-lg border border-blue-800/40">
                <FileCheck2 className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span>
                  {lt('Document Guide & Samples', 'दस्तावेज़ गाइड व नमूने')}
                </span>
              </span>
              <span className="flex items-center gap-1.5 bg-blue-950/60 px-3 py-1.5 rounded-lg border border-blue-800/40">
                <Lock className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <span>
                  {lt('No profile storage', 'प्रोफ़ाइल सहेजी नहीं जाती')}
                </span>
              </span>
            </div>
          </div>

          {/* Citizen Representation Visual Pillar (Image 2 & 3 Aesthetic) */}
          <div className="lg:col-span-4 bg-gradient-to-b from-blue-950/50 to-slate-900/80 p-5 rounded-2xl border border-blue-800/40 backdrop-blur-xs space-y-3 text-center sm:text-left">
            <p className="text-[11px] font-bold uppercase tracking-wider text-amber-300">
              {lt('Welfare Services for Every Citizen', 'सभी नागरिकों के लिए कल्याणकारी सेवाएं')}
            </p>
            <div className="grid grid-cols-2 gap-2.5">
              <div className="bg-[#12234a]/80 p-3 rounded-xl border border-blue-800/30 text-center space-y-1">
                <span className="text-2xl">🌾</span>
                <p className="text-xs font-bold text-white">{lt('Farmers', 'किसान कल्याण')}</p>
                <p className="text-[10px] text-slate-400">{lt('Direct Aid', 'PM-Kisan, सिंचाई')}</p>
              </div>
              <div className="bg-[#12234a]/80 p-3 rounded-xl border border-blue-800/30 text-center space-y-1">
                <span className="text-2xl">👩‍💼</span>
                <p className="text-xs font-bold text-white">{lt('Women', 'महिला सशक्तिकरण')}</p>
                <p className="text-[10px] text-slate-400">{lt('Social Security', 'लाड़ली बहना, पेंशन')}</p>
              </div>
              <div className="bg-[#12234a]/80 p-3 rounded-xl border border-blue-800/30 text-center space-y-1">
                <span className="text-2xl">🎓</span>
                <p className="text-xs font-bold text-white">{lt('Students', 'विद्यार्थी')}</p>
                <p className="text-[10px] text-slate-400">{lt('Scholarships', 'MMVY छात्रवृत्ति')}</p>
              </div>
              <div className="bg-[#12234a]/80 p-3 rounded-xl border border-blue-800/30 text-center space-y-1">
                <span className="text-2xl">👨‍👩‍👧‍👦</span>
                <p className="text-xs font-bold text-white">{lt('Families', 'परिवार')}</p>
                <p className="text-[10px] text-slate-400">{lt('Housing & Health', 'आवास, राशन, स्वास्थ्य')}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Two Primary Action Cards (Images 2 & 3 Core Structure) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              {lt('Two Easy Ways to Check Eligibility', 'पात्रता जांच के दो आसान तरीके')}
            </h2>
            <p className="text-xs text-slate-500">
              {lt('Choose either method to discover your entitlements:', 'अपनी सुविधा के अनुसार कोई भी एक विकल्प चुनें:')}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Action Card 1: Guided Questionnaire */}
          <div
            onClick={() => setCurrentScreen('S1')}
            className="group relative bg-white border-2 border-blue-200 hover:border-blue-600 rounded-2xl p-6 sm:p-7 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            role="button"
            tabIndex={0}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-700 border border-blue-200 flex items-center justify-center group-hover:scale-105 transition-transform shadow-xs">
                  <ClipboardList className="w-7 h-7" />
                </div>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                  {lt('Recommended', 'अनुशंसित (Recommended)')}
                </span>
              </div>

              <div className="space-y-2">
                <h3 className="font-extrabold text-slate-900 text-lg group-hover:text-blue-700 transition-colors">
                  {lt('1. Answer a Few Questions', '१. कुछ सरल प्रश्नों के उत्तर दें')}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {lt('Answer 4 to 8 simple, step-by-step questions tailored to your profile. Every question explains why it is asked.', 'अपनी प्रोफ़ाइल के अनुसार 4 से 8 सीधे प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के साथ कारण और उदाहरण समझाए गए हैं।')}
                </p>
              </div>

              <div className="pt-2 flex flex-wrap gap-2 text-[11px] font-semibold text-slate-500">
                <span className="bg-slate-100 px-2.5 py-1 rounded-md">⚡ 2 मिनट में पूरा</span>
                <span className="bg-slate-100 px-2.5 py-1 rounded-md">✓ कोई गलत व्याख्या नहीं</span>
              </div>
            </div>

            <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between">
              <span className="text-sm font-bold text-blue-700 group-hover:underline flex items-center gap-1.5">
                <span>{lt('Start Questionnaire', 'प्रश्नावली शुरू करें')}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-xs text-slate-400 font-medium">
                ~8 Questions
              </span>
            </div>
          </div>

          {/* Action Card 2: Speak or Type (Free-text / Voice) */}
          <div
            onClick={() => setCurrentScreen('S2')}
            className="group relative bg-white border-2 border-teal-200 hover:border-teal-600 rounded-2xl p-6 sm:p-7 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            role="button"
            tabIndex={0}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-14 h-14 rounded-2xl bg-teal-50 text-teal-700 border border-teal-200 flex items-center justify-center group-hover:scale-105 transition-transform shadow-xs">
                  <Mic className="w-7 h-7" />
                </div>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                  {lt('Voice or Text', 'आवाज़ या विवरण')}
                </span>
              </div>

              <div className="space-y-2">
                <h3 className="font-extrabold text-slate-900 text-lg group-hover:text-teal-700 transition-colors">
                  {lt('2. Tell Us About Yourself', '२. अपने बारे में बोलकर या लिखकर बताएं')}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {lt('Speak in your mother tongue or type naturally. Our assistant extracts profile fields for your explicit review before applying verified rules.', 'अपनी भाषा में बोलें या लिखें (जैसे "मैं रीवा का किसान हूँ, 2 एकड़ जमीन है")। एआई जानकारी निकालेगा और पुष्टि के बाद ही नियम लागू होंगे।')}
                </p>
              </div>

              <div className="pt-2 flex flex-wrap gap-2 text-[11px] font-semibold text-slate-500">
                <span className="bg-slate-100 px-2.5 py-1 rounded-md">
                  {lt('🎙️ Voice Support', '🎙️ आवाज़ सहायता')}
                </span>
                <span className="bg-slate-100 px-2.5 py-1 rounded-md">👁️ नागरिक समीक्षा अनिवार्य</span>
              </div>
            </div>

            <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between">
              <span className="text-sm font-bold text-teal-700 group-hover:underline flex items-center gap-1.5">
                <span>{lt('Speak or Type', 'बोलें या लिखें')}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-xs text-slate-400 font-medium">
                AI + Manual Review
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Prominent Document Guide Feature Card (New S8 Highlight) */}
      <section className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-2 border-amber-300/80 rounded-2xl p-6 sm:p-7 shadow-xs relative overflow-hidden">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100 text-amber-900 text-xs font-bold border border-amber-300">
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span>{lt('New Feature: Official Document Guide', 'नया फीचर: आधिकारिक दस्तावेज़ मार्गदर्शिका')}</span>
            </div>
            <h3 className="text-lg sm:text-xl font-extrabold text-slate-900 tracking-tight">
              {lt('How to Obtain Scheme Documents? Sample Previews & Direct Portal Links', 'सरकारी प्रमाण पत्र कैसे बनवाएं? सांकेतिक नमूने एवं सीधे ऑनलाइन आवेदन लिंक')}
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              {lt('Complete catalogue of required government proofs with issuing authorities, step-by-step procedures, watermarked synthetic sample previews, and verified application portal links.', 'आय प्रमाण पत्र, मूल निवास, जाति प्रमाण पत्र, समग्र आईडी, 12वीं अंकसूची आदि के जारीकर्ता, क्या जांचना है, सांकेतिक नमूने और सीधे आधिकारिक सरकारी आवेदन पोर्टल (जैसे MP e-District, UIDAI, crsorgi) की पूरी जानकारी।')}
            </p>
            <div className="flex flex-wrap gap-2 pt-1 text-[11px] font-semibold text-amber-900">
              <span className="bg-amber-100/70 px-2.5 py-0.5 rounded border border-amber-200">11+ सरकारी प्रमाण पत्र</span>
              <span className="bg-amber-100/70 px-2.5 py-0.5 rounded border border-amber-200">वाटरमार्क सांकेतिक नमूने</span>
              <span className="bg-amber-100/70 px-2.5 py-0.5 rounded border border-amber-200">आधिकारिक सरकारी पोर्टल</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto">
            <button
              onClick={() => openDocumentGuide()}
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-sm shadow-md transition-all min-h-[48px]"
            >
              <FileCheck2 className="w-4 h-4" />
              <span>{lt('Open Document Guide', 'दस्तावेज़ मार्गदर्शिका खोलें')}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentScreen('S7')}
              className="inline-flex items-center justify-center gap-2 px-4 py-3 bg-white hover:bg-slate-100 text-slate-700 font-semibold rounded-xl text-xs border border-slate-300 transition-colors min-h-[48px]"
            >
              <FileText className="w-4 h-4 text-slate-500" />
              <span>{lt('Form Terms', 'कठिन फॉर्म शब्द समझें')}</span>
            </button>
          </div>
        </div>
      </section>

      {/* 3. Demo Persona Instant Testing Section */}
      <section className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>{lt('Quick Demo Personas (Instant Evaluation)', 'त्वरित डेमो परीक्षण (Demo Personas)')}</span>
            </h3>
            <p className="text-xs text-slate-500">
              {lt('Click any profile below to instantly test the full end-to-end evaluation journey:', 'हैकथॉन मूल्यांकन हेतु एक क्लिक में तीनों प्रमुख प्रोफाइल का परीक्षण करें:')}
            </p>
          </div>
          {rulesStatus && (
            <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-lg flex items-center gap-1.5 self-start sm:self-auto">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold">
                {lt(`${rulesStatus.verified_schemes} Verified Schemes Active`, `${rulesStatus.verified_schemes} सत्यापित सरकारी योजनाएं सक्रिय`)}
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
                {lt('Farmer', 'किसान')}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-emerald-800 transition-colors">
              {lt('Rural Farmer', 'ग्रामीण किसान')}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {lt('48y, 1.5 ha land, MP resident', '48 वर्ष, 1.5 हेक्टेयर भूमि, मध्य प्रदेश')}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-emerald-700 flex items-center gap-1">
              <span>{lt('Eligible: PM-Kisan, PMAY-G', 'पात्र: PM-Kisan, PMAY-G')}</span>
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
                {lt('Widow', 'विधवा')}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-rose-800 transition-colors">
              {lt('Widowed Woman', 'विधवा महिला')}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {lt('52y, BPL card, MP resident', '52 वर्ष, BPL राशन कार्ड, मध्य प्रदेश')}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-rose-700 flex items-center gap-1">
              <span>{lt('Eligible: IGNWPS, Ladli Behna', 'पात्र: IGNWPS, लाड़ली बहना')}</span>
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
                {lt('Student', 'विद्यार्थी')}
              </span>
            </div>
            <h4 className="font-bold text-slate-900 text-sm group-hover:text-blue-800 transition-colors">
              {lt('College Student', 'कॉलेज छात्र')}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {lt('19y, 86% marks, MP domicile', '19 वर्ष, 86% 12वीं बोर्ड, मध्य प्रदेश')}
            </p>
            <div className="mt-2 text-[11px] font-semibold text-blue-700 flex items-center gap-1">
              <span>{lt('Eligible: MMVY Scholarship', 'पात्र: MMVY छात्रवृत्ति')}</span>
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
            {lt('Bilingual Support', 'द्विभाषी सहायता')}
          </h5>
          <p className="text-[11px] text-slate-500">
            {lt('Hindi & English', 'हिन्दी और अंग्रेजी')}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <BookOpenCheck className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {lt('Official Sources', 'आधिकारिक स्रोत')}
          </h5>
          <p className="text-[11px] text-slate-500">
            {lt('Verified Guidelines', 'सत्यापित नियम')}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <FileCheck2 className="w-5 h-5 text-indigo-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {lt('Document Checklist', 'दस्तावेज़ चेकलिस्ट')}
          </h5>
          <p className="text-[11px] text-slate-500">
            {lt('De-duplicated & Print', 'एकीकृत एवं प्रिंट')}
          </p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-1 text-center">
          <Lock className="w-5 h-5 text-amber-600 mx-auto mb-1" />
          <h5 className="font-bold text-xs text-slate-900">
            {lt('Privacy Guarantee', 'गोपनीयता की गारंटी')}
          </h5>
          <p className="text-[11px] text-slate-500">
            {lt('No profile storage', 'प्रोफ़ाइल सहेजी नहीं जाती')}
          </p>
        </div>
      </section>
    </div>
  );
}
