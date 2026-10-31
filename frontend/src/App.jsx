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
import S5_SchemeDetailsScreen from './screens/S5_SchemeDetailsScreen';
import S6_DocumentChecklistScreen from './screens/S6_DocumentChecklistScreen';
import S7_FormHelpScreen from './screens/S7_FormHelpScreen';
import S8_DocumentGuideScreen from './screens/S8_DocumentGuideScreen';
import S9_AdminMonitoringScreen from './screens/S9_AdminMonitoringScreen';
import { Shield } from 'lucide-react';

function MainAppContent() {
  const { currentScreen, setCurrentScreen } = useSession();
  const { language, lt } = useLanguage();

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
        {currentScreen === 'S5' && <S5_SchemeDetailsScreen />}
        {currentScreen === 'S6' && <S6_DocumentChecklistScreen />}
        {currentScreen === 'S7' && <S7_FormHelpScreen />}
        {currentScreen === 'S8' && <S8_DocumentGuideScreen />}
        {currentScreen === 'S9' && <S9_AdminMonitoringScreen />}
      </main>

      {/* Global Civic Footer */}
      <footer className="no-print border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">YojnaSarthi</span>
            <span>•</span>
            <span>
              {lt('Citizen Welfare & Public Scheme Assistance', 'नागरिक कल्याण एवं सार्वजनिक योजना सहायता')}
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>
              {lt('Verified Official Rules', 'सत्यापित सरकारी नियम')}
            </span>
            <span>•</span>
            <span>
<<<<<<< HEAD
              {lt('No profile storage', 'प्रोफ़ाइल सहेजी नहीं जाती')}
=======
              {language === 'hi'
                ? 'शून्य डेटा संचयन (Zero Retention)'
                : 'Zero Data Retention'}
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
            </span>
            <span>•</span>
            <button
              onClick={() => setCurrentScreen('S9')}
              className="text-slate-500 hover:text-teal-700 flex items-center gap-1 transition cursor-pointer"
              title="Admin Scheme Intelligence Monitor"
            >
              <Shield className="w-3 h-3 text-teal-600" />
              <span>{lt('Admin Monitor', 'प्रशासनिक निगरानी')}</span>
            </button>
          </div>
        </div>
      </footer>

      {/* Global Modals & Floating Drawers */}
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
