import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchSchemeDetails } from '../services/api';
import {
  X,
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
  Eye
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S5_SchemeDetailsModal() {
  const { language, t } = useLanguage();
  const { activeSchemeModal, setActiveSchemeModal, currentScreen, openDocumentGuide } = useSession();

  const [fullScheme, setFullScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (activeSchemeModal?.scheme_id) {
      setIsLoading(true);
      fetchSchemeDetails(activeSchemeModal.scheme_id)
        .then((data) => setFullScheme(data))
        .catch((err) => console.error('Fetch scheme details error:', err))
        .finally(() => setIsLoading(false));
    }
  }, [activeSchemeModal]);

  if (!activeSchemeModal || currentScreen === 'S8') return null;

  const name = language === 'hi' ? activeSchemeModal.scheme_name_hi : activeSchemeModal.scheme_name_en;
  const benefit = language === 'hi' ? activeSchemeModal.benefit_hi : activeSchemeModal.benefit_en;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white p-5 flex items-start justify-between gap-4 border-b border-slate-800">
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-slate-800 text-blue-300 border border-slate-700">
                {activeSchemeModal.level === 'central'
                  ? (language === 'hi' ? 'केंद्रीय योजना (Central)' : 'Central Scheme')
                  : (language === 'hi' ? 'राज्य योजना (State)' : 'State Scheme')}
              </span>
              <span className="text-xs text-slate-400 font-semibold">
                {activeSchemeModal.category}
              </span>
            </div>
            <h3 className="text-lg sm:text-xl font-bold leading-snug">{name}</h3>
          </div>

          <div className="flex items-center gap-2">
            <AudioSpeaker text={`${name}। ${benefit}`} className="w-8 h-8 text-white bg-slate-800 border-slate-700" />
            <button
              onClick={() => setActiveSchemeModal(null)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {/* Key Entitlement */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 space-y-1">
            <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wider">
              💰 {t('entitlements')}
            </h4>
            <p className="text-sm sm:text-base font-semibold text-emerald-950 leading-relaxed">
              {benefit}
            </p>
          </div>

          {/* Individual Rule Evaluation Breakdown */}
          {activeSchemeModal.rule_results && activeSchemeModal.rule_results.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                <span>{t('rules_breakdown')} (Deterministic Engine)</span>
              </h4>

              <div className="space-y-2">
                {activeSchemeModal.rule_results.map((r, idx) => {
                  const ruleReason = language === 'hi' ? r.reason_hi : r.reason_en;
                  return (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border bg-white flex items-start gap-3 text-xs sm:text-sm shadow-2xs"
                    >
                      <div className="mt-0.5 flex-shrink-0">
                        {r.outcome === 'PASS' && <CheckCircle className="w-4 h-4 text-emerald-600" />}
                        {r.outcome === 'FAIL' && <XCircle className="w-4 h-4 text-rose-600" />}
                        {r.outcome === 'UNKNOWN' && <HelpCircle className="w-4 h-4 text-amber-500" />}
                      </div>
                      <div className="flex-1 leading-snug space-y-0.5">
                        <span className="font-bold text-slate-900 block capitalize">
                          {r.field.replace('_', ' ')}:
                        </span>
                        <span className="text-slate-600 block">{ruleReason}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Important Restrictions if any */}
          {fullScheme?.restrictions && fullScheme.restrictions.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2 text-xs sm:text-sm">
              <h4 className="font-bold text-amber-900 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                <span>
                  {language === 'hi' ? 'महत्वपूर्ण अपवर्जन शर्तें (Exclusions)' : 'Important Exclusion Rules'}
                </span>
              </h4>
              <ul className="list-disc list-inside space-y-1 text-amber-950">
                {fullScheme.restrictions.map((res, i) => (
                  <li key={i}>{res}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Required Documents */}
          {fullScheme?.required_documents && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <FileCheck className="w-4 h-4 text-blue-600" />
                <span>{t('documents_required')}</span>
              </h4>

              <div className="space-y-2.5">
                {fullScheme.required_documents.map((doc) => {
                  const docName = language === 'hi' ? doc.name_hi : doc.name_en;
                  const docProc = language === 'hi' ? doc.how_to_get_hi : doc.how_to_get_en;
                  return (
                    <div key={doc.id} className="p-3.5 bg-white border border-slate-200 rounded-xl text-xs sm:text-sm space-y-2 shadow-2xs">
                      <div className="font-bold text-slate-900">{docName}</div>
                      <div className="text-slate-600 text-xs">{docProc}</div>
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        <button
                          type="button"
                          onClick={() => openDocumentGuide(doc.id, 'S5')}
                          className="inline-flex items-center gap-1.5 text-xs text-amber-900 hover:text-amber-950 font-bold bg-amber-50 hover:bg-amber-100 border border-amber-300/80 px-2.5 py-1 rounded-lg transition-colors cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5 text-amber-700" />
                          <span>{t('open_in_doc_guide')}</span>
                        </button>
                        {doc.online_url && (
                          <a
                            href={doc.online_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-700 hover:text-blue-900 font-bold px-2 py-1"
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

          {/* Step-by-step Application Procedure */}
          {fullScheme?.application_procedure && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <ListOrdered className="w-4 h-4 text-blue-600" />
                <span>{t('how_to_apply')}</span>
              </h4>

              <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5 text-xs sm:text-sm leading-relaxed text-slate-700 shadow-2xs">
                {fullScheme.application_procedure.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-900 font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="flex-1">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Helpline and Verified Date */}
          <div className="p-3.5 bg-slate-100 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-slate-600">
            {fullScheme?.helpline && (
              <span className="flex items-center gap-1.5 font-medium">
                <Phone className="w-3.5 h-3.5 text-slate-700" />
                <span><strong>{t('helpline')}: </strong>{fullScheme.helpline}</span>
              </span>
            )}
            <span className="flex items-center gap-1 text-slate-400">
              <Calendar className="w-3.5 h-3.5" />
              <span>{t('verified_on')}: {activeSchemeModal.last_verified_date}</span>
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-white border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          {fullScheme?.official_source_url ? (
            <a
              href={fullScheme.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto px-6 py-2.5 bg-blue-700 hover:bg-blue-800 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-sm transition-all inline-flex items-center justify-center gap-1.5 no-underline min-h-[44px]"
            >
              <ExternalLink className="w-4 h-4" />
              <span>{t('official_portal')}</span>
            </a>
          ) : <div />}

          <button
            onClick={() => setActiveSchemeModal(null)}
            className="w-full sm:w-auto px-5 py-2.5 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-xl text-xs sm:text-sm font-semibold transition-colors min-h-[44px]"
          >
            {t('cancel')}
          </button>
        </div>
      </div>
    </div>
  );
}
