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
  Building2
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S4_ResultsScreen() {
  const { language, t } = useLanguage();
  const {
    evaluationResults,
    setCurrentScreen,
    setActiveSchemeModal,
  } = useSession();

  const [activeTab, setActiveTab] = useState('eligible'); // 'eligible', 'not_sure', 'not_eligible', 'no_rules'

  const eligibleSchemes = evaluationResults?.eligible || [];
  const notSureSchemes = evaluationResults?.not_sure || [];
  const notEligibleSchemes = evaluationResults?.not_eligible || [];
  const noRulesSchemes = evaluationResults?.no_rules || [];

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

  return (
    <div className="space-y-8 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Header & Stats Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {t('results_title')}
              </h1>
              <AudioSpeaker
                text={
                  language === 'hi'
                    ? `आप ${eligibleSchemes.length} योजनाओं के लिए पात्र हैं, और ${notSureSchemes.length} योजनाओं में अतिरिक्त सत्यापन की आवश्यकता है।`
                    : `You are eligible for ${eligibleSchemes.length} schemes, with ${notSureSchemes.length} requiring further verification.`
                }
              />
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              {t('results_subtitle')}
            </p>
          </div>

          <button
            onClick={() => setCurrentScreen('S1')}
            className="self-start sm:self-auto inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{language === 'hi' ? 'पुनः जांचें (Re-evaluate)' : 'Re-evaluate Profile'}</span>
          </button>
        </div>

        {/* Highlight Checklist Banner if Eligible schemes exist */}
        {eligibleSchemes.length > 0 && (
          <div className="bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-2xl p-5 sm:p-6 shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="inline-block text-[10px] font-bold tracking-wider uppercase bg-emerald-800/80 px-2.5 py-0.5 rounded-full border border-emerald-400/30">
                Action Required
              </span>
              <h2 className="text-lg sm:text-xl font-bold">
                {language === 'hi'
                  ? `बधाई! आप ${eligibleSchemes.length} सरकारी योजनाओं के लिए पात्र पाए गए हैं`
                  : `You Qualify for ${eligibleSchemes.length} Government Schemes`}
              </h2>
              <p className="text-xs sm:text-sm text-emerald-100 max-w-xl leading-relaxed">
                {language === 'hi'
                  ? 'सभी योजनाओं के लिए आवश्यक दस्तावेज़ों की एकीकृत सूची तैयार है। इसे अभी देखें या पीडीएफ प्रिंट करें।'
                  : 'A consolidated, de-duplicated document checklist has been prepared. Review required proofs and print or save as PDF.'}
              </p>
            </div>

            <button
              onClick={handleGenerateChecklist}
              className="bg-white hover:bg-emerald-50 text-emerald-900 font-bold px-5 py-3 rounded-xl text-xs sm:text-sm shadow-sm transition-all flex items-center gap-2 whitespace-nowrap self-stretch sm:self-auto justify-center min-h-[44px]"
            >
              <FileText className="w-4 h-4 text-emerald-700" />
              <span>{t('get_checklist')}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Tab Navigation Pill Bar */}
        <div className="flex items-center gap-1.5 p-1.5 bg-slate-200/80 rounded-xl overflow-x-auto">
          <button
            onClick={() => setActiveTab('eligible')}
            className={`flex-1 min-w-[120px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'eligible'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>{language === 'hi' ? 'पात्र (Eligible)' : 'Likely Eligible'}</span>
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full text-[10px] font-extrabold">
              {eligibleSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('not_sure')}
            className={`flex-1 min-w-[120px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'not_sure'
                ? 'bg-white text-amber-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>{language === 'hi' ? 'सत्यापन आवश्यक' : 'Needs Verification'}</span>
            <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[10px] font-extrabold">
              {notSureSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('not_eligible')}
            className={`flex-1 min-w-[120px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'not_eligible'
                ? 'bg-white text-rose-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>{language === 'hi' ? 'अपात्र (Ineligible)' : 'Not Eligible'}</span>
            <span className="px-2 py-0.5 bg-rose-100 text-rose-800 rounded-full text-[10px] font-extrabold">
              {notEligibleSchemes.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('no_rules')}
            className={`flex-1 min-w-[120px] py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'no_rules'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5 text-slate-500" />
            <span>{language === 'hi' ? 'असत्यापित' : 'No Rules'}</span>
            <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full text-[10px] font-extrabold">
              {noRulesSchemes.length}
            </span>
          </button>
        </div>

        {/* Scheme Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {activeList.length === 0 ? (
            <div className="col-span-full text-center py-12 bg-white border border-slate-200 rounded-2xl space-y-2">
              <div className="text-3xl">📋</div>
              <p className="text-sm font-semibold text-slate-600">
                {language === 'hi' ? 'इस श्रेणी में कोई योजना नहीं है।' : 'No schemes match this category.'}
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
                  className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-blue-300 transition-all flex flex-col justify-between gap-4"
                >
                  <div className="space-y-3">
                    {/* Level & Status Pill */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                          {scheme.level === 'central' ? 'केंद्रीय (Central)' : 'राज्य (State)'}
                        </span>
                        <span className="text-xs font-semibold text-slate-500">
                          {scheme.category}
                        </span>
                      </div>

                      {/* Status Badge */}
                      <div>
                        {scheme.status === 'ELIGIBLE' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                            <span>पात्र (Eligible)</span>
                          </span>
                        )}
                        {scheme.status === 'NOT SURE' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-200">
                            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                            <span>सत्यापन आवश्यक</span>
                          </span>
                        )}
                        {scheme.status === 'NOT ELIGIBLE' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-800 border border-rose-200">
                            <XCircle className="w-3.5 h-3.5 text-rose-600" />
                            <span>अपात्र (Ineligible)</span>
                          </span>
                        )}
                        {scheme.status === 'NO CURRENT RULES' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
                            <AlertCircle className="w-3.5 h-3.5 text-slate-500" />
                            <span>असत्यापित</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Scheme Name */}
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                      {name}
                    </h3>

                    {/* Benefit Box */}
                    <div className="bg-emerald-50/70 border border-emerald-100 rounded-xl p-3 text-xs sm:text-sm font-semibold text-emerald-950 leading-relaxed">
                      💰 {benefit}
                    </div>

                    {/* Deciding Reason Box */}
                    <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-xs text-slate-700 leading-relaxed">
                      <span className="font-bold text-slate-900">
                        {language === 'hi' ? 'निर्णय का कारण: ' : 'Deciding Reason: '}
                      </span>
                      <span>{reason}</span>
                    </div>

                    {/* Missing information warning if any */}
                    {scheme.missing_fields && scheme.missing_fields.length > 0 && (
                      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-900 flex items-start gap-2">
                        <HelpCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold">
                            {language === 'hi' ? 'अपेक्षित अतिरिक्त जानकारी: ' : 'Required to Verify: '}
                          </span>
                          <span>{scheme.missing_fields.join(', ')}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Card Footer: Verified date & Details Button */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      <span>{t('verified_on')}: {scheme.last_verified_date}</span>
                    </span>

                    <button
                      onClick={() => handleOpenDetails(scheme)}
                      className="inline-flex items-center gap-1 text-xs font-bold text-blue-700 hover:text-blue-900 py-1.5 px-3 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <span>{t('view_details')}</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Footer Checklist Action Bar */}
      <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
        <button
          onClick={handleGenerateChecklist}
          disabled={eligibleSchemes.length === 0 && notSureSchemes.length === 0}
          className="w-full sm:w-auto px-8 py-3.5 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 min-h-[48px]"
        >
          <FileText className="w-4 h-4" />
          <span>{t('get_checklist')}</span>
        </button>

        <span className="text-xs text-slate-500 text-center sm:text-right">
          {language === 'hi'
            ? 'दस्तावेज़ चेकलिस्ट में सभी आवश्यक प्रमाण पत्रों की समेकित सूची उपलब्ध है।'
            : 'Checklist consolidates all documents across schemes without duplicate requests.'}
        </span>
      </div>
    </div>
  );
}
