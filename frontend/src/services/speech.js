// Speech Synthesis (Text-to-Speech)
export function speakText(text, lang = 'hi', onEnd = null) {
  if (!('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported in this browser.');
    if (onEnd) onEnd();
    return;
  }

  // Cancel any existing speech
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
  utterance.rate = 0.95; // Slightly slower for better clarity for rural citizens
  utterance.pitch = 1.0;

  if (onEnd) {
    utterance.onend = onEnd;
    utterance.onerror = onEnd;
  }

  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

// Speech Recognition (Speech-to-Text)
export function createSpeechRecognizer({ language = 'hi', onResult, onError, onEnd }) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return {
      isSupported: false,
      start: () => {
        if (onError) onError('Speech recognition is not supported in this browser. Please type your message.');
      },
      stop: () => {},
    };
  }

  const recognition = new SpeechRecognition();
  recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    if (onResult) {
      onResult(transcript);
    }
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    if (onError) onError(event.error);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  return {
    isSupported: true,
    start: () => {
      try {
        recognition.start();
      } catch (err) {
        console.warn('Recognition start error:', err);
      }
    },
    stop: () => {
      try {
        recognition.stop();
      } catch (err) {
        console.warn('Recognition stop error:', err);
      }
    },
  };
}
