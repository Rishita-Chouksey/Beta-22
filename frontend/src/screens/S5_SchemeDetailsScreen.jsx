import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchSchemeDetails } from '../services/api';
<<<<<<< HEAD
import VerificationQuestionnaire from '../components/VerificationQuestionnaire';
=======
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
import {
  ArrowLeft,
  ExternalLink,
  Phone,
  CheckCircle,
  XCircle,
  HelpCircle,
  FileCheck,
  ListOrdered,
  AlertTriangle,
  Info,
  Calendar,
  Eye,
<<<<<<< HEAD
  FileText,
  ShieldCheck,
  Building2,
  ChevronRight,
  Sparkles,
  RefreshCw,
  Share2
=======
  Building2,
  FileText,
  MessageSquare,
  ShieldCheck,
  Award
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S5_SchemeDetailsScreen() {
  const { language, t } = useLanguage();
  const {
    activeSchemeModal,
    setActiveSchemeModal,
    setCurrentScreen,
    openDocumentGuide,
<<<<<<< HEAD
    evaluationResults
=======
    setIsChatOpen,
    profile
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
  } = useSession();

  const [fullScheme, setFullScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
<<<<<<< HEAD
  const [showVerificationForm, setShowVerificationForm] = useState(false);

  // If activeSchemeModal changes, refresh full scheme data
=======

>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
  useEffect(() => {
    if (activeSchemeModal?.scheme_id) {
      setIsLoading(true);
      fetchSchemeDetails(activeSchemeModal.scheme_id)
        .then((data) => setFullScheme(data))
        .catch((err) => console.error('Fetch scheme details error:', err))
        .finally(() => setIsLoading(false));
    }
  }, [activeSchemeModal]);

<<<<<<< HEAD
  // Keep activeScheme in sync with latest evaluationResults if re-evaluated
  const currentSchemeId = activeSchemeModal?.scheme_id;
  const currentEvaluation = (() => {
    if (!evaluationResults || !currentSchemeId) return activeSchemeModal;
    const all = [
      ...(evaluationResults.eligible || []),
      ...(evaluationResults.not_sure || []),
      ...(evaluationResults.not_eligible || []),
      ...(evaluationResults.no_rules || [])
    ];
    const match = all.find((s) => s.scheme_id === currentSchemeId);
    return match || activeSchemeModal;
  })();

  if (!currentEvaluation) {
    return (
      <div className="py-16 text-center space-y-4">
        <div className="text-4xl">🏛️</div>
        <h2 className="text-xl font-bold text-slate-800">
          {language === 'hi' ? 'कोई योजना चयनित नहीं है' : 'No Scheme Selected'}
        </h2>
        <button
          onClick={() => setCurrentScreen('S4')}
          className="px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-bold hover:bg-teal-700"
        >
          {language === 'hi' ? 'योजना परिणामों पर वापस जाएं' : 'Back to Scheme Results'}
=======
  // If no scheme selected, return to S4
  if (!activeSchemeModal) {
    return (
      <div className="text-center py-16 space-y-4">
        <p className="text-slate-600 font-semibold">
          {language === 'hi' ? 'कोई योजना चयनित नहीं है।' : 'No scheme selected.'}
        </p>
        <button
          onClick={() => setCurrentScreen('S4')}
          className="px-4 py-2 bg-slate-900 text-white font-bold rounded-xl text-xs"
        >
          {language === 'hi' ? 'परिणामों पर वापस जाएं' : 'Back to Results'}
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
        </button>
      </div>
    );
  }

<<<<<<< HEAD
  const name = language === 'hi' ? currentEvaluation.scheme_name_hi : currentEvaluation.scheme_name_en;
  const secondaryName = language === 'hi' ? currentEvaluation.scheme_name_en : currentEvaluation.scheme_name_hi;
  const benefit = language === 'hi' ? currentEvaluation.benefit_hi : currentEvaluation.benefit_en;
  const reason = language === 'hi' ? currentEvaluation.deciding_reason_hi : currentEvaluation.deciding_reason_en;
  const isEligible = currentEvaluation.status === 'ELIGIBLE';
  const isNotSure = currentEvaluation.status === 'NOT SURE';
  const isNotEligible = currentEvaluation.status === 'NOT ELIGIBLE';

  const missingFields = currentEvaluation.missing_fields || [];
  const ruleResults = currentEvaluation.rule_results || [];

  const handleBack = () => {
    setCurrentScreen('S4');
  };

  const handleGenerateChecklist = () => {
    setCurrentScreen('S6');
  };

  const getStatusBanner = () => {
    if (isEligible) {
      return (
        <div className="bg-emerald-50 border-2 border-emerald-400 rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 flex-shrink-0 mt-0.5">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-200 text-emerald-950">
                  {language === 'hi' ? 'पात्रता स्थिति: संभावित पात्र' : 'Status: Likely Eligible'}
                </span>
                <span className="text-xs text-emerald-800 font-semibold">
                  {language === 'hi' ? '100% नियम उत्तीर्ण' : 'All Rules Passed'}
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-emerald-950">
                {language === 'hi'
                  ? 'बधाई हो! आपकी प्रोफाइल इस योजना के सभी वैधानिक नियमों के अनुकूल है।'
                  : 'Congratulations! Your profile satisfies all official eligibility criteria.'}
              </h3>
              <p className="text-xs sm:text-sm text-emerald-900 leading-relaxed max-w-2xl">
                {reason}
              </p>
            </div>
          </div>

          <button
            onClick={handleGenerateChecklist}
            className="w-full sm:w-auto px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs sm:text-sm font-bold shadow-sm transition flex items-center justify-center gap-2 whitespace-nowrap min-h-[44px]"
          >
            <FileText className="w-4 h-4" />
            <span>{language === 'hi' ? 'दस्तावेज़ चेकलिस्ट देखें' : 'View Document Checklist'}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      );
    }

    if (isNotSure) {
      return (
        <div className="bg-amber-50 border-2 border-amber-400 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xs">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-800 flex-shrink-0 mt-0.5">
                <HelpCircle className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-200 text-amber-950">
                    {language === 'hi' ? 'पात्रता स्थिति: सत्यापन आवश्यक' : 'Status: Needs Verification'}
                  </span>
                  <span className="text-xs text-amber-900 font-semibold">
                    {missingFields.length} {language === 'hi' ? 'अधूरी जानकारी' : 'Unknown Fields'}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-amber-950">
                  {language === 'hi'
                    ? 'आप इस योजना के लिए पात्र हो सकते हैं, परंतु कुछ जानकारी अभी अधूरी है।'
                    : 'You may qualify for this scheme, but additional verification is needed.'}
                </h3>
                <p className="text-xs sm:text-sm text-amber-900 leading-relaxed max-w-2xl">
                  {reason}
                </p>
              </div>
            </div>

            <button
              onClick={() => setShowVerificationForm((prev) => !prev)}
              className="w-full sm:w-auto px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs sm:text-sm font-bold shadow-sm transition flex items-center justify-center gap-2 whitespace-nowrap min-h-[44px]"
            >
              <Sparkles className="w-4 h-4" />
              <span>
                {showVerificationForm
                  ? (language === 'hi' ? 'प्रश्नावली छुपाएं' : 'Hide Questionnaire')
                  : (language === 'hi' ? 'अभी सत्यापित करें (अधूरी जानकारी भरें)' : 'Verify Now (Answer Unknowns)')}
              </span>
            </button>
          </div>

          {/* Interactive Inline Verification Questionnaire */}
          {showVerificationForm && missingFields.length > 0 && (
            <div className="pt-2">
              <VerificationQuestionnaire
                missingFields={missingFields}
                targetSchemeId={currentSchemeId}
                targetSchemeName={name}
                onComplete={() => {
                  setShowVerificationForm(false);
                }}
                onCancel={() => setShowVerificationForm(false)}
              />
            </div>
          )}
        </div>
      );
    }

    if (isNotEligible) {
      return (
        <div className="bg-rose-50 border-2 border-rose-300 rounded-2xl p-5 sm:p-6 flex items-start gap-3.5 shadow-xs">
          <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-rose-700 flex-shrink-0 mt-0.5">
            <XCircle className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <span className="text-xs font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-rose-200 text-rose-950">
              {language === 'hi' ? 'पात्रता स्थिति: अपात्र (Not Eligible)' : 'Status: Not Eligible'}
            </span>
            <h3 className="text-base sm:text-lg font-bold text-rose-950">
              {language === 'hi'
                ? 'आपकी वर्तमान प्रोफाइल इस योजना के कम से कम एक वैधानिक नियम को पूरा नहीं करती है।'
                : 'Your profile does not satisfy at least one mandatory statutory rule.'}
            </h3>
            <p className="text-xs sm:text-sm text-rose-900 leading-relaxed max-w-2xl">
              {reason}
            </p>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="w-full space-y-6 sm:space-y-8 animate-fade-in pb-12">
      {/* 1. Top Navigation & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <button
          onClick={handleBack}
          className="self-start inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-slate-300 text-xs sm:text-sm font-bold text-slate-700 hover:bg-slate-100 transition shadow-2xs cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4 text-teal-700" />
          <span>{language === 'hi' ? '← परिणामों पर वापस जाएं' : '← Back to Scheme Results'}</span>
        </button>

        <div className="flex items-center gap-3 text-xs text-slate-500 flex-wrap">
          <span className="flex items-center gap-1 font-medium">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{t('verified_on')}: {currentEvaluation.last_verified_date}</span>
          </span>

          {currentEvaluation.official_source_url && (
            <a
              href={currentEvaluation.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-teal-700 hover:text-teal-900 font-bold hover:underline"
            >
              <span>{t('official_source')}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>

      {/* 2. Scheme Hero Card */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="text-xs font-extrabold uppercase tracking-wider px-3 py-1 rounded-full bg-slate-900 text-white">
            {currentEvaluation.level === 'central'
              ? (language === 'hi' ? 'केंद्रीय योजना (Central Govt)' : 'Central Government Scheme')
              : (language === 'hi' ? 'राज्य योजना (State Government)' : 'State Government Scheme')}
          </span>

          <span className="text-xs font-bold px-3 py-1 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
            {language === 'hi' ? (currentEvaluation.category_hi || currentEvaluation.category) : currentEvaluation.category}
          </span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-1 flex-1">
            <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-950 tracking-tight leading-tight">
              {name}
            </h1>
            {secondaryName && secondaryName !== name && (
              <p className="text-sm sm:text-base font-semibold text-slate-500">
                {secondaryName}
              </p>
            )}
          </div>

          <AudioSpeaker
            text={`${name}। ${benefit}। ${reason}`}
            className="w-10 h-10 bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300"
          />
        </div>

        {/* Entitlement Banner */}
        <div className="bg-gradient-to-r from-teal-50 to-blue-50/60 border border-teal-200/80 rounded-2xl p-4 sm:p-5 flex items-start gap-3">
          <span className="text-2xl sm:text-3xl">💰</span>
          <div className="space-y-0.5">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-teal-900 block">
              {t('entitlements')}
            </span>
            <p className="text-sm sm:text-base font-bold text-slate-900 leading-relaxed">
              {benefit}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Status Ribbon */}
      {getStatusBanner()}

      {/* 4. ⭐ COMPLETE ELIGIBILITY CRITERIA & RULE AUDIT SECTION */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-6 shadow-sm">
        <div className="space-y-1.5 border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-teal-700" />
            <h2 className="text-lg sm:text-2xl font-extrabold text-slate-950">
              {language === 'hi'
                ? 'योजना के संपूर्ण पात्रता नियम एवं मानदंड'
                : 'All Eligibility Criteria & Rule Audit'}
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed max-w-3xl">
            {language === 'hi'
              ? 'प्रत्येक नियम को हमारी पायथन एएसटी नियम प्रणाली द्वारा गणितीय शुद्धता के साथ जाँचा जाता है। एआई को पात्रता का मनमाना अनुमान लगाने की अनुमति नहीं है।'
              : 'Each criterion is mathematically checked by our deterministic Python AST rule engine against your verified profile. AI is strictly prohibited from guessing eligibility.'}
          </p>
        </div>

        {/* Detailed Criteria Cards */}
        {ruleResults && ruleResults.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ruleResults.map((r, idx) => {
              const ruleReason = language === 'hi' ? r.reason_hi : r.reason_en;
              const isPass = r.outcome === 'PASS';
              const isFail = r.outcome === 'FAIL';
              const isUnk = r.outcome === 'UNKNOWN';

              // Format field name
              const cleanField = r.field.replace(/_/g, ' ');
=======
  const name = language === 'hi'
    ? (activeSchemeModal.scheme_name_hi || fullScheme?.name_hi || activeSchemeModal.scheme_name_en)
    : (activeSchemeModal.scheme_name_en || fullScheme?.name_en);

  const benefit = language === 'hi'
    ? (activeSchemeModal.benefit_hi || fullScheme?.benefit_hi || activeSchemeModal.benefit_en)
    : (activeSchemeModal.benefit_en || fullScheme?.benefit_en);

  const desc = language === 'hi'
    ? (fullScheme?.description_hi || activeSchemeModal.deciding_reason_hi || '')
    : (fullScheme?.description_en || activeSchemeModal.deciding_reason_en || '');

  const ruleResults = activeSchemeModal.rule_results || [];

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Top Breadcrumb & Back Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
        <button
          onClick={() => setCurrentScreen('S4')}
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 px-3.5 py-2 rounded-xl transition-all shadow-2xs w-fit"
        >
          <ArrowLeft className="w-4 h-4 text-teal-700" />
          <span>{language === 'hi' ? '← योजनाओं के परिणामों पर वापस जाएं' : '← Back to Eligible Schemes'}</span>
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="hidden sm:inline">YojnaSarthi</span>
          <span className="hidden sm:inline">•</span>
          <span>{activeSchemeModal.level === 'central' ? 'Central Scheme' : 'State Scheme'}</span>
          <span>•</span>
          <span className="font-semibold text-slate-600">{activeSchemeModal.category}</span>
        </div>
      </div>

      {/* Main Header Hero Box */}
      <div className="bg-white border border-slate-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-slate-900 text-teal-300">
              {activeSchemeModal.level === 'central'
                ? (language === 'hi' ? '🏛️ केंद्रीय योजना (Central Scheme)' : '🏛️ Central Government Scheme')
                : (language === 'hi' ? '🏛️ राज्य सरकार योजना (State Scheme)' : '🏛️ State Government Scheme')}
            </span>
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              {activeSchemeModal.category}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
              <Calendar className="w-3 h-3 text-slate-400" />
              <span>{t('verified_on')}: {activeSchemeModal.last_verified_date || 'Current Session'}</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <AudioSpeaker
              text={`${name}। ${benefit}। ${desc}`}
              className="w-9 h-9 text-slate-700 hover:text-slate-950 bg-slate-100 border border-slate-200 rounded-xl"
            />
            {fullScheme?.official_source_url && (
              <a
                href={fullScheme.official_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-teal-50 text-teal-800 hover:bg-teal-100 border border-teal-200 transition-colors"
              >
                <span>{language === 'hi' ? 'आधिकारिक पोर्टल' : 'Official Portal'}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </div>

        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-snug">
            {name}
          </h1>
          {desc && (
            <p className="text-sm sm:text-base text-slate-600 mt-2 leading-relaxed">
              {desc}
            </p>
          )}
        </div>

        {/* Key Entitlement / Financial Benefit Highlight */}
        <div className="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-transparent border border-emerald-300 rounded-2xl p-5 sm:p-6 space-y-1.5 shadow-2xs">
          <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-xs tracking-wider uppercase">
            <Award className="w-4 h-4 text-emerald-700" />
            <span>💰 {t('entitlements')} (Statutory Assistance)</span>
          </div>
          <p className="text-base sm:text-xl font-bold text-emerald-950 leading-relaxed">
            {benefit}
          </p>
        </div>
      </div>

      {/* FULL COMPREHENSIVE ELIGIBILITY CRITERIA BREAKDOWN */}
      <div className="bg-white border border-slate-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-teal-700" />
              <span>
                {language === 'hi'
                  ? 'वैधानिक पात्रता मापदंड एवं प्रोफ़ाइल सत्यापन'
                  : 'Statutory Eligibility Criteria & Profile Verification'}
              </span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              {language === 'hi'
                ? 'सरकारी गजट अधिसूचना के अनुसार प्रत्येक नियम का सत्यापन परिणाम'
                : 'Deterministic evaluation results under official gazette notifications'}
            </p>
          </div>

          <span className="text-xs font-bold px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 border border-slate-200 self-start sm:self-auto">
            {ruleResults.length} {language === 'hi' ? 'मापदंड जाँचे गए' : 'Criteria Evaluated'}
          </span>
        </div>

        {/* Detailed Criteria Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ruleResults && ruleResults.length > 0 ? (
            ruleResults.map((r, idx) => {
              const ruleReason = language === 'hi' ? r.reason_hi : r.reason_en;
              const isPass = r.outcome === 'PASS';
              const isFail = r.outcome === 'FAIL';
              const isUnknown = r.outcome === 'UNKNOWN';
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f

              return (
                <div
                  key={idx}
<<<<<<< HEAD
                  className={`p-4 sm:p-5 rounded-2xl border transition-all flex flex-col justify-between gap-3 shadow-2xs ${
                    isPass
                      ? 'bg-emerald-50/40 border-emerald-200 hover:border-emerald-300'
                      : isFail
                      ? 'bg-rose-50/40 border-rose-200 hover:border-rose-300'
                      : 'bg-amber-50/40 border-amber-200 hover:border-amber-300'
                  }`}
                >
                  <div className="space-y-2.5">
                    {/* Header: Field & Status Pill */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-700 capitalize">
                        📋 {cleanField}
                      </span>

                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-extrabold border ${
                          isPass
                            ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                            : isFail
                            ? 'bg-rose-100 text-rose-900 border-rose-300'
                            : 'bg-amber-100 text-amber-900 border-amber-300'
                        }`}
                      >
                        {isPass && <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />}
                        {isFail && <XCircle className="w-3.5 h-3.5 text-rose-600" />}
                        {isUnk && <HelpCircle className="w-3.5 h-3.5 text-amber-600" />}
                        <span>
                          {isPass && (language === 'hi' ? 'उत्तीर्ण (PASS)' : 'PASS')}
                          {isFail && (language === 'hi' ? 'विफल (FAIL)' : 'FAIL')}
                          {isUnk && (language === 'hi' ? 'सत्यापन आवश्यक (UNKNOWN)' : 'UNKNOWN')}
                        </span>
                      </span>
                    </div>

                    {/* Requirement comparison */}
                    <div className="bg-white/80 border border-slate-200/80 rounded-xl p-3 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between gap-2 text-slate-600">
                        <span className="font-semibold text-slate-500">
                          {language === 'hi' ? 'नियम शर्त (Requirement):' : 'Official Requirement:'}
                        </span>
                        <span className="font-bold text-slate-900 text-right">
                          {r.operator} {JSON.stringify(r.expected_value)}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-2 text-slate-600 pt-1 border-t border-slate-100">
                        <span className="font-semibold text-slate-500">
                          {language === 'hi' ? 'आपकी जानकारी (Recorded):' : 'Your Recorded Value:'}
                        </span>
                        <span className="font-bold text-slate-900 text-right">
                          {r.actual_value !== null && r.actual_value !== undefined
                            ? String(r.actual_value)
                            : (language === 'hi' ? 'अज्ञात (Not provided)' : 'Unknown')}
                        </span>
                      </div>
                    </div>

                    {/* Explanatory Reason */}
                    <p className="text-xs sm:text-sm text-slate-700 leading-relaxed pt-1">
                      {ruleReason}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-6 text-sm text-slate-500">
            {language === 'hi' ? 'नियम सूची लोड हो रही है...' : 'Loading verified rule breakdown...'}
          </div>
        )}
      </div>

      {/* 5. Important Restrictions & Exclusions */}
      {fullScheme?.restrictions && fullScheme.restrictions.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 text-amber-900">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h3 className="text-lg font-bold">
              {language === 'hi' ? 'महत्वपूर्ण अपवर्जन एवं प्रतिबंध (Exclusion Policies)' : 'Important Exclusion Rules & Restrictions'}
            </h3>
          </div>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
            {fullScheme.restrictions.map((res, i) => (
              <li key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50/50 border border-amber-100">
                <span className="text-amber-600 font-bold">•</span>
                <span className="leading-relaxed">{res}</span>
=======
                  className={`p-4 sm:p-5 rounded-2xl border transition-all flex flex-col justify-between gap-3 ${
                    isPass
                      ? 'bg-emerald-50/50 border-emerald-200 shadow-2xs'
                      : isFail
                      ? 'bg-rose-50/50 border-rose-200 shadow-2xs'
                      : 'bg-amber-50/50 border-amber-200 shadow-2xs'
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-800 uppercase tracking-wider capitalize flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-slate-400 inline-block" />
                        {r.field.replace(/_/g, ' ')}
                      </span>

                      {isPass && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{language === 'hi' ? 'संतुष्ट (Pass)' : 'Eligible (Pass)'}</span>
                        </span>
                      )}
                      {isFail && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-rose-100 text-rose-800 border border-rose-300">
                          <XCircle className="w-3.5 h-3.5 text-rose-600" />
                          <span>{language === 'hi' ? 'अपात्र (Fail)' : 'Ineligible (Fail)'}</span>
                        </span>
                      )}
                      {isUnknown && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-amber-100 text-amber-900 border border-amber-300">
                          <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                          <span>{language === 'hi' ? 'सत्यापन शेष (Unknown)' : 'Verification Needed'}</span>
                        </span>
                      )}
                    </div>

                    <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
                      {ruleReason}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-200/50 text-[11px] text-slate-500 flex items-center justify-between">
                    <span>
                      {isPass && '✓ ' + (language === 'hi' ? 'मापदंड की शर्तें पूर्ण हैं।' : 'Criterion criteria fully met.')}
                      {isFail && '✗ ' + (language === 'hi' ? 'सरकारी सीमा से बाहर अथवा प्रतिबंधित।' : 'Outside permissible statutory boundary.')}
                      {isUnknown && '? ' + (language === 'hi' ? 'प्रोफ़ाइल में अतिरिक्त जानकारी आवश्यक।' : 'Requires answer in verification questionnaire.')}
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-full py-6 text-center text-xs text-slate-500">
              {language === 'hi' ? 'विस्तृत नियम विश्लेषण लोड हो रहा है...' : 'Detailed criteria rules loading...'}
            </div>
          )}
        </div>
      </div>

      {/* Important Exclusions / Restrictions Section if present */}
      {fullScheme?.restrictions && fullScheme.restrictions.length > 0 && (
        <div className="bg-amber-50/90 border border-amber-300 rounded-3xl p-6 sm:p-7 space-y-3 shadow-xs">
          <h3 className="font-bold text-amber-950 flex items-center gap-2 text-sm sm:text-base">
            <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0" />
            <span>
              {language === 'hi' ? 'महत्वपूर्ण अपवर्जन एवं प्रतिबंध (Exclusion Rules)' : 'Statutory Exclusion Criteria & Disqualifications'}
            </span>
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs sm:text-sm text-amber-950">
            {fullScheme.restrictions.map((res, i) => (
              <li key={i} className="flex items-start gap-2 bg-white/70 p-3 rounded-xl border border-amber-200/80">
                <span className="text-amber-800 font-bold">•</span>
                <span>{res}</span>
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
              </li>
            ))}
          </ul>
        </div>
      )}

<<<<<<< HEAD
      {/* 6. Required Documents & Procurement Guide */}
      {fullScheme?.required_documents && fullScheme.required_documents.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-6 shadow-sm">
          <div className="space-y-1 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-teal-700" />
              <h3 className="text-lg sm:text-xl font-extrabold text-slate-950">
                {t('documents_required')}
              </h3>
            </div>
            <p className="text-xs text-slate-500">
              {language === 'hi'
                ? 'आवेदन करने से पूर्व इन आवश्यक प्रमाण पत्रों को तैयार रखें। नमूना देखने हेतु दस्तावेज़ गाइड खोलें।'
                : 'Ensure you possess these documents before applying. Click to view samples and procurement steps.'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {fullScheme.required_documents.map((doc) => {
              const docName = language === 'hi' ? doc.name_hi : doc.name_en;
              const docProc = language === 'hi' ? doc.how_to_get_hi : doc.how_to_get_en;
              return (
                <div
                  key={doc.id}
                  className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-2xl text-xs sm:text-sm space-y-3 flex flex-col justify-between shadow-2xs hover:border-teal-300 transition"
                >
                  <div className="space-y-1.5">
                    <div className="font-bold text-slate-900 text-sm">{docName}</div>
                    <div className="text-slate-600 text-xs leading-relaxed">{docProc}</div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200/80">
                    <button
                      type="button"
                      onClick={() => openDocumentGuide(doc.id, 'S5')}
                      className="inline-flex items-center gap-1.5 text-xs text-amber-900 hover:text-amber-950 font-bold bg-amber-50 hover:bg-amber-100 border border-amber-300 px-3 py-1.5 rounded-xl transition cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5 text-amber-700" />
                      <span>{t('open_in_doc_guide')}</span>
                    </button>

=======
      {/* REQUIRED DOCUMENTS SECTION */}
      {fullScheme?.required_documents && (
        <div className="bg-white border border-slate-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-slate-900 flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-teal-700" />
                <span>{t('documents_required')}</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                {language === 'hi'
                  ? 'आवेदन से पूर्व इन सभी दस्तावेज़ों की मूल व सत्यापित प्रतियां तैयार रखें'
                  : 'Keep original and verified copies of these documents ready before applying'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fullScheme.required_documents.map((doc) => {
              const docName = language === 'hi' ? doc.name_hi : doc.name_en;
              const docProc = language === 'hi' ? doc.how_to_get_hi : doc.how_to_get_en;
              const docPurpose = language === 'hi' ? doc.purpose_hi : doc.purpose_en;

              return (
                <div
                  key={doc.id}
                  className="p-4 sm:p-5 bg-slate-50 border border-slate-200/80 rounded-2xl flex flex-col justify-between space-y-3 hover:border-teal-300 transition-colors shadow-2xs"
                >
                  <div className="space-y-1.5">
                    <h3 className="font-bold text-sm sm:text-base text-slate-900">
                      {docName}
                    </h3>
                    {docPurpose && (
                      <p className="text-xs text-slate-600 leading-relaxed">
                        <strong>{language === 'hi' ? 'उद्देश्य:' : 'Purpose:'}</strong> {docPurpose}
                      </p>
                    )}
                    <p className="text-xs text-slate-600 leading-relaxed">
                      <strong>{language === 'hi' ? 'कहाँ से प्राप्त करें:' : 'How to Obtain:'}</strong> {docProc}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200/60">
                    <button
                      type="button"
                      onClick={() => openDocumentGuide(doc.id, 'S5')}
                      className="inline-flex items-center gap-1.5 text-xs text-amber-900 hover:text-amber-950 font-bold bg-amber-100/70 hover:bg-amber-200/80 border border-amber-300 px-3 py-1.5 rounded-xl transition-colors cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5 text-amber-800" />
                      <span>{t('open_in_doc_guide')}</span>
                    </button>
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
                    {doc.online_url && (
                      <a
                        href={doc.online_url}
                        target="_blank"
                        rel="noopener noreferrer"
<<<<<<< HEAD
                        className="inline-flex items-center gap-1 text-xs text-teal-700 hover:text-teal-900 font-bold px-2 py-1"
=======
                        className="inline-flex items-center gap-1 text-xs text-blue-700 hover:text-blue-900 font-bold px-2.5 py-1.5 rounded-xl bg-blue-50 border border-blue-200"
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
                      >
                        <span>{t('online_link')}</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* 7. Step-by-Step Official Application Procedure */}
      {fullScheme?.application_procedure && fullScheme.application_procedure.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-6 shadow-sm">
          <div className="space-y-1 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2">
              <ListOrdered className="w-5 h-5 text-teal-700" />
              <h3 className="text-lg sm:text-xl font-extrabold text-slate-950">
                {t('how_to_apply')}
              </h3>
            </div>
            <p className="text-xs text-slate-500">
              {language === 'hi'
                ? 'आधिकारिक पोर्टल अथवा नजदीकी लोक सेवा केंद्र / ग्राम पंचायत कार्यालय से आवेदन की प्रक्रिया।'
                : 'Follow these step-by-step instructions for online or nearest physical center submission.'}
=======
      {/* STEP-BY-STEP APPLICATION PROCEDURE */}
      {fullScheme?.application_procedure && (
        <div className="bg-white border border-slate-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-5">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 flex items-center gap-2">
              <ListOrdered className="w-5 h-5 text-teal-700" />
              <span>{t('how_to_apply')}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              {language === 'hi'
                ? 'आधिकारिक पोर्टल अथवा निकटतम लोक सेवा केंद्र (CSC) के माध्यम से चरणबद्ध आवेदन प्रक्रिया'
                : 'Step-by-step verified application procedure via official portal or nearest CSC'}
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
            </p>
          </div>

          <div className="space-y-3">
            {fullScheme.application_procedure.map((step, idx) => (
              <div
                key={idx}
<<<<<<< HEAD
                className="flex items-start gap-3.5 p-4 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs sm:text-sm text-slate-800 leading-relaxed shadow-2xs"
              >
                <span className="w-6 h-6 rounded-full bg-slate-900 text-white font-extrabold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
=======
                className="flex items-start gap-3.5 p-4 rounded-2xl bg-slate-50 border border-slate-200/70 text-xs sm:text-sm text-slate-800 leading-relaxed shadow-2xs"
              >
                <span className="w-7 h-7 rounded-xl bg-slate-900 text-teal-300 font-extrabold flex items-center justify-center text-xs flex-shrink-0 mt-0.5 shadow-xs">
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
                  {idx + 1}
                </span>
                <span className="flex-1 font-medium">{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* 8. Helpline & Contact Bar */}
      <div className="p-5 bg-slate-100/90 border border-slate-200 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs sm:text-sm text-slate-700">
        {fullScheme?.helpline && (
          <span className="flex items-center gap-2 font-semibold">
            <Phone className="w-4 h-4 text-teal-700" />
            <span><strong>{t('helpline')}: </strong>{fullScheme.helpline}</span>
          </span>
        )}

        <span className="flex items-center gap-1.5 text-slate-500 text-xs">
          <Calendar className="w-3.5 h-3.5" />
          <span>{t('verified_on')}: {currentEvaluation.last_verified_date}</span>
        </span>
      </div>

      {/* 9. Bottom Action Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <button
          onClick={handleBack}
          className="w-full sm:w-auto px-6 py-3 border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold rounded-xl text-xs sm:text-sm transition flex items-center justify-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{language === 'hi' ? 'सभी योजनाओं पर वापस जाएं' : 'Back to All Schemes'}</span>
        </button>

        <div className="flex items-center gap-3 w-full sm:w-auto flex-wrap">
=======
      {/* HELPLINE & STATUTORY CONTACTS */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-slate-800 shadow-md">
        <div className="space-y-1">
          <span className="text-[10px] uppercase font-bold tracking-wider text-teal-400">
            {language === 'hi' ? 'आधिकारिक सहायता डेस्क' : 'Official Assistance & Grievance'}
          </span>
          <h3 className="text-base sm:text-lg font-bold">
            {language === 'hi' ? 'योजना संबंधी आधिकारिक संपर्क सूत्र' : 'Official Department Helpline & Nodal Assistance'}
          </h3>
          {fullScheme?.helpline && (
            <p className="text-xs sm:text-sm text-slate-300 flex items-center gap-1.5 font-medium">
              <Phone className="w-4 h-4 text-teal-400" />
              <span><strong>{t('helpline')}:</strong> {fullScheme.helpline}</span>
            </p>
          )}
        </div>

        <div className="flex items-center gap-2.5 flex-wrap self-stretch sm:self-auto">
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
          {fullScheme?.official_source_url && (
            <a
              href={fullScheme.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
<<<<<<< HEAD
              className="flex-1 sm:flex-initial px-6 py-3 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-xl text-xs sm:text-sm shadow-sm transition inline-flex items-center justify-center gap-2 no-underline min-h-[44px]"
=======
              className="px-5 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs sm:text-sm flex items-center gap-2 shadow-sm transition-all"
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
            >
              <span>{t('official_portal')}</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
<<<<<<< HEAD

          {isEligible && (
            <button
              onClick={handleGenerateChecklist}
              className="flex-1 sm:flex-initial px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl text-xs sm:text-sm shadow-sm transition inline-flex items-center justify-center gap-2 min-h-[44px]"
            >
              <FileText className="w-4 h-4" />
              <span>{t('get_checklist')}</span>
            </button>
          )}
=======
        </div>
      </div>

      {/* BOTTOM ACTION BAR */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={() => setCurrentScreen('S4')}
          className="w-full sm:w-auto px-5 py-3 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs sm:text-sm transition-colors text-center"
        >
          {language === 'hi' ? '← सभी योजनाओं पर लौटें' : '← Back to All Schemes'}
        </button>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <button
            onClick={() => setIsChatOpen(true)}
            className="flex-1 sm:flex-none px-4 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-colors border border-slate-200"
          >
            <MessageSquare className="w-4 h-4 text-teal-700" />
            <span>{language === 'hi' ? 'इस योजना पर चैट करें' : 'Ask Bot About This Scheme'}</span>
          </button>

          <button
            onClick={() => setCurrentScreen('S6')}
            className="flex-1 sm:flex-none px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all shadow-xs"
          >
            <FileText className="w-4 h-4 text-teal-400" />
            <span>{t('get_checklist')}</span>
          </button>
>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
        </div>
      </div>
    </div>
  );
}
<<<<<<< HEAD
=======

>>>>>>> 0c8519a438a18c035174e0639c3e7be376f5f48f
