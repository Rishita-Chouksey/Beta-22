import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
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
  AlertTriangle
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S4_ResultsScreen() {
  const { language, t } = useLanguage();
  const {
    evaluationResults,
    setCurrentScreen,
    setActiveSchemeModal,
  } = useSession();

  const [activeTab, setActiveTab] = useState('eligible');

  const eligibleSchemes = evaluationResults?.eligible || [];
  const notSureSchemes = evaluationResults?.not_sure || [];
  const notEligibleSchemes = evaluationResults?.not_eligible || [];
  const noRulesSchemes = evaluationResults?.no_rules || [];
  const contradictions = evaluationResults?.contradictions || [];

  const handleOpenDetails = (schemeResult) => {
    setActiveSchemeModal(schemeResult);
  };

  const handleGenerateChecklist = () => {
    setCurrentScreen('S6');
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

        {/* Profile Inconsistency / Contradiction Banner (Requirement 7) */}
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'eligible'
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'not_sure'
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'not_eligible'
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
            className={`flex-1 min-w-[130px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'no_rules'
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
                          {scheme.category}
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

                    {/* Satisfied / Unknown / Failed Conditions Breakdown (Requirement 6) */}
                    <div className="space-y-2 pt-1 border-t border-slate-100 text-xs">
                      {scheme.satisfied_conditions && scheme.satisfied_conditions.length > 0 && (
                        <div className="space-y-1">
                          <span className="font-bold text-emerald-800 text-[11px] block">
                            ✓ {t('satisfied_conditions_label')}:
                          </span>
                          <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                            {scheme.satisfied_conditions.map((sc, sIdx) => (
                              <li key={sIdx}>{sc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {scheme.unknown_conditions && scheme.unknown_conditions.length > 0 && (
                        <div className="space-y-1">
                          <span className="font-bold text-amber-800 text-[11px] block">
                            ? {t('unknown_conditions_label')}:
                          </span>
                          <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                            {scheme.unknown_conditions.map((uc, uIdx) => (
                              <li key={uIdx}>{uc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {scheme.failed_conditions && scheme.failed_conditions.length > 0 && (
                        <div className="space-y-1">
                          <span className="font-bold text-rose-800 text-[11px] block">
                            ✗ {t('failed_conditions_label')}:
                          </span>
                          <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
                            {scheme.failed_conditions.map((fc, fIdx) => (
                              <li key={fIdx}>{fc}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
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
