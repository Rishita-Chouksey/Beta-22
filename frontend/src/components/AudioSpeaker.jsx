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
          ? 'bg-blue-600 text-white border-blue-600 animate-pulse'
          : 'bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-700 border-slate-200'
      } w-9 h-9 flex-shrink-0 ${className}`}
      title={isPlaying ? 'बोलना बंद करें' : t('read_aloud')}
      aria-label={t('read_aloud')}
    >
      {isPlaying ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
    </button>
  );
}
