import React, { useState, useMemo } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import VerificationQuestionnaire from '../components/VerificationQuestionnaire';
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
  Eye
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
  const [showBatchVerification, setShowBatchVerification] = useState(false);
  const [activeInlineVerifySchemeId, setActiveInlineVerifySchemeId] = useState(null);
  const [recentResolutionNotice, setRecentResolutionNotice] = useState(null);

  const eligibleSchemes = evaluationResults?.eligible || [];
  const notSureSchemes = evaluationResults?.not_sure || [];
  const notEligibleSchemes = evaluationResults?.not_eligible || [];
  const noRulesSchemes = evaluationResults?.no_rules || [];
  const contradictions = evaluationResults?.contradictions || [];

  // Gather all unique missing fields across all not_sure schemes
  const allMissingFields = Array.from(
    new Set(notSureSchemes.flatMap((s) => s.missing_fields || []))
  );

  // Navigate to complete full-page view for the scheme
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
            className="self-start sm:self-auto inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors shadow-2xs cursor-pointer"
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

        {/* Verification Success Toast Notification */}
        {recentResolutionNotice && (
          <div className="bg-emerald-50 border-2 border-emerald-400 rounded-2xl p-4 sm:p-5 flex items-center justify-between gap-3 shadow-sm animate-fade-in">
            <div className="flex items-center gap-2.5">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <p className="text-xs sm:text-sm font-bold text-emerald-950">
                {recentResolutionNotice}
              </p>
            </div>
            <button
              onClick={() => setActiveTab('eligible')}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl transition whitespace-nowrap cursor-pointer"
            >
              {language === 'hi' ? 'पात्र योजनाएं देखें →' : 'View Eligible Schemes →'}
            </button>
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
              className="bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold px-5 py-3 rounded-xl text-xs sm:text-sm shadow-md transition-all flex items-center gap-2 whitespace-nowrap self-stretch sm:self-auto justify-center min-h-[44px] cursor-pointer"
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
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

        {/* 1. Interactive Verification Questionnaire Callout (for "Needs Verification" Tab) */}
        {activeTab === 'not_sure' && notSureSchemes.length > 0 && allMissingFields.length > 0 && (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-amber-500/15 via-amber-100/40 to-amber-50 border-2 border-amber-300 rounded-2xl p-5 sm:p-6 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-200 text-amber-900 border border-amber-400">
                    ⚡ {language === 'hi' ? 'पात्रता सत्यापन' : 'Action Needed'}
                  </span>
                  <span className="text-xs font-bold text-amber-900">
                    {notSureSchemes.length} {language === 'hi' ? 'योजनाएं सत्यापन की प्रतीक्षा में' : 'schemes pending verification'}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">
                  {language === 'hi'
                    ? 'अधूरी जानकारी की सत्यापन प्रश्नावली भरें'
                    : 'Complete Verification Questionnaire for Pending Schemes'}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
                  {language === 'hi'
                    ? `आपके द्वारा ${allMissingFields.length} विवरण उपलब्ध कराने पर हमारा नियम इंजन तुरंत तय कर देगा कि आप इन योजनाओं के लिए पात्र हैं या नहीं।`
                    : `Answering ${allMissingFields.length} missing questions will allow the deterministic rule engine to finalize eligibility for all pending schemes.`}
                </p>
              </div>

              <button
                onClick={() => setShowBatchVerification((prev) => !prev)}
                className="w-full sm:w-auto px-5 py-3 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-sm transition flex items-center justify-center gap-2 cursor-pointer whitespace-nowrap min-h-[44px]"
              >
                <Sparkles className="w-4 h-4" />
                <span>
                  {showBatchVerification
                    ? (language === 'hi' ? 'प्रश्नावली बंद करें' : 'Hide Questionnaire')
                    : (language === 'hi' ? 'प्रश्नावली शुरू करें (अभी सत्यापित करें)' : 'Start Verification Questionnaire')}
                </span>
              </button>
            </div>

            {/* Batch Verification Questionnaire Container */}
            {showBatchVerification && (
              <VerificationQuestionnaire
                missingFields={allMissingFields}
                onComplete={() => {
                  setShowBatchVerification(false);
                  setRecentResolutionNotice(
                    language === 'hi'
                      ? 'सत्यापन पूर्ण! नियम इंजन द्वारा आपकी अंतिम पात्रता निर्धारित कर दी गई है।'
                      : 'Verification complete! Your definitive eligibility has been computed.'
                  );
                }}
                onCancel={() => setShowBatchVerification(false)}
              />
            )}
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
              const isInlineVerifying = activeInlineVerifySchemeId === scheme.scheme_id;
              const schemeMissingFields = scheme.missing_fields || [];

              return (
                <div
                  key={scheme.scheme_id}
                  className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-xs hover:shadow-md hover:border-teal-400 transition-all flex flex-col justify-between gap-4 cursor-pointer"
                  onClick={() => handleOpenDetails(scheme)}
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
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug hover:text-teal-700 transition">
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

                    {/* Conditions Breakdown Preview */}
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
                                {satList.slice(0, 3).map((sc, sIdx) => (
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

                    {/* Scheme-Specific Inline Verification Questionnaire */}
                    {isInlineVerifying && schemeMissingFields.length > 0 && (
                      <div
                        className="pt-2"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <VerificationQuestionnaire
                          missingFields={schemeMissingFields}
                          targetSchemeId={scheme.scheme_id}
                          targetSchemeName={name}
                          onComplete={() => {
                            setActiveInlineVerifySchemeId(null);
                            setRecentResolutionNotice(
                              language === 'hi'
                                ? `${name} की पात्रता निर्धारित हो गई है!`
                                : `Eligibility for ${name} has been evaluated!`
                            );
                          }}
                          onCancel={() => setActiveInlineVerifySchemeId(null)}
                        />
                      </div>
                    )}
                  </div>

                  {/* Card Footer: Metadata and Action Buttons */}
                  <div
                    className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3 text-xs flex-wrap"
                    onClick={(e) => e.stopPropagation()}
                  >
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

                    <div className="flex items-center gap-2">
                      {/* If in NOT SURE: Show instant verify button */}
                      {scheme.status === 'NOT SURE' && schemeMissingFields.length > 0 && (
                        <button
                          type="button"
                          onClick={() => setActiveInlineVerifySchemeId(isInlineVerifying ? null : scheme.scheme_id)}
                          className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs transition inline-flex items-center gap-1 shadow-2xs cursor-pointer"
                        >
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>
                            {isInlineVerifying
                              ? (language === 'hi' ? 'बंद करें' : 'Close')
                              : (language === 'hi' ? 'सत्यापित करें' : 'Verify Now')}
                          </span>
                        </button>
                      )}

                      {/* Complete Full-Page View Button */}
                      <button
                        type="button"
                        onClick={() => handleOpenDetails(scheme)}
                        className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition inline-flex items-center gap-1 shadow-2xs cursor-pointer"
                      >
                        <span>{t('view_details')}</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
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
