import React, { useState, useMemo } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { evaluateCitizenProfile } from '../services/api';
import questionsData from '../data/questions.json';
import {
  CheckCircle,
  HelpCircle,
  XCircle,
  FileText,
  ExternalLink,
  ChevronRight,
  Calendar,
  AlertCircle,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Building2,
  AlertTriangle,
  ArrowRight,
  Check,
  Zap
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S4_ResultsScreen() {
  const { language, t } = useLanguage();
  const {
    evaluationResults,
    setEvaluationResults,
    setCurrentScreen,
    setActiveSchemeModal,
    profile,
    updateProfile
  } = useSession();

  const [activeTab, setActiveTab] = useState('eligible');
  const [missingAnswers, setMissingAnswers] = useState({});
  const [isProcessingVerification, setIsProcessingVerification] = useState(false);
  const [verificationSuccessMsg, setVerificationSuccessMsg] = useState(null);

  const eligibleSchemes = evaluationResults?.eligible || [];
  const notSureSchemes = evaluationResults?.not_sure || [];
  const notEligibleSchemes = evaluationResults?.not_eligible || [];
  const noRulesSchemes = evaluationResults?.no_rules || [];
  const contradictions = evaluationResults?.contradictions || [];

  // Map question registry by field name
  const questionsMap = useMemo(() => {
    const map = {};
    (questionsData.questions || []).forEach((q) => {
      map[q.field] = q;
    });
    return map;
  }, []);

  // Compute unique unknown/missing fields for the "Needs Verification" category
  const unverifiedMissingFields = useMemo(() => {
    const fieldsSet = new Set();
    notSureSchemes.forEach((s) => {
      (s.missing_fields || []).forEach((f) => {
        // Exclude internal flags and exclude fields that citizen already has an explicit answer for
        if (
          !['holds_constitutional_post', 'is_institutional_landholder', 'confirmed_fields', 'skipped_fields'].includes(f) &&
          (profile[f] === undefined || profile[f] === null || profile[f] === '')
        ) {
          fieldsSet.add(f);
        }
      });
    });
    return Array.from(fieldsSet);
  }, [notSureSchemes, profile]);

  const handleOpenDetails = (schemeResult) => {
    setActiveSchemeModal(schemeResult);
    setCurrentScreen('S5');
  };

  const handleGenerateChecklist = () => {
    setCurrentScreen('S6');
  };

  const handleAnswerChange = (field, val) => {
    setMissingAnswers((prev) => ({
      ...prev,
      [field]: val
    }));
  };

  const handleProcessMissingAnswers = async (e) => {
    e?.preventDefault();
    if (Object.keys(missingAnswers).length === 0) return;

    setIsProcessingVerification(true);
    setVerificationSuccessMsg(null);

    try {
      const updatedProfile = {
        ...profile,
        ...missingAnswers,
        confirmed_fields: Array.from(
          new Set([...(profile.confirmed_fields || []), ...Object.keys(missingAnswers)])
        )
      };

      // 1. Update session profile
      updateProfile(updatedProfile);

      // 2. Deterministically re-evaluate all schemes with newly confirmed attributes
      const newEval = await evaluateCitizenProfile(updatedProfile);
      setEvaluationResults(newEval);

      // Clear local answered staging
      setMissingAnswers({});

      const newlyEligibleCount = (newEval.eligible || []).length - eligibleSchemes.length;
      if (newlyEligibleCount > 0) {
        setVerificationSuccessMsg(
          language === 'hi'
            ? `🎉 सत्यापन पूर्ण! आपकी नई जानकारी से ${newlyEligibleCount} नई योजनाएं पात्रता सूची में जुड़ गई हैं!`
            : `🎉 Verification complete! ${newlyEligibleCount} additional scheme(s) confirmed as Eligible!`
        );
        setTimeout(() => setActiveTab('eligible'), 1500);
      } else {
        setVerificationSuccessMsg(
          language === 'hi'
            ? '✓ सत्यापन पूर्ण! आपकी दर्ज जानकारी के आधार पर सभी योजनाओं का अंतिम निर्णय ले लिया गया है।'
            : '✓ Verification complete! All unverified schemes have been definitively evaluated.'
        );
      }
    } catch (err) {
      console.error('Error processing verification answers:', err);
    } finally {
      setIsProcessingVerification(false);
    }
  };

  const getActiveList = () => {
    switch (activeTab) {
      case 'eligible':
        return eligibleSchemes;
      case 'not_sure':
        return notSureSchemes;
      case 'not_eligible':
        return notEligibleSchemes;
      case 'no_rules':
        return noRulesSchemes;
      default:
        return eligibleSchemes;
    }
  };

  const activeList = getActiveList();

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ELIGIBLE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>{language === 'hi' ? 'संभावित पात्र (Likely Eligible)' : 'Likely Eligible'}</span>
          </span>
        );
      case 'NOT SURE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300">
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>{language === 'hi' ? 'सत्यापन आवश्यक (Needs Verification)' : 'Needs Verification'}</span>
          </span>
        );
      case 'NOT ELIGIBLE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-800 border border-rose-300">
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>{language === 'hi' ? 'अपात्र (Not Eligible)' : 'Not Eligible'}</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
            <AlertCircle className="w-3.5 h-3.5 text-slate-500" />
            <span>{language === 'hi' ? 'वर्तमान नियम उपलब्ध नहीं' : 'No Current Rules'}</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Header & Re-evaluate Control */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {t('results_title')}
              </h1>
              <AudioSpeaker
                text={
                  language === 'hi'
                    ? `आप ${eligibleSchemes.length} योजनाओं के लिए संभावित पात्र हैं, और ${notSureSchemes.length} योजनाओं में अतिरिक्त सत्यापन की आवश्यकता है।`
                    : `You are likely eligible for ${eligibleSchemes.length} schemes, with ${notSureSchemes.length} requiring further verification.`
                }
              />
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              {t('results_subtitle')}
            </p>
          </div>

          <button
            onClick={() => setCurrentScreen('S1')}
            className="self-start sm:self-auto inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors shadow-2xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-teal-700" />
            <span>{t('reevaluate_profile')}</span>
          </button>
        </div>

        {/* Profile Inconsistency / Contradiction Banner */}
        {contradictions.length > 0 && (
          <div className="bg-amber-50/90 border border-amber-300 rounded-2xl p-4 sm:p-5 space-y-2 shadow-xs">
            <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0" />
              <span>{t('contradiction_warning')}</span>
            </div>
            <div className="space-y-1.5 text-xs text-amber-950">
              {contradictions.map((c, idx) => (
                <p key={idx} className="leading-relaxed">
                  • {language === 'hi' ? c.warning_hi : c.warning_en}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Action Required: Checklist Banner */}
        {eligibleSchemes.length > 0 && (
          <div className="bg-gradient-to-r from-teal-800 to-slate-900 text-white rounded-2xl p-5 sm:p-6 shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-teal-500/30">
            <div className="space-y-1">
              <span className="inline-block text-[10px] font-bold tracking-wider uppercase bg-teal-900 px-2.5 py-0.5 rounded-full border border-teal-400/40 text-teal-200">
                {t('action_required')}
              </span>
              <h2 className="text-lg sm:text-xl font-bold">
                {t('qualify_banner_title').replace('{count}', eligibleSchemes.length)}
              </h2>
              <p className="text-xs sm:text-sm text-teal-100/90 max-w-xl leading-relaxed">
                {t('qualify_banner_desc')}
              </p>
            </div>

            <button
              onClick={handleGenerateChecklist}
              className="bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold px-5 py-3 rounded-xl text-xs sm:text-sm shadow-md transition-all flex items-center gap-2 whitespace-nowrap self-stretch sm:self-auto justify-center min-h-[44px]"
            >
              <FileText className="w-4 h-4 text-slate-950" />
              <span>{t('get_checklist')}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Tab Navigation Pill Bar */}
        <div className="flex items-center gap-1.5 p-1.5 bg-slate-200/80 rounded-xl overflow-x-auto">
          <button
            onClick={() => setActiveTab('eligible')}
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'eligible'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t('tab_eligible')}</span>
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full text-[10px] font-extrabold">
              {eligibleSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('not_sure')}
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'not_sure'
                ? 'bg-white text-amber-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>{t('tab_not_sure')}</span>
            <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[10px] font-extrabold">
              {notSureSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('not_eligible')}
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'not_eligible'
                ? 'bg-white text-rose-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>{t('tab_not_eligible')}</span>
            <span className="px-2 py-0.5 bg-rose-100 text-rose-800 rounded-full text-[10px] font-extrabold">
              {notEligibleSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('no_rules')}
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'no_rules'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('tab_no_rules')}</span>
            <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full text-[10px] font-extrabold">
              {noRulesSchemes.length}
            </span>
          </button>
        </div>

        {/* Verification Success Toast / Notification */}
        {verificationSuccessMsg && (
          <div className="bg-emerald-50 border border-emerald-300 text-emerald-950 p-4 rounded-2xl flex items-center justify-between text-xs sm:text-sm font-semibold shadow-xs animate-fade-in">
            <div className="flex items-center gap-2.5">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span>{verificationSuccessMsg}</span>
            </div>
            <button
              onClick={() => setVerificationSuccessMsg(null)}
              className="text-xs text-emerald-700 hover:underline cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* INTERACTIVE QUESTIONNAIRE FOR UNKNOWN INFORMATION (Requirement 1) */}
        {activeTab === 'not_sure' && unverifiedMissingFields.length > 0 && (
          <div className="bg-gradient-to-br from-amber-50 via-orange-50/50 to-white border-2 border-amber-300/90 rounded-3xl p-6 sm:p-7 shadow-md space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-200/80 pb-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-2xl bg-amber-500 text-white flex items-center justify-center flex-shrink-0 shadow-xs">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-extrabold uppercase tracking-wider bg-amber-200 text-amber-900 px-2.5 py-0.5 rounded-full">
                      {language === 'hi' ? 'अंतिम पात्रता निर्णय प्रश्नावली' : 'Definitive Decision Questionnaire'}
                    </span>
                    <span className="text-xs font-bold text-amber-800">
                      {unverifiedMissingFields.length} {language === 'hi' ? 'महत्वपूर्ण प्रश्न शेष' : 'Questions Required'}
                    </span>
                  </div>
                  <h2 className="text-base sm:text-lg font-extrabold text-slate-900 mt-1">
                    {language === 'hi'
                      ? 'अधूरी जानकारी दर्ज करें — अंतिम पात्रता परिणाम तुरंत जानें'
                      : 'Provide Unknown Information to Finalize Your Eligibility'}
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
                    {language === 'hi'
                      ? 'सत्यापन आवश्यक वाली योजनाओं के लिए केवल ये कुछ बिंदु स्पष्ट करें। हमारे नियम इंजन द्वारा तत्काल अंतिम निर्णय लिया जाएगा।'
                      : 'Answer these unconfirmed points to let YojnaSarthi definitively conclude whether you qualify for these schemes.'}
                  </p>
                </div>
              </div>
            </div>

            <form onSubmit={handleProcessMissingAnswers} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
                {unverifiedMissingFields.map((fieldKey) => {
                  const qDef = questionsMap[fieldKey];
                  if (!qDef) return null;

                  const qTitle = language === 'hi'
                    ? qDef.title_hi
                    : language === 'bn'
                    ? (qDef.title_bn || qDef.title_en)
                    : qDef.title_en;

                  const qSubtitle = language === 'hi'
                    ? qDef.subtitle_hi
                    : language === 'bn'
                    ? (qDef.subtitle_bn || qDef.subtitle_en)
                    : qDef.subtitle_en;

                  const currentVal = missingAnswers[fieldKey];

                  return (
                    <div
                      key={fieldKey}
                      className="bg-white border border-amber-200 rounded-2xl p-4 sm:p-5 shadow-2xs space-y-3.5 flex flex-col justify-between"
                    >
                      <div className="space-y-1">
                        <label className="text-xs sm:text-sm font-bold text-slate-900 leading-snug block">
                          {qTitle}
                        </label>
                        {qSubtitle && (
                          <p className="text-[11px] text-slate-500 leading-relaxed">
                            {qSubtitle}
                          </p>
                        )}
                      </div>

                      {/* Render input by type */}
                      {qDef.type === 'boolean' && (
                        <div className="grid grid-cols-2 gap-2 pt-1">
                          <button
                            type="button"
                            onClick={() => handleAnswerChange(fieldKey, true)}
                            className={`py-2.5 px-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                              currentVal === true
                                ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                            }`}
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>
                              {language === 'hi' ? 'हाँ (Yes)' : language === 'bn' ? 'হ্যাঁ (Yes)' : 'Yes'}
                            </span>
                          </button>

                          <button
                            type="button"
                            onClick={() => handleAnswerChange(fieldKey, false)}
                            className={`py-2.5 px-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                              currentVal === false
                                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                            }`}
                          >
                            <span>✕</span>
                            <span>
                              {language === 'hi' ? 'नहीं (No)' : language === 'bn' ? 'না (No)' : 'No'}
                            </span>
                          </button>
                        </div>
                      )}

                      {qDef.type === 'single_choice' && qDef.options && (
                        <div className="space-y-1.5 pt-1">
                          {qDef.options.map((opt, oIdx) => {
                            const optLabel = language === 'hi'
                              ? opt.label_hi
                              : language === 'bn'
                              ? (opt.label_bn || opt.label_en)
                              : opt.label_en;
                            const isSelected = currentVal === opt.value;

                            return (
                              <button
                                key={oIdx}
                                type="button"
                                onClick={() => handleAnswerChange(fieldKey, opt.value)}
                                className={`w-full text-left p-2.5 rounded-xl border text-xs font-medium transition-all flex items-center justify-between cursor-pointer ${
                                  isSelected
                                    ? 'bg-blue-50 border-blue-600 text-blue-900 font-bold shadow-2xs'
                                    : 'bg-slate-50/70 border-slate-200 text-slate-700 hover:bg-slate-100'
                                }`}
                              >
                                <span>{optLabel}</span>
                                {isSelected && <Check className="w-4 h-4 text-blue-700" />}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {qDef.type === 'number' && (
                        <div className="relative pt-1">
                          <input
                            type="number"
                            min={qDef.min_val ?? 0}
                            max={qDef.max_val ?? 10000000}
                            value={currentVal !== undefined ? currentVal : ''}
                            onChange={(e) => handleAnswerChange(fieldKey, e.target.value === '' ? null : Number(e.target.value))}
                            placeholder={`e.g. ${qDef.min_val ?? 0}`}
                            className="w-full text-xs sm:text-sm p-3 rounded-xl border border-slate-300 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 focus:outline-hidden bg-white"
                          />
                          {qDef.unit && (
                            <span className="absolute right-3 top-3.5 text-xs font-semibold text-slate-400">
                              {qDef.unit}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                <span className="text-xs text-slate-500">
                  {Object.keys(missingAnswers).length} / {unverifiedMissingFields.length}{' '}
                  {language === 'hi' ? 'उत्तर दर्ज किए गए' : 'questions answered'}
                </span>

                <button
                  type="submit"
                  disabled={isProcessingVerification || Object.keys(missingAnswers).length === 0}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer min-h-[44px]"
                >
                  <Sparkles className="w-4 h-4 text-teal-400" />
                  <span>
                    {isProcessingVerification
                      ? (language === 'hi' ? 'पात्रता जाँची जा रही है...' : 'Evaluating Rules...')
                      : (language === 'hi' ? 'जानकारी सत्यापित करें व अंतिम पात्रता देखें' : 'Process Information & Decide Eligibility')}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Scheme Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {activeList.length === 0 ? (
            <div className="col-span-full text-center py-12 bg-white border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
              <div className="text-3xl">📋</div>
              <p className="text-sm font-semibold text-slate-600">
                {t('no_schemes_in_category')}
              </p>
            </div>
          ) : (
            activeList.map((scheme) => {
              const name = language === 'hi' ? scheme.scheme_name_hi : scheme.scheme_name_en;
              const reason = language === 'hi' ? scheme.deciding_reason_hi : scheme.deciding_reason_en;
              const benefit = language === 'hi' ? scheme.benefit_hi : scheme.benefit_en;

              return (
                <div
                  key={scheme.scheme_id}
                  className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-xs hover:shadow-md hover:border-teal-400 transition-all flex flex-col justify-between gap-4"
                >
                  <div className="space-y-3.5">
                    {/* Header tags & status badge */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                          {scheme.level === 'central' ? t('central_scheme') : t('state_scheme')}
                        </span>
                        <span className="text-xs font-semibold text-slate-500">
                          {language === 'hi' ? (scheme.category_hi || scheme.category) : scheme.category}
                        </span>
                      </div>

                      {getStatusBadge(scheme.status)}
                    </div>

                    {/* Scheme Name */}
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                      {name}
                    </h3>

                    {/* Benefit Highlight */}
                    <div className="bg-teal-50/60 border border-teal-100 rounded-xl p-3 text-xs sm:text-sm text-teal-950 font-medium leading-relaxed">
                      💰 {benefit}
                    </div>

                    {/* Deciding Reason Box */}
                    <div className="space-y-1.5 text-xs text-slate-700 bg-slate-50 border border-slate-100 p-3 rounded-xl">
                      <p className="font-semibold text-slate-900">
                        {scheme.status === 'ELIGIBLE' && '✓ ' + (language === 'hi' ? 'पात्रता कारण: ' : 'Why recommended: ')}
                        {scheme.status === 'NOT ELIGIBLE' && '✗ ' + (language === 'hi' ? 'अपात्रता कारण: ' : 'Reason not eligible: ')}
                        {scheme.status === 'NOT SURE' && '? ' + (language === 'hi' ? 'सत्यापन कारण: ' : 'Verification required: ')}
                        {scheme.status === 'NO CURRENT RULES' && '! ' + (language === 'hi' ? 'असत्यापित: ' : 'Unverified: ')}
                        <span className="font-normal text-slate-700">{reason}</span>
                      </p>
                    </div>

                    {/* Satisfied / Unknown / Failed Conditions Breakdown */}
                    {(() => {
                      const satList = language === 'hi' ? (scheme.satisfied_conditions_hi || scheme.satisfied_conditions) : (scheme.satisfied_conditions_en || scheme.satisfied_conditions);
                      const unkList = language === 'hi' ? (scheme.unknown_conditions_hi || scheme.unknown_conditions) : (scheme.unknown_conditions_en || scheme.unknown_conditions);
                      const failList = language === 'hi' ? (scheme.failed_conditions_hi || scheme.failed_conditions) : (scheme.failed_conditions_en || scheme.failed_conditions);

                      return (
                        <div className="space-y-2 pt-1 border-t border-slate-100 text-xs">
                          {satList && satList.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-bold text-emerald-800 text-[11px] block">
                                ✓ {t('satisfied_conditions_label')}:
                              </span>
                              <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                                {satList.map((sc, sIdx) => (
                                  <li key={sIdx}>{sc}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {unkList && unkList.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-bold text-amber-800 text-[11px] block">
                                ? {t('unknown_conditions_label')}:
                              </span>
                              <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                                {unkList.map((uc, uIdx) => (
                                  <li key={uIdx}>{uc}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {failList && failList.length > 0 && (
                            <div className="space-y-1">
                              <span className="font-bold text-rose-800 text-[11px] block">
                                ✗ {t('failed_conditions_label')}:
                              </span>
                              <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                                {failList.map((fc, fIdx) => (
                                  <li key={fIdx}>{fc}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </div>

                  {/* Card Footer: Metadata and Action Button */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3 text-xs flex-wrap">
                    <div className="flex items-center gap-3 text-slate-500">
                      <span className="flex items-center gap-1 font-medium text-[11px]">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span>{t('verified_on')}: {scheme.last_verified_date}</span>
                      </span>

                      {scheme.official_source_url && (
                        <a
                          href={scheme.official_source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-teal-700 hover:text-teal-900 inline-flex items-center gap-1 font-semibold hover:underline text-[11px]"
                        >
                          <span>{t('official_source')}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>

                    <button
                      onClick={() => handleOpenDetails(scheme)}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition-colors inline-flex items-center gap-1 shadow-2xs"
                    >
                      <span>{t('view_details')}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
