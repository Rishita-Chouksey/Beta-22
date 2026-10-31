import React from 'react';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { SessionProvider, useSession } from './context/SessionContext';
import Header from './components/Header';
import ClearExitModal from './components/ClearExitModal';
import IdleWarningModal from './components/IdleWarningModal';
import ChatbotDrawer from './components/ChatbotDrawer';
import S0_StartScreen from './screens/S0_StartScreen';
import S1_QuestionnaireScreen from './screens/S1_QuestionnaireScreen';
import S2_FreeTextInputScreen from './screens/S2_FreeTextInputScreen';
import S3_ConfirmProfileScreen from './screens/S3_ConfirmProfileScreen';
import S4_ResultsScreen from './screens/S4_ResultsScreen';
import S5_SchemeDetailsModal from './screens/S5_SchemeDetailsModal';
import S6_DocumentChecklistScreen from './screens/S6_DocumentChecklistScreen';
import S7_FormHelpScreen from './screens/S7_FormHelpScreen';

function MainAppContent() {
  const { currentScreen } = useSession();
  const { language } = useLanguage();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      <Header />

      {/* Main Content Responsive Wrapper */}
      <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 flex flex-col">
        {currentScreen === 'S0' && <S0_StartScreen />}
        {currentScreen === 'S1' && <S1_QuestionnaireScreen />}
        {currentScreen === 'S2' && <S2_FreeTextInputScreen />}
        {currentScreen === 'S3' && <S3_ConfirmProfileScreen />}
        {currentScreen === 'S4' && <S4_ResultsScreen />}
        {currentScreen === 'S6' && <S6_DocumentChecklistScreen />}
        {currentScreen === 'S7' && <S7_FormHelpScreen />}
      </main>

      {/* Global Civic Footer */}
      <footer className="no-print border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">YojnaSarthi</span>
            <span>•</span>
            <span>
              {language === 'hi'
                ? 'नागरिक कल्याण एवं सार्वजनिक योजना सहायता'
                : 'Citizen Welfare & Public Scheme Assistance'}
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>
              {language === 'hi' ? 'सत्यापित सरकारी नियम' : 'Verified Official Rules'}
            </span>
            <span>•</span>
            <span>
              {language === 'hi'
                ? 'शून्य डेटा संचयन (Zero Retention)'
                : 'Zero Data Retention'}
            </span>
            <span>•</span>
            <span>
              {language === 'hi' ? 'डिजिटल भारत' : 'Digital India'}
            </span>
          </div>
        </div>
      </footer>

      {/* Global Modals & Floating Drawers */}
      <S5_SchemeDetailsModal />
      <ChatbotDrawer />
      <ClearExitModal />
      <IdleWarningModal />
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <SessionProvider>
        <MainAppContent />
      </SessionProvider>
    </LanguageProvider>
  );
}
