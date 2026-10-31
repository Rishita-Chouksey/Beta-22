import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { AlertTriangle, Trash2, X, ShieldAlert } from 'lucide-react';

export default function ClearExitModal() {
  const { t } = useLanguage();
  const { showClearConfirmModal, setShowClearConfirmModal, resetSession } = useSession();

  if (!showClearConfirmModal) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/60 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-fade-in">
      <div className="bg-white rounded-2xl max-w-sm w-full p-6 sm:p-7 shadow-2xl border border-slate-200" role="dialog" aria-modal="true">
        <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-4 border border-rose-100">
          <Trash2 className="w-6 h-6" />
        </div>

        <h3 className="text-lg font-bold text-center text-slate-900 mb-2 tracking-tight">
          {t('clear_confirm_title')}
        </h3>

        <p className="text-xs sm:text-sm text-slate-500 text-center mb-6 leading-relaxed">
          {t('clear_confirm_msg')}
        </p>

        <div className="flex flex-col gap-2.5">
          <button
            onClick={resetSession}
            className="w-full bg-rose-600 hover:bg-rose-700 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors min-h-[48px] text-sm shadow-sm"
          >
            <Trash2 className="w-4 h-4" />
            <span>{t('clear_now')}</span>
          </button>
          
          <button
            onClick={() => setShowClearConfirmModal(false)}
            className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-3 px-4 rounded-xl transition-colors min-h-[48px] text-sm"
          >
            {t('cancel')}
          </button>
        </div>
      </div>
    </div>
  );
}
