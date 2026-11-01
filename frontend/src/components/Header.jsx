import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import {
  RotateCcw,
  Shield,
  FileCheck2,
  Home,
  HelpCircle,
  ExternalLink,
  CheckCircle2,
  Globe
} from 'lucide-react';

export default function Header() {
  const { language, setLanguage, t, lt } = useLanguage();
  const { currentScreen, setCurrentScreen, setShowClearConfirmModal, openDocumentGuide } = useSession();

  const isHomeActive = ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6'].includes(currentScreen);
  const isDocGuideActive = currentScreen === 'S8';
  const isFormHelpActive = currentScreen === 'S7';
  const isAdminActive = currentScreen === 'S9';

  return (
    <header className="no-print sticky top-0 z-40 bg-white border-b border-slate-200/90 shadow-xs">
      {/* 1. National Flag Tricolour Accent Line */}
      <div className="h-1 w-full bg-gradient-to-r from-[#FF9933] via-[#FFFFFF] via-50% to-[#138808]" />

      {/* 2. Official Government Masthead Utility Bar */}
      <div className="bg-slate-50 border-b border-slate-200/70 text-[11px] text-slate-600 py-1 px-4 sm:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800 tracking-wide flex items-center gap-1.5">
              <span className="text-xs">🇮🇳</span>
              <span>{lt('Government of India', 'भारत सरकार', 'ভারত সরকার', 'महाराष्ट्र / भारत शासन')}</span>
            </span>
            <span className="text-slate-300">|</span>
            <span className="hidden sm:inline text-slate-500 font-medium">
              {lt('Citizen Welfare & Entitlement Portal', 'नागरिक कल्याण एवं अधिकारिता मंच', 'নাগরিক কল্যাণ ও যোগ্যতা পোর্টাল')}
            </span>
          </div>

          <div className="flex items-center gap-3 text-[11px]">
            <span className="hidden md:inline-flex items-center gap-1 text-emerald-800 font-medium">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              <span>{lt('Zero PII Stored • Deterministic Engine', 'शून्य व्यक्तिगत डेटा संचयन • सुरक्षित')}</span>
            </span>
            <a
              href="https://india.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-600 hover:text-blue-800 inline-flex items-center gap-0.5 font-medium hover:underline"
            >
              <span>india.gov.in</span>
              <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
            </a>
          </div>
        </div>
      </div>

      {/* 3. Main Government Portal Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-8 h-18 flex items-center justify-between gap-4">
        {/* Brand / Official Crest / National Title */}
        <div
          onClick={() => setCurrentScreen('S0')}
          className="flex items-center gap-3 cursor-pointer group select-none flex-shrink-0"
        >
          {/* Official Emblem: Indian National Ashoka Chakra Crest */}
          <div className="w-11 h-11 rounded-full bg-white border border-slate-200 shadow-xs flex items-center justify-center p-1 group-hover:border-blue-300 transition-colors">
            <svg viewBox="0 0 100 100" className="w-9 h-9 text-[#000080]" fill="currentColor" aria-hidden="true">
              <circle cx="50" cy="50" r="47" fill="none" stroke="#000080" strokeWidth="3" />
              <circle cx="50" cy="50" r="42" fill="none" stroke="#000080" strokeWidth="1.5" />
              <circle cx="50" cy="50" r="10" fill="#000080" />
              <circle cx="50" cy="50" r="4" fill="#ffffff" />
              {Array.from({ length: 24 }).map((_, i) => (
                <line
                  key={i}
                  x1="50"
                  y1="50"
                  x2={50 + 38 * Math.cos((i * 15 * Math.PI) / 180)}
                  y2={50 + 38 * Math.sin((i * 15 * Math.PI) / 180)}
                  stroke="#000080"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              ))}
            </svg>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl sm:text-2xl tracking-tight text-[#0a2540] group-hover:text-blue-900 transition-colors font-sans">
                {t('app_name')}
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase rounded-full bg-blue-50 text-blue-900 border border-blue-200">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                <span>{t('official_assistant')}</span>
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-500 font-medium leading-tight">
              {lt(
                'Citizen Welfare Discovery & Entitlement Portal',
                'नागरिक कल्याण योजना खोज एवं पात्रता पोर्टल',
                'নাগরিক কল্যাণ যোজনা আবিষ্কার ও যোগ্যতা পোর্টাল'
              )}
            </p>
          </div>
        </div>

        {/* Official Navigation Menu */}
        <nav className="hidden lg:flex items-center gap-1">
          <button
            onClick={() => setCurrentScreen('S0')}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-colors cursor-pointer ${
              isHomeActive
                ? 'text-blue-900 bg-blue-50/90 font-bold border-b-2 border-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Home className={`w-4 h-4 ${isHomeActive ? 'text-blue-700' : 'text-slate-500'}`} />
            <span>{t('nav_home')}</span>
          </button>

          <button
            onClick={() => openDocumentGuide()}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-colors cursor-pointer ${
              isDocGuideActive
                ? 'text-blue-900 bg-blue-50/90 font-bold border-b-2 border-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileCheck2 className={`w-4 h-4 ${isDocGuideActive ? 'text-blue-700' : 'text-slate-500'}`} />
            <span>{t('nav_doc_guide')}</span>
          </button>

          <button
            onClick={() => setCurrentScreen('S7')}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-colors cursor-pointer ${
              isFormHelpActive
                ? 'text-blue-900 bg-blue-50/90 font-bold border-b-2 border-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <HelpCircle className={`w-4 h-4 ${isFormHelpActive ? 'text-blue-700' : 'text-slate-500'}`} />
            <span>{t('nav_form_help')}</span>
          </button>

          <button
            onClick={() => setCurrentScreen('S9')}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-colors cursor-pointer ${
              isAdminActive
                ? 'text-blue-900 bg-blue-50/90 font-bold border-b-2 border-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
            title="Administrative Scheme Intelligence Monitor"
          >
            <Shield className={`w-4 h-4 ${isAdminActive ? 'text-blue-700' : 'text-slate-500'}`} />
            <span>
              {lt('Scheme Monitor', 'योजना निगरानी', 'যোজনা পর্যবেক্ষণ')}
            </span>
          </button>
        </nav>

        {/* Right Side Utility Controls */}
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          {/* Mobile Quick Doc Guide button */}
          <button
            onClick={() => openDocumentGuide()}
            className="lg:hidden flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-200 hover:bg-slate-200 transition-colors"
            title={t('nav_doc_guide')}
            aria-label={t('nav_doc_guide')}
          >
            <FileCheck2 className="w-3.5 h-3.5 text-blue-700" />
            <span className="hidden xs:inline">
              {lt('Docs', 'दस्तावेज़', 'নথিপত্র')}
            </span>
          </button>

          {/* Mobile Quick Form Helper button */}
          <button
            onClick={() => setCurrentScreen('S7')}
            className="lg:hidden flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-200 hover:bg-slate-200 transition-colors"
            title={t('nav_form_help')}
            aria-label={t('nav_form_help')}
          >
            <HelpCircle className="w-3.5 h-3.5 text-blue-700" />
          </button>

          {/* Multilingual Selector: Standard Government Portal Tabs */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200/90">
            <button
              onClick={() => setLanguage('hi')}
              className={`px-2 sm:px-2.5 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                language === 'hi'
                  ? 'bg-white text-blue-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="हिंदी भाषा चुनें"
            >
              हिन्दी
            </button>
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 sm:px-2.5 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                language === 'en'
                  ? 'bg-white text-blue-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="Select English language"
            >
              English
            </button>
            <button
              onClick={() => setLanguage('mr')}
              className={`px-2 sm:px-2.5 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                language === 'mr'
                  ? 'bg-white text-blue-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="मराठी भाषा निवडा"
            >
              मराठी
            </button>
            <button
              onClick={() => setLanguage('bn')}
              className={`px-2 sm:px-2.5 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                language === 'bn'
                  ? 'bg-white text-blue-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="বাংলা ভাষা নির্বাচন করুন"
            >
              বাংলা
            </button>
          </div>

          {/* Clear & Exit Button (Clean, respectful civic utility button) */}
          <button
            onClick={() => setShowClearConfirmModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-rose-700 bg-white hover:bg-rose-50 border border-slate-200 hover:border-rose-300 transition-colors shadow-2xs min-h-[34px] cursor-pointer"
            title={t('clear_and_exit')}
            aria-label={t('clear_and_exit')}
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-500 group-hover:text-rose-600" />
            <span className="hidden md:inline">{t('clear_and_exit')}</span>
            <span className="md:hidden">
              {lt('Exit', 'मिटाएं', 'মুছুন')}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
