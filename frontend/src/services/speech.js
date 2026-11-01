// YojnaSarthi Speech Service: Multilingual (Hindi, English, Marathi, Bengali) Voice Recognition & Synthesis
// Strictly privacy-preserving: Zero voice audio recorded or stored on server.

// Phonetic acronym map for natural Indian language pronunciation
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
  if (lang === 'hi' || lang === 'mr') {
    for (const [pattern, replacement] of HINDI_PHONETIC_REPLACEMENTS) {
      prepared = prepared.replace(pattern, replacement);
    }
  }
  // Remove markdown bold asterisks, bullets, backticks
  prepared = prepared
    .replace(/[*#_~`]/g, '')
    .replace(/•/g, ', ')
    .replace(/\s+/g, ' ')
    .trim();
  return prepared;
}

export function getLocaleCode(lang) {
  if (lang === 'mr') return 'mr-IN';
  if (lang === 'bn') return 'bn-IN';
  if (lang === 'en') return 'en-IN';
  return 'hi-IN';
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

  if (lang === 'mr') {
    const marathiVoice = voices.find(
      (v) =>
        v.lang.toLowerCase() === 'mr-in' ||
        v.lang.toLowerCase().startsWith('mr') ||
        v.name.toLowerCase().includes('marathi') ||
        v.name.toLowerCase().includes('मराठी')
    );
    if (marathiVoice) return marathiVoice;
    // Fallback to Hindi voice if Marathi not found
    const hiFallback = voices.find((v) => v.lang.toLowerCase().startsWith('hi'));
    if (hiFallback) return hiFallback;
  } else if (lang === 'bn') {
    const bengaliVoice = voices.find(
      (v) =>
        v.lang.toLowerCase() === 'bn-in' ||
        v.lang.toLowerCase().startsWith('bn') ||
        v.name.toLowerCase().includes('bengali') ||
        v.name.toLowerCase().includes('বাংলা')
    );
    if (bengaliVoice) return bengaliVoice;
  } else if (lang === 'hi') {
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
    // English
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

let speechWatchdogTimer = null;

function speakWithBrowserSynthesis(cleanText, lang = 'hi', onEnd = null) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported in this browser.');
    if (onEnd) onEnd();
    return;
  }

  // Cancel any ongoing speech
  try {
    window.speechSynthesis.cancel();
  } catch (_) {}

  if (speechWatchdogTimer) {
    clearTimeout(speechWatchdogTimer);
    speechWatchdogTimer = null;
  }

  const utterance = new SpeechSynthesisUtterance(cleanText);
  // Keep global reference to prevent Chromium garbage-collection audio cutoff bug
  window.__activeSpeechUtterance = utterance;

  utterance.lang = getLocaleCode(lang);
  utterance.rate = lang === 'en' ? 1.0 : 0.95;
  utterance.pitch = 1.0;

  const bestVoice = getBestVoice(lang);
  if (bestVoice) {
    utterance.voice = bestVoice;
  }

  let hasEnded = false;
  let keepAliveTimer = null;

  const safeEnd = () => {
    if (!hasEnded) {
      hasEnded = true;
      if (speechWatchdogTimer) {
        clearTimeout(speechWatchdogTimer);
        speechWatchdogTimer = null;
      }
      if (keepAliveTimer) {
        clearInterval(keepAliveTimer);
        keepAliveTimer = null;
      }
      window.__activeSpeechUtterance = null;
      if (onEnd) onEnd();
    }
  };

  utterance.onend = safeEnd;
  utterance.onerror = (e) => {
    console.warn('Speech synthesis notice:', e);
    safeEnd();
  };

  // Keep Chromium synthesis active (prevents speech cut-off on longer sentences)
  keepAliveTimer = setInterval(() => {
    if (!hasEnded && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      } else {
        clearInterval(keepAliveTimer);
      }
    } else {
      clearInterval(keepAliveTimer);
    }
  }, 4000);

  // Watchdog timer: safety net allowing ample time (250ms/char, min 15s) so sentences are NEVER cut off mid-speech
  const expectedDurationMs = Math.max(15000, cleanText.length * 250);
  speechWatchdogTimer = setTimeout(() => {
    if (!hasEnded) {
      console.warn('Speech synthesis watchdog maximum timeout reached, completing turn.');
      safeEnd();
    }
  }, expectedDurationMs);

  try {
    window.speechSynthesis.speak(utterance);
  } catch (err) {
    console.warn('Speech synthesis speak exception:', err);
    safeEnd();
  }
}

