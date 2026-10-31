// YojnaSarthi Speech Service: Bilingual Hindi & English Voice Recognition & Synthesis
// Strictly privacy-preserving: Zero voice audio recorded or stored on server.

// Phonetic acronym map for natural Hindi pronunciation
const HINDI_PHONETIC_REPLACEMENTS = [
  [/\bMMVY\b/gi, 'एम.एम.वी.वाई.'],
  [/\bPM-KISAN\b/gi, 'पीएम किसान'],
  [/\bPMKISAN\b/gi, 'पीएम किसान'],
  [/\bPM-JAY\b/gi, 'पीएम जन आरोग्य'],
  [/\bPMJAY\b/gi, 'पीएम जन आरोग्य'],
  [/\bPMAY-G\b/gi, 'पीएम आवास योजना ग्रामीण'],
  [/\bPMAY\b/gi, 'पीएम आवास'],
  [/\bIGNWPS\b/gi, 'इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना'],
  [/\bBPL\b/gi, 'बीपीएल'],
  [/\bDBT\b/gi, 'डीबीटी'],
  [/\bNPCI\b/gi, 'एनपीसीआई'],
  [/\bUIDAI\b/gi, 'यूआईडीएआई'],
  [/\bCSC\b/gi, 'सीएससी'],
  [/\bha\b/gi, 'हेक्टेयर'],
  [/\bha\.\b/gi, 'हेक्टेयर'],
  [/₹\s*(\d+)/g, '$1 रुपये'],
];

function prepareTextForSpeech(text, lang) {
  if (!text) return '';
  let prepared = text;
  if (lang === 'hi') {
    for (const [pattern, replacement] of HINDI_PHONETIC_REPLACEMENTS) {
      prepared = prepared.replace(pattern, replacement);
    }
  }
  // Remove markdown bold asterisks and bullets
  prepared = prepared.replace(/[*#_~`]/g, '').replace(/•/g, ', ');
  return prepared;
}

// Global voice cache
let cachedVoices = [];
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  cachedVoices = window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => {
    cachedVoices = window.speechSynthesis.getVoices();
  };
}

export function getBestVoice(lang = 'hi') {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;
  const voices = cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices();

  if (lang === 'hi') {
    // 1. Search for hi-IN or Hindi named voices
    const hindiVoice = voices.find(
      (v) =>
        v.lang.toLowerCase() === 'hi-in' ||
        v.lang.toLowerCase().startsWith('hi') ||
        v.name.toLowerCase().includes('hindi') ||
        v.name.toLowerCase().includes('हिन्दी') ||
        v.name.toLowerCase().includes('swara') ||
        v.name.toLowerCase().includes('hemant') ||
        v.name.toLowerCase().includes('kalpana')
    );
    if (hindiVoice) return hindiVoice;
  } else {
    // 1. Search for en-IN first, then general en
    const indianEnglish = voices.find(
      (v) =>
        v.lang.toLowerCase() === 'en-in' ||
        v.name.toLowerCase().includes('india') ||
        v.name.toLowerCase().includes('ravi') ||
        v.name.toLowerCase().includes('heera')
    );
    if (indianEnglish) return indianEnglish;

    const anyEnglish = voices.find((v) => v.lang.toLowerCase().startsWith('en'));
    if (anyEnglish) return anyEnglish;
  }

  return null;
}

// Speech Synthesis (Text-to-Speech)
export function speakText(text, lang = 'hi', onEnd = null) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported in this browser.');
    if (onEnd) onEnd();
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  const cleanText = prepareTextForSpeech(text, lang);
  if (!cleanText.trim()) {
    if (onEnd) onEnd();
    return;
  }

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
  utterance.rate = lang === 'hi' ? 0.90 : 0.95; // Slightly measured rate for maximum rural clarity
  utterance.pitch = 1.0;

  const bestVoice = getBestVoice(lang);
  if (bestVoice) {
    utterance.voice = bestVoice;
  }

  let hasEnded = false;
  const safeEnd = () => {
    if (!hasEnded) {
      hasEnded = true;
      if (onEnd) onEnd();
    }
  };

  utterance.onend = safeEnd;
  utterance.onerror = (e) => {
    console.warn('Speech synthesis error/interrupted:', e);
    safeEnd();
  };

  // Chrome bug workaround: speech synthesis can stall on long text unless resumed
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

// Speech Recognition (Speech-to-Text) with continuous manual recording
export function createSpeechRecognizer({ language = 'hi', onInterim, onFinal, onError, onStateChange }) {
  if (typeof window === 'undefined') {
    return { isSupported: false, start: () => { }, stop: () => { } };
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return {
      isSupported: false,
      start: () => {
        if (onError) onError('browser_unsupported');
      },
      stop: () => { },
    };
  }

  let recognition = null;
  let isIntentionallyListening = false;
  let accumulatedTranscript = '';

  const initRecognition = () => {
    recognition = new SpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = true; // DO NOT auto-stop on silence!
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      if (onStateChange) onStateChange(true);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let newlyFinalized = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const item = event.results[i];
        if (item.isFinal) {
          newlyFinalized += item[0].transcript + ' ';
        } else {
          interim += item[0].transcript;
        }
      }

      if (newlyFinalized) {
        accumulatedTranscript += newlyFinalized;
      }

      const currentLive = (accumulatedTranscript + interim).trim();
      if (onInterim) {
        onInterim(currentLive);
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition warning:', event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        isIntentionallyListening = false;
        if (onError) onError('permission_denied');
        if (onStateChange) onStateChange(false);
      } else if (event.error === 'no-speech') {
        // Natural user pause, do not stop recording!
      } else if (event.error === 'network') {
        if (onError) onError('network_error');
      }
    };

    recognition.onend = () => {
      // If user did NOT manually press stop, auto-restart seamlessly
      if (isIntentionallyListening) {
        try {
          recognition.start();
        } catch (e) {
          // Restart quickly
          setTimeout(() => {
            if (isIntentionallyListening) {
              try { recognition.start(); } catch (_) { }
            }
          }, 250);
        }
      } else {
        if (onStateChange) onStateChange(false);
      }
    };
  };

  initRecognition();

  return {
    isSupported: true,
    start: () => {
      accumulatedTranscript = '';
      isIntentionallyListening = true;
      try {
        recognition.start();
      } catch (err) {
        console.warn('Recognition start exception:', err);
      }
    },
    stop: () => {
      isIntentionallyListening = false;
      try {
        recognition.stop();
      } catch (err) {
        console.warn('Recognition stop exception:', err);
      }
      if (onStateChange) onStateChange(false);
      if (onFinal) {
        onFinal(accumulatedTranscript.trim());
      }
    },
    cancel: () => {
      isIntentionallyListening = false;
      accumulatedTranscript = '';
      try {
        recognition.abort();
      } catch (_) { }
      if (onStateChange) onStateChange(false);
    }
  };
}
