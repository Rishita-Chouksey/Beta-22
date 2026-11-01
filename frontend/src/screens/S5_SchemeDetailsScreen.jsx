import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchSchemeDetails } from '../services/api';
import VerificationQuestionnaire from '../components/VerificationQuestionnaire';
import {
  Phone,
  Eye,
  XCircle,
  Calendar,
  ExternalLink,
  ChevronRight,
  FileCheck,
  Sparkles,
  HelpCircle,
  CheckCircle,
  FileText,
  ShieldCheck,
  ListOrdered,
  AlertTriangle,
  ArrowLeft
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S5_SchemeDetailsScreen() {
  const { language, t } = useLanguage();
  const {
    activeSchemeModal,
    setActiveSchemeModal,
    setCurrentScreen,
    openDocumentGuide,
    evaluationResults
  } = useSession();

  const [fullScheme, setFullScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showVerificationForm, setShowVerificationForm] = useState(false);

  // If activeSchemeModal changes, refresh full scheme data
  useEffect(() => {
    if (activeSchemeModal?.scheme_id) {
      setIsLoading(true);
      fetchSchemeDetails(activeSchemeModal.scheme_id)
        .then((data) => setFullScheme(data))
        .catch((err) => console.error('Fetch scheme details error:', err))
        .finally(() => setIsLoading(false));
    }
  }, [activeSchemeModal]);

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
          {lt('No Scheme Selected', 'कोई योजना चयनित नहीं है')}
        </h2>
        <button
          onClick={() => setCurrentScreen('S4')}
          className="px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-bold hover:bg-teal-700"
        >
          {lt('Back to Scheme Results', 'योजना परिणामों पर वापस जाएं')}
        </button>
      </div>
    );
  }

  const name = getBilingualText(currentEvaluation, 'scheme_name') || lt(currentEvaluation.scheme_name_en, currentEvaluation.scheme_name_hi);
  const secondaryName = language === 'en' ? (currentEvaluation.scheme_name_hi || '') : (currentEvaluation.scheme_name_en || '');
  const benefit = getBilingualText(currentEvaluation, 'benefit') || lt(currentEvaluation.benefit_en, currentEvaluation.benefit_hi);
  const reason = getBilingualText(currentEvaluation, 'deciding_reason') || lt(currentEvaluation.deciding_reason_en, currentEvaluation.deciding_reason_hi);
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
                  {lt('Status: Likely Eligible', 'पात्रता स्थिति: संभावित पात्र')}
                </span>
                <span className="text-xs text-emerald-800 font-semibold">
                  {lt('All Rules Passed', '100% नियम उत्तीर्ण')}
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-emerald-950">
                {lt('Congratulations! Your profile satisfies all official eligibility criteria.', 'बधाई हो! आपकी प्रोफाइल इस योजना के सभी वैधानिक नियमों के अनुकूल है।')}
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
            <span>{lt('View Document Checklist', 'दस्तावेज़ चेकलिस्ट देखें')}</span>
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
                    {lt('Status: Needs Verification', 'पात्रता स्थिति: सत्यापन आवश्यक')}
                  </span>
                  <span className="text-xs text-amber-900 font-semibold">
                    {missingFields.length} {lt('Unknown Fields', 'अधूरी जानकारी')}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-amber-950">
                  {lt('You may qualify for this scheme, but additional verification is needed.', 'आप इस योजना के लिए पात्र हो सकते हैं, परंतु कुछ जानकारी अभी अधूरी है।')}
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
                {showVerificationForm ? lt('Hide Questionnaire', 'प्रश्नावली छुपाएं') : lt('Verify Now (Answer Unknowns)', 'अभी सत्यापित करें (अधूरी जानकारी भरें)')}
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
              {lt('Status: Not Eligible', 'पात्रता स्थिति: अपात्र (Not Eligible)')}
            </span>
            <h3 className="text-base sm:text-lg font-bold text-rose-950">
              {lt('Your profile does not satisfy at least one mandatory statutory rule.', 'आपकी वर्तमान प्रोफाइल इस योजना के कम से कम एक वैधानिक नियम को पूरा नहीं करती है।')}
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
          <span>{lt('← Back to Scheme Results', '← परिणामों पर वापस जाएं')}</span>
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
            {currentEvaluation.level === 'central' ? lt('Central Government Scheme', 'केंद्रीय योजना (Central Govt)') : lt('State Government Scheme', 'राज्य योजना (State Government)')}
          </span>

          <span className="text-xs font-bold px-3 py-1 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
            {lt(currentEvaluation.category, currentEvaluation.category_hi || currentEvaluation.category)}
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
              {lt('All Eligibility Criteria & Rule Audit', 'योजना के संपूर्ण पात्रता नियम एवं मानदंड')}
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed max-w-3xl">
            {lt('Each criterion is mathematically checked by our deterministic Python AST rule engine against your verified profile. AI is strictly prohibited from guessing eligibility.', 'प्रत्येक नियम को हमारी पायथन एएसटी नियम प्रणाली द्वारा गणितीय शुद्धता के साथ जाँचा जाता है। एआई को पात्रता का मनमाना अनुमान लगाने की अनुमति नहीं है।')}
          </p>
        </div>

        {/* Detailed Criteria Cards */}
        {ruleResults && ruleResults.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ruleResults.map((r, idx) => {
              const ruleReason = getBilingualText(r, 'reason') || lt(r.reason_en, r.reason_hi);
              const isPass = r.outcome === 'PASS';
              const isFail = r.outcome === 'FAIL';
              const isUnk = r.outcome === 'UNKNOWN';

              // Format field name
              const cleanField = r.field.replace(/_/g, ' ');

              return (
                <div
                  key={idx}
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
                          {isPass && lt('Pass', 'उत्तीर्ण (PASS)')}
                          {isFail && lt('Fail', 'विफल (FAIL)')}
                          {isUnk && lt('Unknown', 'सत्यापन आवश्यक (UNKNOWN)')}
                        </span>
                      </span>
                    </div>

                    {/* Requirement comparison */}
                    <div className="bg-white/80 border border-slate-200/80 rounded-xl p-3 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between gap-2 text-slate-600">
                        <span className="font-semibold text-slate-500">
                          {lt('Official Requirement:', 'नियम शर्त (Requirement):')}
                        </span>
                        <span className="font-bold text-slate-900 text-right">
                          {r.operator} {JSON.stringify(r.expected_value)}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-2 text-slate-600 pt-1 border-t border-slate-100">
                        <span className="font-semibold text-slate-500">
                          {lt('Your Recorded Value:', 'आपकी जानकारी (Recorded):')}
                        </span>
                        <span className="font-bold text-slate-900 text-right">
                          {r.actual_value !== null && r.actual_value !== undefined
                            ? String(r.actual_value)
                            : (lt('Unknown', 'अज्ञात (Not provided)'))}
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
            {lt('Loading verified rule breakdown...', 'नियम सूची लोड हो रही है...')}
          </div>
        )}
      </div>

      {/* 5. Important Restrictions & Exclusions */}
      {fullScheme?.restrictions && fullScheme.restrictions.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 text-amber-900">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h3 className="text-lg font-bold">
              {lt('Important Exclusion Rules & Restrictions', 'महत्वपूर्ण अपवर्जन एवं प्रतिबंध (Exclusion Policies)')}
            </h3>
          </div>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
            {fullScheme.restrictions.map((res, i) => (
              <li key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50/50 border border-amber-100">
                <span className="text-amber-600 font-bold">•</span>
                <span className="leading-relaxed">{res}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

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
              {lt('Ensure you possess these documents before applying. Click to view samples and procurement steps.', 'आवेदन करने से पूर्व इन आवश्यक प्रमाण पत्रों को तैयार रखें। नमूना देखने हेतु दस्तावेज़ गाइड खोलें।')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {fullScheme.required_documents.map((doc) => {
              const docName = getBilingualText(doc, 'name') || lt(doc.name_en, doc.name_hi);
              const docProc = getBilingualText(doc, 'how_to_get') || lt(doc.how_to_get_en, doc.how_to_get_hi);
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

                    {doc.online_url && (
                      <a
                        href={doc.online_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-teal-700 hover:text-teal-900 font-bold px-2 py-1"
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
              {lt('Follow these step-by-step instructions for online or nearest physical center submission.', 'आधिकारिक पोर्टल अथवा नजदीकी लोक सेवा केंद्र / ग्राम पंचायत कार्यालय से आवेदन की प्रक्रिया।')}
            </p>
          </div>

          <div className="space-y-3">
            {fullScheme.application_procedure.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3.5 p-4 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs sm:text-sm text-slate-800 leading-relaxed shadow-2xs"
              >
                <span className="w-6 h-6 rounded-full bg-slate-900 text-white font-extrabold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="flex-1 font-medium">{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
          <span>{lt('Back to All Schemes', 'सभी योजनाओं पर वापस जाएं')}</span>
        </button>

        <div className="flex items-center gap-3 w-full sm:w-auto flex-wrap">
          {fullScheme?.official_source_url && (
            <a
              href={fullScheme.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 sm:flex-initial px-6 py-3 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-xl text-xs sm:text-sm shadow-sm transition inline-flex items-center justify-center gap-2 no-underline min-h-[44px]"
            >
              <span>{t('official_portal')}</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}

          {isEligible && (
            <button
              onClick={handleGenerateChecklist}
              className="flex-1 sm:flex-initial px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl text-xs sm:text-sm shadow-sm transition inline-flex items-center justify-center gap-2 min-h-[44px]"
            >
              <FileText className="w-4 h-4" />
              <span>{t('get_checklist')}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
