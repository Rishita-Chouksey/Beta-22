import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { createSpeechRecognizer } from '../services/speech';
import { useLanguage } from '../context/LanguageContext';

export default function VoiceMic({ onTranscriptChange, className = '' }) {
  const [isListening, setIsListening] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const { language, t } = useLanguage();
  const recognizerRef = useRef(null);

  useEffect(() => {
    recognizerRef.current = createSpeechRecognizer({
      language,
      onResult: (text) => {
        if (onTranscriptChange) {
          onTranscriptChange(text);
        }
      },
      onError: (err) => {
        setIsListening(false);
        setErrorMsg('Microphone hint: Speak clearly or use text typing.');
      },
      onEnd: () => {
        setIsListening(false);
      },
    });

    return () => {
      if (recognizerRef.current) {
        recognizerRef.current.stop();
      }
    };
  }, [language, onTranscriptChange]);

  const toggleListening = () => {
    setErrorMsg('');
    if (isListening) {
      recognizerRef.current?.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognizerRef.current?.start();
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={toggleListening}
        className={`w-11 h-11 rounded-xl flex items-center justify-center transition-all ${
          isListening
            ? 'bg-rose-600 text-white mic-pulse shadow-md'
            : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200'
        } ${className}`}
        title={isListening ? t('voice_stop') : t('voice_input')}
        aria-label={isListening ? t('voice_stop') : t('voice_input')}
      >
        {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
      </button>

      {errorMsg && (
        <span className="text-[11px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
          {errorMsg}
        </span>
      )}
    </div>
  );
}
