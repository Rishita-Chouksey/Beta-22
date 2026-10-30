import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { Clock, ShieldCheck } from 'lucide-react';

export default function IdleWarningModal() {
  const { t } = useLanguage();
  const { showIdleWarningModal, setShowIdleWarningModal, resetSession } = useSession();

  if (!showIdleWarningModal) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/70 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-fade-in">
      <div className="bg-white rounded-2xl max-w-sm w-full p-6 sm:p-7 shadow-2xl border-2 border-amber-500" role="alertdialog">
        <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200">
          <Clock className="w-6 h-6 animate-pulse" />
        </div>

        <h3 className="text-lg font-bold text-center text-slate-900 mb-2 tracking-tight">
          {t('idle_warning_title')}
        </h3>

        <p className="text-xs sm:text-sm text-slate-500 text-center mb-6 leading-relaxed">
          {t('idle_warning_msg')}
        </p>

        <div className="flex flex-col gap-2.5">
          <button
            onClick={() => setShowIdleWarningModal(false)}
            className="w-full bg-blue-700 hover:bg-blue-800 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors min-h-[48px] text-sm shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>{t('keep_session')}</span>
          </button>
          
          <button
            onClick={resetSession}
            className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2.5 px-4 rounded-xl transition-colors text-xs"
          >
            {t('clear_now')}
          </button>
        </div>
      </div>
    </div>
  );
}
