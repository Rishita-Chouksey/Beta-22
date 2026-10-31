import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, AlertCircle, Volume2, Loader2 } from 'lucide-react';
import { createSpeechRecognizer } from '../services/speech';
import { useLanguage } from '../context/LanguageContext';

export default function VoiceMic({ onTranscriptChange, onLiveInterim = null, className = '' }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [hasCapturedSpeech, setHasCapturedSpeech] = useState(false);
  const { language, t, lt } = useLanguage();
  
  const recognizerRef = useRef(null);
  const timerRef = useRef(null);
  const latestTextRef = useRef('');

  useEffect(() => {
    recognizerRef.current = createSpeechRecognizer({
      language,
      onInterim: (liveText) => {
        latestTextRef.current = liveText;
        setHasCapturedSpeech(Boolean(liveText.trim()));
        if (onLiveInterim) {
          onLiveInterim(liveText);
        }
      },
      onFinal: (finalText) => {
        const textToSubmit = finalText || latestTextRef.current;
        if (textToSubmit && textToSubmit.trim()) {
          if (onTranscriptChange) {
            onTranscriptChange(textToSubmit.trim());
          }
        }
      },
      onError: (errCode) => {
        if (errCode === 'permission_denied') {
          setErrorMessage(
            lt('Microphone permission blocked. Please allow mic access in your browser address bar.', 'माइक्रोफ़ोन की अनुमति अस्वीकृत है। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन की अनुमति दें।')
          );
        } else if (errCode === 'browser_unsupported') {
          setErrorMessage(
            lt('Speech recognition is not supported in this browser. Please use text typing.', 'इस ब्राउज़र में ध्वनि पहचान समर्थित नहीं है। कृपया लिखकर विवरण दर्ज करें।')
          );
        } else if (errCode === 'network_error') {
          setErrorMessage(
            lt('Voice recognition network error. You can continue by typing.', 'ध्वनि सेवा नेटवर्क समस्या। आप नीचे लिखकर भी विवरण दर्ज कर सकते हैं।')
          );
        }
      },
      onStateChange: (active) => {
        setIsRecording(active);
      }
    });

    return () => {
      if (recognizerRef.current) {
        recognizerRef.current.cancel();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [language, onTranscriptChange, onLiveInterim]);

  // Timer while recording
  useEffect(() => {
    if (isRecording) {
      setRecordingSeconds(0);
      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  const handleStartRecording = () => {
    setErrorMessage('');
    latestTextRef.current = '';
    setHasCapturedSpeech(false);
    recognizerRef.current?.start();
  };

  const handleStopRecording = () => {
    recognizerRef.current?.stop();
    setIsRecording(false);
  };

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins}:${rem < 10 ? '0' : ''}${rem}`;
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-3">
        {!isRecording ? (
          <button
            type="button"
            onClick={handleStartRecording}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-50 hover:bg-teal-100/80 text-teal-900 border border-teal-300 font-semibold text-xs sm:text-sm shadow-2xs hover:shadow-xs transition-all active:scale-98 min-h-[44px] ${className}`}
            title={t('voice_input')}
            aria-label={t('voice_input')}
          >
            <Mic className="w-4 h-4 text-teal-700" />
            <span>{lt('Speak with Voice', 'बोलकर बताएं')}</span>
          </button>
        ) : (
          <div className="inline-flex items-center gap-3 p-1.5 pr-3 rounded-xl bg-rose-50 border border-rose-300 shadow-sm animate-pulse">
            {/* Live recording pulsing indicator */}
            <div className="flex items-center gap-2 px-2.5 py-1 text-xs font-bold text-rose-800">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-ping inline-block" />
              <span>{lt('Recording...', 'सुन रहे हैं...')}</span>
              <span className="font-mono text-rose-950 font-extrabold">{formatTime(recordingSeconds)}</span>
            </div>

            {/* Obvious Manual Stop Button */}
            <button
              type="button"
              onClick={handleStopRecording}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-xs transition-all active:scale-95 min-h-[36px]"
              title={t('voice_stop')}
              aria-label={t('voice_stop')}
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>{lt('Stop Recording', 'रिकॉर्डिंग रोकें (Stop)')}</span>
            </button>
          </div>
        )}

        {isRecording && (
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            {lt('Speak naturally with pauses; click Stop when finished.', 'बोलते रहें; बोलने के बाद "रिकॉर्डिंग रोकें" दबाएं।')}
          </span>
        )}
      </div>

      {/* Permission or error message alert */}
      {errorMessage && (
        <div className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-900 text-xs">
          <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
          <span className="leading-snug">{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
