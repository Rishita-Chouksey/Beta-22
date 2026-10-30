import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchDocumentChecklist } from '../services/api';
import {
  ArrowLeft,
  Printer,
  CheckSquare,
  Square,
  ExternalLink,
  MapPin,
  FileCheck,
  ShieldCheck,
  Calendar,
  Sparkles
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S6_DocumentChecklistScreen() {
  const { language, t } = useLanguage();
  const { evaluationResults, setCurrentScreen, checklistData, setChecklistData } = useSession();

  const [readyDocs, setReadyDocs] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  const eligibleIds = (evaluationResults?.eligible || []).map((s) => s.scheme_id);
  const targetSchemeIds = eligibleIds.length > 0 ? eligibleIds : (evaluationResults?.not_sure || []).map((s) => s.scheme_id);

  useEffect(() => {
    if (targetSchemeIds.length > 0) {
      setIsLoading(true);
      fetchDocumentChecklist(targetSchemeIds)
        .then((data) => {
          setChecklistData(data);
        })
        .catch((err) => console.error('Checklist fetch error:', err))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const toggleReady = (docId) => {
    setReadyDocs((prev) => ({
      ...prev,
      [docId]: !prev[docId],
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  const documents = checklistData?.documents || [];
  const readyCount = Object.values(readyDocs).filter(Boolean).length;
  const progressPercent = documents.length > 0 ? Math.round((readyCount / documents.length) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Navigation & Header */}
        <div className="no-print space-y-2">
          <button
            onClick={() => setCurrentScreen('S4')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{language === 'hi' ? 'परिणामों पर लौटें' : 'Back to Results'}</span>
          </button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
                {t('checklist_title')}
              </h2>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                {t('checklist_subtitle')}
              </p>
            </div>
            <AudioSpeaker
              text={
                language === 'hi'
                  ? `आपकी पात्र योजनाओं के लिए कुल ${documents.length} दस्तावेज़ आवश्यक हैं।`
                  : `A total of ${documents.length} documents are required across your eligible schemes.`
              }
              className="mt-1 flex-shrink-0"
            />
          </div>
        </div>

        {/* Print-Only Header */}
        <div className="hidden print-only border-b-2 border-slate-900 pb-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-extrabold text-slate-900">योजनासारथी (YojnaSarthi)</h1>
              <p className="text-xs text-slate-700 font-bold uppercase tracking-wider mt-0.5">
                नागरिक व्यक्तिगत दस्तावेज़ चेकलिस्ट (Personalized Scheme Document Checklist)
              </p>
            </div>
            <div className="text-right text-xs text-slate-500 space-y-0.5">
              <p>दिनांक: {new Date().toLocaleDateString('en-IN')}</p>
              <p>आधिकारिक सत्यापन मार्गदर्शिका</p>
            </div>
          </div>
        </div>

        {/* Readiness Tracker Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                {language === 'hi' ? 'दस्तावेज़ तैयारी स्थिति' : 'Document Readiness'}
              </span>
              <span className="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-blue-50 text-blue-800 border border-blue-200">
                {readyCount} / {documents.length} Ready
              </span>
            </div>

            {/* Visual progress bar */}
            <div className="w-full max-w-md bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className="bg-emerald-600 h-full transition-all duration-300 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-500">
              {language === 'hi'
                ? 'दस्तावेज़ की उपलब्धता केवल आपकी सुविधा के लिए ट्रैक होती है, पात्रता पहले ही सिद्ध है।'
                : 'Document readiness is tracked separately from eligibility for your application preparation.'}
            </p>
          </div>

          <button
            onClick={handlePrint}
            className="no-print self-stretch sm:self-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-xs transition-colors min-h-[44px]"
          >
            <Printer className="w-4 h-4" />
            <span>{t('print_save_pdf')}</span>
          </button>
        </div>

        {/* Consolidated Documents List */}
        {isLoading ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
            <div className="w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs font-semibold text-slate-600">समेकित चेकलिस्ट तैयार की जा रही है...</p>
          </div>
        ) : (
          <div className="space-y-3.5">
            {documents.map((doc) => {
              const isChecked = Boolean(readyDocs[doc.document_id]);
              const docName = language === 'hi' ? doc.name_hi : doc.name_en;
              const purpose = language === 'hi' ? doc.purpose_hi : doc.purpose_en;
              const howToGet = language === 'hi' ? doc.how_to_get_hi : doc.how_to_get_en;

              return (
                <div
                  key={doc.document_id}
                  className={`bg-white border rounded-2xl p-5 transition-all shadow-xs printable-doc-card ${
                    isChecked
                      ? 'border-emerald-300 bg-emerald-50/20'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <button
                      type="button"
                      onClick={() => toggleReady(doc.document_id)}
                      className="mt-0.5 text-slate-400 hover:text-emerald-700 flex-shrink-0 transition-colors p-1"
                      title={isChecked ? 'तैयार है' : 'तैयार नहीं'}
                      aria-label={docName}
                    >
                      {isChecked ? (
                        <CheckSquare className="w-6 h-6 text-emerald-600" />
                      ) : (
                        <Square className="w-6 h-6 text-slate-300" />
                      )}
                    </button>

                    <div className="flex-1 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                        <h3 className={`text-base font-bold ${isChecked ? 'text-emerald-950 line-through' : 'text-slate-900'}`}>
                          {docName}
                        </h3>

                        {/* Scheme tag pills */}
                        <div className="flex flex-wrap gap-1">
                          {doc.schemes_required_for?.map((sName, sIdx) => (
                            <span
                              key={sIdx}
                              className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200"
                            >
                              ✓ {sName}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Purpose */}
                      <p className="text-xs text-slate-600 leading-relaxed">
                        <strong className="text-slate-800">
                          {language === 'hi' ? 'उद्देश्य: ' : 'Purpose: '}
                        </strong>
                        {purpose}
                      </p>

                      {/* Procurement Instructions Box */}
                      <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-xs text-slate-700 space-y-1.5">
                        <p className="leading-relaxed">
                          <strong className="text-slate-900">
                            {language === 'hi' ? 'कहाँ और कैसे प्राप्त करें: ' : 'How to Obtain: '}
                          </strong>
                          {howToGet}
                        </p>

                        <div className="flex flex-wrap items-center gap-4 pt-1 text-xs">
                          {doc.online_url && (
                            <a
                              href={doc.online_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-700 hover:text-blue-900 font-bold inline-flex items-center gap-1 underline"
                            >
                              <span>{t('online_link')}</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}

                          {doc.offline_office && (
                            <span className="text-slate-500 inline-flex items-center gap-1 font-medium">
                              <MapPin className="w-3.5 h-3.5 text-slate-400" />
                              <span>{doc.offline_office}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Navigation Action Bar */}
      <div className="no-print pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={handlePrint}
          className="w-full sm:w-auto px-6 py-3 bg-blue-700 hover:bg-blue-800 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all inline-flex items-center justify-center gap-2 min-h-[48px]"
        >
          <Printer className="w-4 h-4" />
          <span>{t('print_save_pdf')}</span>
        </button>

        <button
          onClick={() => setCurrentScreen('S4')}
          className="w-full sm:w-auto px-6 py-3 border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold rounded-xl text-sm transition-colors min-h-[48px]"
        >
          {t('back')}
        </button>
      </div>
    </div>
  );
}
