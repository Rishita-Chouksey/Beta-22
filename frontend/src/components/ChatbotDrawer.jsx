import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { sendChatMessage } from '../services/api';
import { MessageSquare, X, Send, Bot, User, ExternalLink, Sparkles } from 'lucide-react';
import AudioSpeaker from './AudioSpeaker';

export default function ChatbotDrawer() {
  const { language, t } = useLanguage();
  const { isChatOpen, setIsChatOpen, activeSchemeModal, profile } = useSession();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: language === 'hi'
        ? 'नमस्ते! मैं योजनासारथी सरकारी योजना सहायक हूँ। आप मुझसे किसी भी योजना की पात्रता, आवश्यक दस्तावेज़ या आवेदन प्रक्रिया के बारे में पूछ सकते हैं।'
        : 'Namaste! I am your YojnaSarthi Assistant. Ask me about eligibility rules, required documents, or application procedures.',
      sources: []
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isChatOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isChatOpen]);

  const handleSend = async (e) => {
    e?.preventDefault();
    const query = inputValue.trim();
    if (!query || isLoading) return;

    const userMsg = { id: Date.now().toString(), sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const resp = await sendChatMessage(
        query,
        activeSchemeModal?.scheme_id || null,
        profile,
        language
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
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: language === 'hi'
            ? 'क्षमा करें, सेवा अभी व्यस्त है। कृपया आधिकारिक पोर्टल देखें।'
            : 'Sorry, the service is currently experiencing delay. Please try again.',
          sources: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="no-print fixed bottom-6 right-6 bg-slate-900 hover:bg-slate-800 text-white rounded-full p-4 shadow-xl flex items-center gap-2.5 border border-slate-700 z-40 transition-transform active:scale-95 touch-target hover:scale-105"
          aria-label={t('chat_title')}
        >
          <Bot className="w-6 h-6 text-blue-400" />
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
                <div className="w-9 h-9 rounded-xl bg-blue-600/30 flex items-center justify-center border border-blue-500/40 text-blue-400">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm leading-tight text-white">{t('chat_title')}</h3>
                  <p className="text-[11px] text-slate-400">{t('chat_disclaimer')}</p>
                </div>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/60">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {m.sender === 'bot' && (
                    <div className="w-7 h-7 rounded-lg bg-blue-900 text-white flex items-center justify-center text-xs flex-shrink-0 mt-1 shadow-xs">
                      🏛️
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed shadow-xs ${
                      m.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-br-xs'
                        : 'bg-white text-slate-800 border border-slate-200 rounded-bl-xs'
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
                            className="text-[11px] text-blue-700 hover:underline flex items-center gap-1 font-semibold"
                          >
                            <span>आधिकारिक स्रोत</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    )}
                  </div>

                  {m.sender === 'user' && (
                    <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-200 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-1">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex items-center gap-2 text-slate-500 text-xs py-2 px-2">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span>योजना नियमों से उत्तर सत्यापित हो रहा है...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-200 flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={t('chat_placeholder')}
                className="flex-1 bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm focus:bg-white focus:border-blue-600 focus:outline-hidden"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-3.5 py-2.5 rounded-xl flex items-center justify-center shadow-xs transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