// Speech Synthesis (Text-to-Speech) using native browser SpeechSynthesis engine
export function speakText(text, lang = 'hi', onEnd = null) {
  stopSpeaking();

  const cleanText = prepareTextForSpeech(text, lang);
  if (!cleanText.trim()) {
    if (onEnd) onEnd();
    return;
  }

  speakWithBrowserSynthesis(cleanText, lang, onEnd);
}

export function stopSpeaking() {
  if (speechWatchdogTimer) {
    clearTimeout(speechWatchdogTimer);
    speechWatchdogTimer = null;
  }
  window.__activeSpeechUtterance = null;
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (_) {}
  }
}

// Speech Recognition (Speech-to-Text) with robust live capture and continuous audio support
export function createSpeechRecognizer({ language = 'hi', onInterim, onFinal, onError, onStateChange }) {
  if (typeof window === 'undefined') {
    return { isSupported: false, start: () => {}, stop: () => {}, cancel: () => {} };
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return {
      isSupported: false,
      start: () => {
        if (onError) onError('browser_unsupported');
      },
      stop: () => {},
      cancel: () => {},
    };
  }

  let recognition = null;
  let isIntentionallyListening = false;
  let accumulatedTranscript = '';
  let latestLiveTranscript = '';

  const initRecognition = () => {
    try {
      recognition = new SpeechRecognition();
    } catch (e) {
      console.warn('SpeechRecognition initialization error:', e);
      return;
    }

    recognition.lang = getLocaleCode(language);
    recognition.continuous = true; // Listen continuously until user pauses or clicks stop
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      if (onStateChange) onStateChange(true);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let finalized = '';

      for (let i = 0; i < event.results.length; ++i) {
        const item = event.results[i];
        if (item.isFinal) {
          finalized += item[0].transcript + ' ';
        } else {
          interim += item[0].transcript;
        }
      }

      accumulatedTranscript = finalized;
      const fullCurrentText = (finalized + interim).trim();
      latestLiveTranscript = fullCurrentText;

      if (onInterim) {
        onInterim(fullCurrentText);
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition event:', event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        isIntentionallyListening = false;
        if (onError) onError('permission_denied');
        if (onStateChange) onStateChange(false);
      } else if (event.error === 'no-speech') {
        // User paused briefly, keep listening
      } else if (event.error === 'network') {
        if (onError) onError('network_error');
      }
    };

    recognition.onend = () => {
      if (isIntentionallyListening) {
        // Automatically reconnect if browser closed the connection while user is still speaking
        setTimeout(() => {
          if (isIntentionallyListening && recognition) {
            try {
              recognition.start();
            } catch (_) {}
          }
        }, 150);
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
      latestLiveTranscript = '';
      isIntentionallyListening = true;

      try {
        recognition?.start();
      } catch (err) {
        if (err.name !== 'InvalidStateError') {
          console.warn('Restarting recognition engine:', err);
          try {
            recognition?.abort();
            setTimeout(() => {
              if (isIntentionallyListening) {
                try {
                  recognition?.start();
                } catch (_) {}
              }
            }, 100);
          } catch (_) {}
        }
      }
    },
    stop: () => {
      isIntentionallyListening = false;
      try {
        recognition?.stop();
      } catch (err) {
        console.warn('Recognition stop notice:', err);
      }
      if (onStateChange) onStateChange(false);

      // Give priority to accumulated transcript, then latestLiveTranscript
      const finalResult = (accumulatedTranscript || latestLiveTranscript).trim();
      if (onFinal) {
        onFinal(finalResult);
      }
    },
    cancel: () => {
      isIntentionallyListening = false;
      accumulatedTranscript = '';
      latestLiveTranscript = '';
      try {
        recognition?.abort();
      } catch (_) {}
      if (onStateChange) onStateChange(false);
    },
  };
}
