import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { RotateCcw, Shield, ExternalLink, Globe } from 'lucide-react';

export default function Header() {
  const { language, setLanguage, t } = useLanguage();
  const { currentScreen, setCurrentScreen, setShowClearConfirmModal } = useSession();

  return (
    <header className="no-print bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div
          onClick={() => setCurrentScreen('S0')}
          className="flex items-center gap-3 cursor-pointer group select-none"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-md border border-blue-400/30 group-hover:scale-105 transition-transform">
            🏛️
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white group-hover:text-blue-300 transition-colors">
                {t('app_name')}
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-full bg-blue-950/80 text-blue-300 border border-blue-800">
                {t('official_assistant')}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-normal leading-tight hidden xs:block">
              {language === 'hi' ? 'सरकारी योजना पात्रता मार्गदर्शक' : 'Government Scheme Eligibility Guide'}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Language Toggle */}
          <div className="flex items-center bg-slate-800 p-0.5 rounded-lg border border-slate-700 shadow-inner">
            <button
              onClick={() => setLanguage('hi')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                language === 'hi'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white'
              }`}
              aria-label="हिंदी भाषा चुनें"
            >
              हिन्दी
            </button>
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                language === 'en'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white'
              }`}
              aria-label="Select English language"
            >
              English
            </button>
          </div>

          {/* Clear & Exit Button (Always visible on all screens) */}
          <button
            onClick={() => setShowClearConfirmModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-300 hover:text-white bg-rose-950/40 hover:bg-rose-900/70 border border-rose-800/60 transition-all shadow-xs min-h-[36px]"
            title={t('clear_and_exit')}
            aria-label={t('clear_and_exit')}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden md:inline">{t('clear_and_exit')}</span>
            <span className="md:hidden">{language === 'hi' ? 'मिटाएं' : 'Exit'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
