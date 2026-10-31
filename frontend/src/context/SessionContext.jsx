import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

const SessionContext = createContext();

const IDLE_WARNING_TIME_MS = 9 * 60 * 1000; // 9 minutes
const AUTO_CLEAR_TIME_MS = 10 * 60 * 1000;   // 10 minutes

export function SessionProvider({ children }) {
  // In-memory tab state ONLY. No localStorage or sessionStorage used for personal citizen data!
  const [currentScreen, setCurrentScreen] = useState('S0'); // 'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8' (Document Guide)
  const [profile, setProfile] = useState({});
  const [evaluationResults, setEvaluationResults] = useState(null);
  const [activeSchemeModal, setActiveSchemeModal] = useState(null);
  const [checklistData, setChecklistData] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Document Guide state & cross-navigation
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [docGuideReturnScreen, setDocGuideReturnScreen] = useState(null);

  // Privacy & Session Timeout modals
  const [showClearConfirmModal, setShowClearConfirmModal] = useState(false);
  const [showIdleWarningModal, setShowIdleWarningModal] = useState(false);

  const lastActivityRef = useRef(Date.now());
  const idleTimerRef = useRef(null);

  const openDocumentGuide = (docId = null, returnScreen = null) => {
    setSelectedDocId(docId);
    if (returnScreen) {
      setDocGuideReturnScreen(returnScreen);
    }
    setCurrentScreen('S8');
    lastActivityRef.current = Date.now();
  };

  const resetSession = () => {
    setProfile({});
    setEvaluationResults(null);
    setActiveSchemeModal(null);
    setChecklistData(null);
    setSelectedDocId(null);
    setDocGuideReturnScreen(null);
    setShowClearConfirmModal(false);
    setShowIdleWarningModal(false);
    setCurrentScreen('S0');
    lastActivityRef.current = Date.now();
  };

  const updateProfile = (newFields) => {
    setProfile((prev) => ({
      ...prev,
      ...newFields,
    }));
    lastActivityRef.current = Date.now();
  };

  // Inactivity tracking
  useEffect(() => {
    const handleUserActivity = () => {
      lastActivityRef.current = Date.now();
      if (showIdleWarningModal) {
        setShowIdleWarningModal(false);
      }
    };

    window.addEventListener('mousemove', handleUserActivity);
    window.addEventListener('keydown', handleUserActivity);
    window.addEventListener('touchstart', handleUserActivity);
    window.addEventListener('scroll', handleUserActivity);

    idleTimerRef.current = setInterval(() => {
      const elapsed = Date.now() - lastActivityRef.current;
      if (elapsed >= AUTO_CLEAR_TIME_MS) {
        resetSession();
      } else if (elapsed >= IDLE_WARNING_TIME_MS && !showIdleWarningModal) {
        setShowIdleWarningModal(true);
      }
    }, 15000); // Check every 15s

    return () => {
      window.removeEventListener('mousemove', handleUserActivity);
      window.removeEventListener('keydown', handleUserActivity);
      window.removeEventListener('touchstart', handleUserActivity);
      window.removeEventListener('scroll', handleUserActivity);
      if (idleTimerRef.current) clearInterval(idleTimerRef.current);
    };
  }, [showIdleWarningModal]);

  return (
    <SessionContext.Provider
      value={{
        currentScreen,
        setCurrentScreen,
        profile,
        setProfile,
        updateProfile,
        evaluationResults,
        setEvaluationResults,
        activeSchemeModal,
        setActiveSchemeModal,
        checklistData,
        setChecklistData,
        isChatOpen,
        setIsChatOpen,
        showClearConfirmModal,
        setShowClearConfirmModal,
        showIdleWarningModal,
        setShowIdleWarningModal,
        selectedDocId,
        setSelectedDocId,
        docGuideReturnScreen,
        setDocGuideReturnScreen,
        openDocumentGuide,
        resetSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
