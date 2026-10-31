import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { evaluateCitizenProfile } from '../services/api';
import { getFieldQuestion } from '../services/questionRegistry';
import {
  HelpCircle,
  CheckCircle,
  XCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Check,
  RefreshCw,
  X
} from 'lucide-react';

export default function VerificationQuestionnaire({
  missingFields = [],
  targetSchemeName = null,
  targetSchemeId = null,
  onComplete = null,
  onCancel = null,
  compact = false
}) {
  const { language, t } = useLanguage();
  const { profile, updateProfile, setEvaluationResults } = useSession();

  // Initialize answers from current profile if any
  const [answers, setAnswers] = useState(() => {
    const init = {};
    missingFields.forEach((field) => {
      const val = profile[field];
      if (val !== undefined && val !== null) {
        init[field] = val;
      }
    });
    return init;
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successInfo, setSuccessInfo] = useState(null);

  const handleValueChange = (field, value) => {
    setAnswers((prev) => ({
      ...prev,
      [field]: value,
    }));
    setErrorMsg('');
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();

    // Verify at least one field has an answer
    const answeredCount = Object.keys(answers).filter((k) => answers[k] !== undefined && answers[k] !== '').length;
    if (answeredCount === 0) {
      setErrorMsg(
        language === 'hi'
          ? 'कृपया पात्रता तय करने के लिए कम से कम एक जानकारी दर्ज करें।'
          : 'Please answer at least one question to evaluate eligibility.'
      );
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const confirmedList = Array.from(
        new Set([...(profile.confirmed_fields || []), ...Object.keys(answers)])
      );
      const cleanSkipped = (profile.skipped_fields || []).filter((f) => !Object.keys(answers).includes(f));

      const updatedProfile = {
        ...profile,
        ...answers,
        confirmed_fields: confirmedList,
        skipped_fields: cleanSkipped,
      };

      // 1. Update in-memory session profile
      updateProfile(updatedProfile);

      // 2. Call deterministic rule engine evaluation
      const newResults = await evaluateCitizenProfile(updatedProfile);
      setEvaluationResults(newResults);

      // 3. Find target scheme verdict if targetSchemeId provided
      let finalStatus = null;
      let targetSchemeObj = null;
      if (targetSchemeId) {
        targetSchemeObj = (newResults.eligible || []).find((s) => s.scheme_id === targetSchemeId);
        if (targetSchemeObj) {
          finalStatus = 'ELIGIBLE';
        } else {
          targetSchemeObj = (newResults.not_eligible || []).find((s) => s.scheme_id === targetSchemeId);
          if (targetSchemeObj) {
            finalStatus = 'NOT ELIGIBLE';
          } else {
            targetSchemeObj = (newResults.not_sure || []).find((s) => s.scheme_id === targetSchemeId);
            finalStatus = targetSchemeObj ? 'NOT SURE' : 'EVALUATED';
          }
        }
      }

      setSuccessInfo({
        status: finalStatus,
        scheme: targetSchemeObj,
        eligibleCount: (newResults.eligible || []).length,
        notEligibleCount: (newResults.not_eligible || []).length,
        remainingNotSure: (newResults.not_sure || []).length,
      });

      if (onComplete) {
        onComplete(newResults, answers, finalStatus);
      }
    } catch (err) {
      console.error('Verification evaluation error:', err);
      setErrorMsg(
        language === 'hi'
          ? 'सत्यापन गणना में त्रुटि हुई। कृपया पुनः प्रयास करें।'
          : 'Error occurred during deterministic rule evaluation. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // If already submitted and finalized, display verdict
  if (successInfo) {
    const isNowEligible = successInfo.status === 'ELIGIBLE';
    const isNowNotEligible = successInfo.status === 'NOT ELIGIBLE';

    return (
      <div className="bg-white border-2 border-emerald-400 rounded-2xl p-5 sm:p-6 space-y-4 shadow-md animate-fade-in">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-base sm:text-lg font-bold text-slate-900">
              {language === 'hi'
                ? 'सत्यापन पूर्ण! अंतिम निर्णय प्राप्त हो गया है।'
                : 'Verification Complete! Final Decision Calculated.'}
            </h3>
            <p className="text-xs sm:text-sm text-slate-600">
              {language === 'hi'
                ? 'आपकी दर्ज की गई जानकारी को ऑडिटेड नियम इंजन द्वारा सत्यापित कर लिया गया है।'
                : 'Your confirmed answers have been evaluated with deterministic certainty.'}
            </p>
          </div>
        </div>

        {targetSchemeName && (
          <div
            className={`p-4 rounded-xl border ${
              isNowEligible
                ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
                : isNowNotEligible
                ? 'bg-rose-50 border-rose-300 text-rose-950'
                : 'bg-amber-50 border-amber-300 text-amber-950'
            }`}
          >
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <span className="font-bold text-sm sm:text-base">{targetSchemeName}</span>
              <span
                className={`text-xs font-extrabold px-3 py-1 rounded-full border ${
                  isNowEligible
                    ? 'bg-emerald-200 text-emerald-900 border-emerald-400'
                    : isNowNotEligible
                    ? 'bg-rose-200 text-rose-900 border-rose-400'
                    : 'bg-amber-200 text-amber-900 border-amber-400'
                }`}
              >
                {isNowEligible && (language === 'hi' ? '✓ संभावित पात्र (Likely Eligible)' : 'Likely Eligible')}
                {isNowNotEligible && (language === 'hi' ? '✗ अपात्र (Not Eligible)' : 'Not Eligible')}
                {!isNowEligible && !isNowNotEligible && (language === 'hi' ? 'सत्यापन प्रगति पर' : 'In Progress')}
              </span>
            </div>
            {successInfo.scheme && (
              <p className="text-xs mt-2 leading-relaxed opacity-90">
                {language === 'hi'
                  ? successInfo.scheme.deciding_reason_hi
                  : successInfo.scheme.deciding_reason_en}
              </p>
            )}
          </div>
        )}

        <div className="flex items-center justify-between gap-3 pt-2">
          <div className="text-xs text-slate-500">
            {language === 'hi'
              ? `कुल पात्र योजनाएं: ${successInfo.eligibleCount} | शेष सत्यापन: ${successInfo.remainingNotSure}`
              : `Total eligible: ${successInfo.eligibleCount} | Pending verification: ${successInfo.remainingNotSure}`}
          </div>
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition"
            >
              {language === 'hi' ? 'बंद करें (Close)' : 'Done'}
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-amber-50/70 border-2 border-amber-300/90 rounded-2xl p-5 sm:p-6 space-y-5 shadow-xs animate-fade-in">
      {/* Questionnaire Header */}
      <div className="flex items-start justify-between gap-3 border-b border-amber-200/80 pb-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-amber-200 text-amber-950 border border-amber-400">
              <HelpCircle className="w-3.5 h-3.5 text-amber-800" />
              <span>
                {language === 'hi' ? 'सत्यापन प्रश्नावली' : 'Verification Questionnaire'}
              </span>
            </span>
            <span className="text-xs text-amber-900 font-semibold">
              {missingFields.length} {language === 'hi' ? 'अधूरी जानकारी' : 'Missing Information'}
            </span>
          </div>

          <h3 className="text-base sm:text-lg font-bold text-slate-900">
            {targetSchemeName
              ? (language === 'hi'
                  ? `${targetSchemeName} की अंतिम पात्रता हेतु आवश्यक जानकारी`
                  : `Complete Information for ${targetSchemeName}`)
              : (language === 'hi'
                  ? 'योजनाओं की अंतिम पात्रता निश्चित करने के लिए जानकारी दर्ज करें'
                  : 'Answer Unknown Questions to Finalize Eligibility')}
          </h3>
          <p className="text-xs text-slate-600">
            {language === 'hi'
              ? 'ये विवरण भरते ही हमारा नियम इंजन तुरंत तय करेगा कि आप इस योजना के लिए पात्र हैं या नहीं।'
              : 'Providing these details allows our deterministic rule engine to compute an immediate definitive verdict.'}
          </p>
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-amber-100 transition"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Questions Stack */}
      <div className="space-y-5">
        {missingFields.map((field, idx) => {
          const q = getFieldQuestion(field, language);
          const currentVal = answers[field];

          return (
            <div
              key={field}
              className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 space-y-3 shadow-2xs"
            >
              <div className="flex items-start gap-2.5">
                <span className="w-6 h-6 rounded-full bg-teal-100 text-teal-900 text-xs font-extrabold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <h4 className="text-sm sm:text-base font-bold text-slate-900 leading-snug">
                    {q.title}
                  </h4>
                  {q.subtitle && (
                    <p className="text-xs text-slate-500 mt-0.5">{q.subtitle}</p>
                  )}
                </div>
              </div>

              {/* Render by Question Type */}
              {q.type === 'boolean' && (
                <div className="grid grid-cols-2 gap-3 pt-1">
                  {q.options && q.options.length > 0 ? (
                    q.options.map((opt) => {
                      const isSelected = currentVal === opt.value;
                      const optLabel = opt[`label_${language}`] || opt.label_hi || opt.label_en;
                      return (
                        <button
                          key={String(opt.value)}
                          type="button"
                          onClick={() => handleValueChange(field, opt.value)}
                          className={`p-3 rounded-xl border text-xs sm:text-sm font-bold text-left transition-all flex items-center justify-between gap-2 min-h-[44px] cursor-pointer ${
                            isSelected
                              ? 'bg-teal-50 border-teal-500 text-teal-950 ring-2 ring-teal-500/20 shadow-xs'
                              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300'
                          }`}
                        >
                          <span>{optLabel}</span>
                          {isSelected && <Check className="w-4 h-4 text-teal-600 flex-shrink-0" />}
                        </button>
                      );
                    })
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={() => handleValueChange(field, true)}
                        className={`p-3 rounded-xl border text-xs sm:text-sm font-bold text-center transition-all min-h-[44px] cursor-pointer ${
                          currentVal === true
                            ? 'bg-teal-50 border-teal-500 text-teal-950 ring-2 ring-teal-500/20 shadow-xs'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {language === 'hi' ? 'हाँ (Yes)' : 'Yes'}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleValueChange(field, false)}
                        className={`p-3 rounded-xl border text-xs sm:text-sm font-bold text-center transition-all min-h-[44px] cursor-pointer ${
                          currentVal === false
                            ? 'bg-teal-50 border-teal-500 text-teal-950 ring-2 ring-teal-500/20 shadow-xs'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {language === 'hi' ? 'नहीं (No)' : 'No'}
                      </button>
                    </>
                  )}
                </div>
              )}

              {q.type === 'single_choice' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                  {q.options.map((opt) => {
                    const isSelected = currentVal === opt.value;
                    const optLabel = opt[`label_${language}`] || opt.label_hi || opt.label_en;
                    return (
                      <button
                        key={String(opt.value)}
                        type="button"
                        onClick={() => handleValueChange(field, opt.value)}
                        className={`p-3 rounded-xl border text-xs sm:text-sm font-semibold text-left transition-all flex items-center justify-between gap-2 min-h-[44px] cursor-pointer ${
                          isSelected
                            ? 'bg-teal-50 border-teal-500 text-teal-950 ring-2 ring-teal-500/20 shadow-xs'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300'
                        }`}
                      >
                        <span>{optLabel}</span>
                        {isSelected && <Check className="w-4 h-4 text-teal-600 flex-shrink-0" />}
                      </button>
                    );
                  })}
                </div>
              )}

              {q.type === 'number' && (
                <div className="space-y-2.5 pt-1">
                  <div className="relative">
                    <input
                      type="number"
                      min={q.min || 0}
                      max={q.max || 9999999}
                      step="any"
                      placeholder={language === 'hi' ? 'संख्या दर्ज करें...' : 'Enter value...'}
                      value={currentVal !== undefined && currentVal !== null ? currentVal : ''}
                      onChange={(e) => handleValueChange(field, e.target.value !== '' ? parseFloat(e.target.value) : '')}
                      className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500 text-sm font-semibold bg-white"
                    />
                    {q.unit && (
                      <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400 pointer-events-none">
                        {q.unit}
                      </span>
                    )}
                  </div>

                  {q.presets && q.presets.length > 0 && (
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-[11px] text-slate-400 font-medium">
                        {language === 'hi' ? 'सुझाव:' : 'Presets:'}
                      </span>
                      {q.presets.map((preset) => (
                        <button
                          key={preset}
                          type="button"
                          onClick={() => handleValueChange(field, preset)}
                          className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
                        >
                          {preset} {q.unit}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {errorMsg && (
        <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Footer Submit CTA */}
      <div className="flex items-center justify-between gap-3 pt-2">
        <span className="text-xs text-slate-500 font-medium hidden sm:inline-block">
          {language === 'hi'
            ? '✓ निर्णय 100% सटीक नियम इंजन द्वारा निकाला जाता है'
            : '✓ Verdict computed mathematically by deterministic rule engine'}
        </span>

        <button
          type="button"
          disabled={isSubmitting}
          onClick={handleSubmit}
          className="w-full sm:w-auto px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs sm:text-sm shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 min-h-[44px]"
        >
          {isSubmitting ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>{language === 'hi' ? 'गणना हो रही है...' : 'Evaluating Rules...'}</span>
            </>
          ) : (
            <>
              <ShieldCheck className="w-4 h-4" />
              <span>
                {language === 'hi'
                  ? 'जानकारी जमा करें एवं अंतिम पात्रता जानें'
                  : 'Submit & Finalize Decision'}
              </span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
