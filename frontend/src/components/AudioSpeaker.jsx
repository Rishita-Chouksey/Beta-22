import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { speakText, stopSpeaking } from '../services/speech';
import { useLanguage } from '../context/LanguageContext';

export default function AudioSpeaker({ text, className = '' }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const { language, t } = useLanguage();

  const handleToggle = (e) => {
    e?.stopPropagation();
    if (isPlaying) {
      stopSpeaking();
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      speakText(text, language, () => {
        setIsPlaying(false);
      });
    }
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      className={`inline-flex items-center justify-center rounded-xl border transition-all ${
        isPlaying
          ? 'bg-teal-700 text-white border-teal-800 shadow-sm animate-pulse'
          : 'bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-900 border-slate-200'
      } w-9 h-9 flex-shrink-0 touch-target ${className}`}
      title={isPlaying ? (language === 'hi' ? 'बोलना बंद करें' : 'Stop speaking') : t('read_aloud')}
      aria-label={isPlaying ? (language === 'hi' ? 'बोलना बंद करें' : 'Stop speaking') : t('read_aloud')}
    >
      {isPlaying ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
    </button>
  );
}
