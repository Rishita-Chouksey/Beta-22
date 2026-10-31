import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { RotateCcw, Shield, ExternalLink, Globe, BookOpen, FileCheck2, Home, HelpCircle, Activity } from 'lucide-react';

export default function Header() {
  const { language, setLanguage, t } = useLanguage();
  const { currentScreen, setCurrentScreen, setShowClearConfirmModal, openDocumentGuide } = useSession();

  const isHomeActive = ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6'].includes(currentScreen);
  const isDocGuideActive = currentScreen === 'S8';
  const isFormHelpActive = currentScreen === 'S7';
  const isAdminActive = currentScreen === 'S9';

  return (
    <header className="no-print bg-[#0b1730] border-b border-blue-900/40 text-white sticky top-0 z-40 shadow-md">
      {/* Subtle National Civic Top Accent */}
      <div className="h-0.5 w-full bg-gradient-to-r from-amber-500 via-blue-400 to-emerald-500 opacity-90" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3 sm:gap-4">
        {/* Brand / Logo */}
        <div
          onClick={() => setCurrentScreen('S0')}
          className="flex items-center gap-2.5 sm:gap-3 cursor-pointer group select-none flex-shrink-0"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-md border border-blue-400/30 group-hover:scale-105 transition-transform">
            🏛️
          </div>
          <div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-bold text-base sm:text-lg tracking-tight text-white group-hover:text-blue-300 transition-colors">
                {t('app_name')}
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-full bg-blue-950/90 text-blue-300 border border-blue-800/80">
                {t('official_assistant')}
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 font-normal leading-tight hidden xs:block">
              {language === 'hi' ? 'सरकारी योजना पात्रता मार्गदर्शक' : 'Government Scheme Eligibility Guide'}
            </p>
          </div>
        </div>

        {/* Civic Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-[#102042]/70 p-1 rounded-xl border border-blue-900/60 shadow-inner">
          <button
            onClick={() => setCurrentScreen('S0')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              isHomeActive
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-300 hover:text-white hover:bg-blue-950/60'
            }`}
          >
            <Home className="w-3.5 h-3.5" />
            <span>{t('nav_home')}</span>
          </button>

          <button
            onClick={() => openDocumentGuide()}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              isDocGuideActive
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-300 hover:text-white hover:bg-blue-950/60'
            }`}
          >
            <FileCheck2 className="w-3.5 h-3.5 text-amber-400" />
            <span>{t('nav_doc_guide')}</span>
          </button>

          <button
            onClick={() => setCurrentScreen('S7')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              isFormHelpActive
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-300 hover:text-white hover:bg-blue-950/60'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>{t('nav_form_help')}</span>
          </button>

          <button
            onClick={() => setCurrentScreen('S9')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              isAdminActive
                ? 'bg-teal-700 text-white shadow-xs'
                : 'text-slate-300 hover:text-white hover:bg-blue-950/60'
            }`}
            title="Administrative Scheme Intelligence Monitor"
          >
            <Shield className="w-3.5 h-3.5 text-teal-400" />
            <span>{language === 'hi' ? 'योजना निगरानी' : 'Monitor'}</span>
          </button>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          {/* Quick Document Guide Button for Mobile */}
          <button
            onClick={() => openDocumentGuide()}
            className="md:hidden flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-amber-300 bg-amber-950/40 border border-amber-700/50 hover:bg-amber-900/60 transition-colors"
            title={t('nav_doc_guide')}
            aria-label={t('nav_doc_guide')}
          >
            <FileCheck2 className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden xs:inline">{language === 'hi' ? 'दस्तावेज़' : 'Docs'}</span>
          </button>

          {/* Quick Monitor Button for Mobile */}
          <button
            onClick={() => setCurrentScreen('S9')}
            className="md:hidden flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-teal-300 bg-teal-950/40 border border-teal-700/50 hover:bg-teal-900/60 transition-colors"
            title="Admin Monitor"
            aria-label="Admin Monitor"
          >
            <Shield className="w-3.5 h-3.5 text-teal-400" />
          </button>

          {/* Language Toggle */}
          <div className="flex items-center bg-[#102042] p-0.5 rounded-lg border border-blue-900/60 shadow-inner">
            <button
              onClick={() => setLanguage('hi')}
              className={`px-2.5 sm:px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
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
              className={`px-2.5 sm:px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
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
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-300 hover:text-white bg-rose-950/40 hover:bg-rose-900/70 border border-rose-800/60 transition-all shadow-xs min-h-[36px]"
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
