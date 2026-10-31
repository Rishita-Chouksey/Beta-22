import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { sendChatMessage } from '../services/api';
import { MessageSquare, X, Send, Bot, User, ExternalLink, Sparkles, HelpCircle, ArrowRight, FileCheck2 } from 'lucide-react';
import AudioSpeaker from './AudioSpeaker';
import VoiceMic from './VoiceMic';

export default function ChatbotDrawer() {
  const { language, t } = useLanguage();
  const { isChatOpen, setIsChatOpen, activeSchemeModal, profile, openDocumentGuide } = useSession();
  
  const initialBotWelcome = {
    id: 'welcome',
    sender: 'bot',
    text: language === 'hi'
      ? 'नमस्ते! मैं योजनासारथी सरकारी योजना सहायक हूँ। आप मुझसे किसी भी सरकारी योजना की पात्रता, आवश्यक दस्तावेज़ या आवेदन प्रक्रिया के बारे में पूछ सकते हैं।'
      : 'Namaste! I am your YojnaSarthi Government Scheme Assistant. Ask me about scheme eligibility rules, required documents, or official application procedures.',
    sources: []
  };

  const [messages, setMessages] = useState([initialBotWelcome]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isChatOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isChatOpen]);

  // Update initial welcome if user hasn't messaged yet
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === 'welcome') {
        return [initialBotWelcome];
      }
      return prev;
    });
  }, [language]);

  const quickPrompts = language === 'hi' ? [
    { label: '🎓 MMVY छात्रवृत्ति क्या है?', text: 'MMVY क्या है और इसके लिए क्या पात्रता है?' },
    { label: '👩 विधवाओं हेतु योजनाएं', text: 'विधवा महिलाओं के लिए कौन-कौन सी सरकारी योजनाएं उपलब्ध हैं?' },
    { label: '🌾 किसानों हेतु योजनाएं', text: 'किसानों के लिए कौन सी कल्याणकारी योजनाएं उपलब्ध हैं?' },
    { label: '📑 आय प्रमाण पत्र कैसे बनवाएं?', text: 'आय प्रमाण पत्र कैसे और कहाँ से बनवाएं?' },
    { label: '💰 क्या 2 छात्रवृत्ति एक साथ मिल सकती हैं?', text: 'क्या दो छात्रवृत्तियां एक साथ मिल सकती हैं?' },
    { label: '🌸 लाड़ली बहना योजना', text: 'लाड़ली बहना योजना की पात्रता और लाभ क्या हैं?' }
  ] : [
    { label: '🎓 What is MMVY?', text: 'What is MMVY and who is eligible?' },
    { label: '👩 Schemes for Widows', text: 'Are there any government schemes for widows?' },
    { label: '🌾 Schemes for Farmers', text: 'Which schemes are available for farmers?' },
    { label: '📑 How to get Income Cert?', text: 'How can I get an income certificate?' },
    { label: '💰 Two scholarships at once?', text: 'Can I receive two scholarships simultaneously?' },
    { label: '🌸 Ladli Behna Yojana', text: 'What is Ladli Behna Yojana and its benefits?' }
  ];

  const sendMessageWithText = async (textToSend) => {
    const query = textToSend.trim();
    if (!query || isLoading) return;

    const userMsg = { id: Date.now().toString(), sender: 'user', text: query };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInputValue('');
    setIsLoading(true);

    // Prepare history payload for conversational context
    const historyPayload = updatedMessages
      .filter((m) => m.id !== 'welcome')
      .map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        text: m.text
      }));

    try {
      const resp = await sendChatMessage(
        query,
        activeSchemeModal?.scheme_id || null,
        profile,
        language,
        historyPayload
      );

      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: resp.reply,
        sources: resp.grounded_sources || [],
        disclaimer: resp.disclaimer
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: language === 'hi'
            ? 'क्षमा करें, सेवा अभी व्यस्त है। कृपया आधिकारिक पोर्टल देखें।'
            : 'Sorry, the service is currently experiencing delay. Please try again or visit official portals.',
          sources: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = (e) => {
    e?.preventDefault();
    sendMessageWithText(inputValue);
  };

  const handleVoiceTranscript = (spokenText) => {
    if (spokenText && spokenText.trim()) {
      setInputValue((prev) => (prev ? `${prev} ${spokenText}` : spokenText));
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="no-print fixed bottom-6 right-6 bg-slate-900 hover:bg-slate-800 text-white rounded-full p-4 shadow-xl flex items-center gap-2.5 border border-teal-500/30 z-40 transition-transform active:scale-95 touch-target hover:scale-105"
          aria-label={t('chat_title')}
        >
          <Bot className="w-6 h-6 text-teal-400" />
          <span className="text-xs font-bold pr-1 hidden sm:inline">{t('chat_title')}</span>
        </button>
      )}

      {/* Slide-over Drawer */}
      {isChatOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/40 backdrop-blur-xs animate-fade-in">
          <div className="bg-white w-full sm:max-w-md h-full flex flex-col shadow-2xl border-l border-slate-200">
            {/* Header */}
            <div className="bg-slate-900 text-white px-5 py-4 flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-teal-500/20 flex items-center justify-center border border-teal-400/30 text-teal-300">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm leading-tight text-white">{t('chat_title')}</h3>
                  <p className="text-[11px] text-teal-300/80">{t('chat_disclaimer')}</p>
                </div>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Document Guide Quick Hint */}
            <div className="bg-amber-50/90 border-b border-amber-200 px-4 py-2 flex items-center justify-between text-xs text-amber-900">
              <span className="flex items-center gap-1.5 font-medium">
                <FileCheck2 className="w-3.5 h-3.5 text-amber-700" />
                <span>{language === 'hi' ? 'दस्तावेज़ों का नमूना देखना चाहते हैं?' : 'Need document sample previews?'}</span>
              </span>
              <button
                type="button"
                onClick={() => {
                  setIsChatOpen(false);
                  openDocumentGuide();
                }}
                className="font-bold text-amber-800 hover:text-amber-950 underline cursor-pointer"
              >
                {language === 'hi' ? 'गाइड खोलें' : 'Open Guide'}
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/70">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {m.sender === 'bot' && (
                    <div className="w-7 h-7 rounded-lg bg-slate-900 text-white flex items-center justify-center text-xs flex-shrink-0 mt-1 shadow-xs border border-teal-500/30">
                      🏛️
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed shadow-xs ${
                      m.sender === 'user'
                        ? 'bg-blue-700 text-white rounded-br-xs'
                        : 'bg-white text-slate-900 border border-slate-200 rounded-bl-xs'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{m.text}</p>

                    {m.sender === 'bot' && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                        <AudioSpeaker text={m.text} className="w-7 h-7" />
                        {m.sources && m.sources.length > 0 && (
                          <a
                            href={m.sources[0]}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-teal-700 hover:underline flex items-center gap-1 font-semibold"
                          >
                            <span>{language === 'hi' ? 'आधिकारिक स्रोत' : 'Official Source'}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    )}
                  </div>

                  {m.sender === 'user' && (
                    <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-900 flex items-center justify-center text-xs flex-shrink-0 mt-1">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-2.5 justify-start items-center">
                  <div className="w-7 h-7 rounded-lg bg-slate-900 text-white flex items-center justify-center text-xs flex-shrink-0 border border-teal-500/30">
                    🏛️
                  </div>
                  <div className="bg-white border border-slate-200 rounded-2xl px-4 py-2.5 text-xs text-slate-600 flex items-center gap-2 shadow-2xs">
                    <span className="font-semibold text-slate-700">
                      {language === 'hi' ? 'उत्तर तैयार हो रहा है' : 'YojnaSarthi is typing'}
                    </span>
                    <div className="flex items-center gap-1 pl-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-teal-600 typing-dot-1" />
                      <span className="w-1.5 h-1.5 rounded-full bg-teal-600 typing-dot-2" />
                      <span className="w-1.5 h-1.5 rounded-full bg-teal-600 typing-dot-3" />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestion Chips */}
            <div className="px-4 py-2 bg-white border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
              {quickPrompts.map((qp, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => sendMessageWithText(qp.text)}
                  className="text-[11px] font-semibold text-slate-700 bg-slate-100 hover:bg-teal-50 hover:text-teal-900 border border-slate-200 px-3 py-1 rounded-full whitespace-nowrap transition-colors flex-shrink-0"
                >
                  {qp.label}
                </button>
              ))}
            </div>

            {/* Input Form with Text & Voice */}
            <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-200 space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={t('chat_placeholder')}
                  className="flex-1 text-xs sm:text-sm p-3 rounded-xl border border-slate-300 focus:border-teal-600 focus:outline-hidden bg-slate-50/50"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isLoading}
                  className="w-10 h-10 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white flex items-center justify-center transition-all flex-shrink-0 shadow-xs"
                  aria-label="Send"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500 px-1">
                <VoiceMic onTranscriptChange={handleVoiceTranscript} />
                <span className="text-[11px] text-slate-400">
                  {language === 'hi' ? 'गोपनीय एवं सुरक्षित' : 'Zero PII logged'}
                </span>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
