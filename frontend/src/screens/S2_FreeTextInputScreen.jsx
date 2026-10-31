import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { parseFreeTextDescription, evaluateCitizenProfile } from '../services/api';
import { createSpeechRecognizer, speakText, stopSpeaking } from '../services/speech';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  CheckCircle2,
  ShieldCheck,
  Send,
  Zap,
  HelpCircle,
  Play,
  Pause,
  MessageSquare,
  Award
} from 'lucide-react';

export default function S2_FreeTextInputScreen() {
<<<<<<< HEAD
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen, setProfile } = useSession();
=======
  const { language, t } = useLanguage();
  const { setCurrentScreen, setProfile, setEvaluationResults } = useSession();
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636

  // Voice Interaction States: 'idle' | 'listening' | 'processing' | 'speaking'
  const [voiceState, setVoiceState] = useState('idle');
  const [liveInterim, setLiveInterim] = useState('');
  const [typedInput, setTypedInput] = useState('');
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [processingStep, setProcessingStep] = useState(0);

<<<<<<< HEAD
  const samplePrompts = [
    {
      label_hi: '🌾 किसान उदाहरण (Farmer)',
      label_en: '🌾 Farmer example',
      text: lt('I am a 48 year old farmer living in Sehore, Madhya Pradesh with 1.5 hectares of land and annual family income of 65000 INR.', 'मैं 48 साल का किसान हूँ, मध्य प्रदेश के सीहोर जिले में रहता हूँ। मेरे पास 1.5 हेक्टेयर खेती की जमीन है और वार्षिक आय 65 हजार रुपये है।')
    },
    {
      label_hi: '👩 विधवा महिला उदाहरण (Widow)',
      label_en: '👩 Widow example',
      text: lt('I am a 52 year old widow living in Madhya Pradesh. We have a BPL ration card and annual income under 25000.', 'मैं 52 वर्ष की महिला हूँ, मेरे पति का देहांत हो चुका है। मेरे पास बीपीएल राशन कार्ड है और मैं मध्य प्रदेश में रहती हूँ।')
    },
    {
      label_hi: '🎓 कॉलेज छात्र उदाहरण (Student)',
      label_en: '🎓 Student example',
      text: lt('I am a 19 year old student from MP with 86% marks in 12th board exams and enrolled in an engineering degree.', 'मैं 19 साल का छात्र हूँ, मध्य प्रदेश का मूल निवासी हूँ। 12वीं बोर्ड में मेरे 86% अंक आए हैं और मैंने बी.टेक इंजीनियरिंग कॉलेज में प्रवेश लिया है।')
=======
  // Accumulated Citizen Profile (grows turn by turn)
  const [accumulatedProfile, setAccumulatedProfile] = useState({});
  const [confirmedFields, setConfirmedFields] = useState([]);

  // Conversational History: [{ id, sender: 'ai'|'citizen', text, timestamp, extracted: {} }]
  const [conversation, setConversation] = useState([]);

  const recognizerRef = useRef(null);
  const chatScrollRef = useRef(null);
  const speechTimerRef = useRef(null);

  // Initial AI Voice Welcome
  useEffect(() => {
    const welcomeText =
      language === 'hi'
        ? 'नमस्ते! मैं आपका योजनासारथी दो-तरफ़ा आवाज़ सहायक हूँ। अपने बारे में बताएं—जैसे आपकी आयु, काम, राज्य या परिवार—ताकि मैं आपकी पात्र सरकारी योजनाएं खोज सकूँ।'
        : 'Namaste! I am your YojnaSarthi two-way voice assistant. Speak naturally about yourself—your age, work, state, or family—so I can discover your eligible welfare schemes.';

    const initialMsg = {
      id: 'welcome-1',
      sender: 'ai',
      text: welcomeText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setConversation([initialMsg]);

    // Initial polite voice greeting
    if (isAudioEnabled) {
      setVoiceState('speaking');
      speakText(welcomeText, language, () => {
        setVoiceState('idle');
      });
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
    }

    return () => {
      stopSpeaking();
      if (recognizerRef.current) {
        recognizerRef.current.cancel();
      }
    };
  }, [language]);

  // Auto-scroll chat history to latest message
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [conversation, liveInterim, voiceState]);

  // Initialize Speech Recognizer
  useEffect(() => {
    recognizerRef.current = createSpeechRecognizer({
      language,
      onInterim: (text) => {
        setLiveInterim(text);
      },
      onFinal: (finalText) => {
        const textToProcess = (finalText || liveInterim).trim();
        setLiveInterim('');
        if (textToProcess) {
          handleCitizenTurn(textToProcess);
        } else {
          setVoiceState('idle');
        }
      },
      onError: (err) => {
        console.warn('Speech error:', err);
        setVoiceState('idle');
      },
      onStateChange: (active) => {
        if (!active && voiceState === 'listening') {
          // Handled via onFinal
        }
      },
    });

    return () => {
      if (recognizerRef.current) {
        recognizerRef.current.cancel();
      }
    };
  }, [language, liveInterim, voiceState, accumulatedProfile]);

  // Start Mic Listening
  const startListening = () => {
    stopSpeaking();
    setLiveInterim('');
    setVoiceState('listening');
    try {
      recognizerRef.current?.start();
    } catch (e) {
      console.warn('Mic start error:', e);
    }
  };

  // Stop Mic Listening & Trigger Processing
  const stopListening = () => {
    try {
      recognizerRef.current?.stop();
    } catch (e) {
      console.warn('Mic stop error:', e);
    }
  };

  // Analyze Profile & Compute Follow-up Question
  const computeNextFollowup = (profile) => {
    const isHi = language === 'hi';

    // 1. Domicile State
    if (!profile.state) {
      return {
        question: isHi
          ? 'कृपया अपने गृह राज्य (Domicile State) का नाम बताएं, जैसे मध्य प्रदेश या महाराष्ट्र?'
          : 'Could you please mention your state of residence, such as Madhya Pradesh or Maharashtra?',
        targetField: 'state'
      };
    }

    // 2. Age
    if (!profile.age) {
      return {
        question: isHi
          ? 'आपकी उम्र (आयु) कितने वर्ष है?'
          : 'Could you share your approximate age in years?',
        targetField: 'age'
      };
    }

    // 3. Occupation
    if (!profile.occupation) {
      return {
        question: isHi
          ? 'आप क्या कार्य करते हैं? जैसे कि किसान, छात्र, गृहिणी, मजदूर, या स्वरोजगार?'
          : 'What is your current occupation—for instance, a farmer, student, homemaker, laborer, or self-employed?',
        targetField: 'occupation'
      };
    }

    // 4. Farmer Specifics: Landholding & Pucca House
    if (profile.occupation === 'farmer') {
      if (profile.landholding_hectares === undefined || profile.landholding_hectares === null) {
        return {
          question: isHi
            ? 'बहुत बढ़िया! PM-किसान योजना की पात्रता के लिए, आपके पास कितने हेक्टेयर या एकड़ कृषि भूमि है?'
            : 'Excellent! To check PM-KISAN entitlement, approximately how much agricultural land (hectares or acres) do you own?',
          targetField: 'landholding_hectares'
        };
      }
      if (profile.has_pucca_house === undefined || profile.has_pucca_house === null) {
        return {
          question: isHi
            ? 'पीएम आवास योजना (PMAY-G) के लिए, क्या आपके पास पहले से पक्का मकान है, या कच्चा घर है?'
            : 'For PM Awas Yojana (PMAY-G) housing grants, do you already own a pucca concrete house, or a kutcha dwelling?',
          targetField: 'has_pucca_house'
        };
      }
      if (profile.bpl_card_holder === undefined || profile.bpl_card_holder === null) {
        return {
          question: isHi
            ? 'क्या आपके परिवार के पास बीपीएल (गरीबी रेखा) राशन कार्ड है?'
            : 'Does your family hold a BPL (Below Poverty Line) or Antyodaya ration card?',
          targetField: 'bpl_card_holder'
        };
      }
    }

    // 5. Student Specifics: Class 12 Marks & College Admission
    if (profile.occupation === 'student') {
      if (profile.student_class12_marks_percent === undefined || profile.student_class12_marks_percent === null) {
        return {
          question: isHi
            ? 'मुख्यमंत्री मेधावी विद्यार्थी योजना (MMVY) के लिए, 12वीं बोर्ड परीक्षा में आपके कितने प्रतिशत (%) अंक आए हैं?'
            : 'For the MMVY Scholarship, what percentage of marks did you secure in your Class 12th board exams?',
          targetField: 'student_class12_marks_percent'
        };
      }
      if (profile.annual_income === undefined || profile.annual_income === null) {
        return {
          question: isHi
            ? 'छात्रवृत्ति के आय प्रमाण पत्र हेतु, आपके परिवार की अनुमानित वार्षिक आय कितनी है (जैसे 2 लाख या 4 लाख)?'
            : 'For the scholarship income criteria, what is your family\'s approximate annual income (e.g. ₹2 Lakhs)?',
          targetField: 'annual_income'
        };
      }
    }

    // 6. Widow / Woman Specifics
    if (profile.gender === 'female' || profile.marital_status === 'widow') {
      if (!profile.marital_status) {
        return {
          question: isHi
            ? 'लाड़ली बहना एवं सामाजिक सुरक्षा पेंशन हेतु, क्या आप विवाहित, विधवा, अथवा अविवाहित हैं?'
            : 'For Ladli Behna and widow pensions, could you confirm your marital status (married, widowed, or single)?',
          targetField: 'marital_status'
        };
      }
      if (profile.annual_income === undefined || profile.annual_income === null) {
        return {
          question: isHi
            ? 'लाड़ली बहना (₹2.5 लाख सीमा) एवं पेंशन पात्रता के लिए, आपकी कुल वार्षिक पारिवारिक आय कितनी है?'
            : 'For statutory income eligibility (such as Ladli Behna ₹2.5L limit), what is your approximate annual household income?',
          targetField: 'annual_income'
        };
      }
      if (profile.bpl_card_holder === undefined || profile.bpl_card_holder === null) {
        return {
          question: isHi
            ? 'क्या आपके पास बीपीएल राशन कार्ड उपलब्ध है?'
            : 'Do you hold a BPL ration card?',
          targetField: 'bpl_card_holder'
        };
      }
    }

    // 7. General Income
    if (profile.annual_income === undefined || profile.annual_income === null) {
      return {
        question: isHi
          ? 'सटीक सरकारी अनुदान जांच हेतु, आपकी वार्षिक पारिवारिक आय लगभग कितनी है?'
          : 'To evaluate income-ceiling welfare benefits, what is your approximate annual family income?',
        targetField: 'annual_income'
      };
    }

    // Sufficient Profile Gathered!
    return null;
  };

  // Main Multi-Turn Processing Flow
  const handleCitizenTurn = async (speechText) => {
    if (!speechText.trim()) return;

    // 1. Add Citizen Message
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'citizen',
      text: speechText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setConversation((prev) => [...prev, userMsg]);
    setVoiceState('processing');
    setProcessingStep(1);

    // Dynamic Processing Visualizer Ticker
    const stepTimer1 = setTimeout(() => setProcessingStep(2), 600);
    const stepTimer2 = setTimeout(() => setProcessingStep(3), 1200);

    try {
<<<<<<< HEAD
      const resp = await parseFreeTextDescription(descriptionText, language);
      const extracted = resp.extracted_profile || {};
      
      setProfile({
        ...extracted,
        confirmed_fields: [] // explicitly unconfirmed until citizen confirms in S3!
      });
      setCurrentScreen('S3');
    } catch (err) {
      console.error('Text parsing error:', err);
      setErrorMsg(
        lt('Could not extract profile details. Please try again or rephrase.', 'विवरण विश्लेषण में समस्या आई। कृपया नीचे दोबारा प्रयास करें।')
=======
      // 2. Parse text with backend AI & local heuristic
      const parseResp = await parseFreeTextDescription(speechText, language);
      const newExtracted = parseResp.extracted_profile || {};

      // Heuristic fallback detection for quick local updates
      const tLower = speechText.toLowerCase();
      if (!newExtracted.has_pucca_house) {
        if (tLower.includes('कच्चा') || tLower.includes('kutcha') || tLower.includes('छप्पर')) {
          newExtracted.has_pucca_house = false;
        } else if (tLower.includes('पक्का') || tLower.includes('pucca')) {
          newExtracted.has_pucca_house = true;
        }
      }
      if (newExtracted.bpl_card_holder === undefined) {
        if (tLower.includes('बीपीएल') || tLower.includes('bpl') || tLower.includes('गरीबी')) {
          newExtracted.bpl_card_holder = true;
        }
      }

      // Merge into accumulated profile
      const merged = {
        ...accumulatedProfile,
        ...newExtracted,
      };

      const activeKeys = Object.keys(merged).filter(
        (k) => merged[k] !== undefined && merged[k] !== null && merged[k] !== '' && k !== 'confirmed_fields'
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
      );

      setAccumulatedProfile(merged);
      setConfirmedFields(activeKeys);

      // 3. Determine Next Move (Follow-up Question OR Direct Scheme Evaluation)
      const nextFollowup = computeNextFollowup(merged);

      // Check if user specifically requested schemes
      const userAskedForSchemes =
        tLower.includes('योजना') ||
        tLower.includes('स्कीम') ||
        tLower.includes('scheme') ||
        tLower.includes('बताओ') ||
        tLower.includes('show') ||
        tLower.includes('check');

      // If enough details gathered (or user explicitly requested), offer final transition!
      if (!nextFollowup || (activeKeys.length >= 4 && userAskedForSchemes)) {
        clearTimeout(stepTimer1);
        clearTimeout(stepTimer2);
        setProcessingStep(3);

        const readyMsgText =
          language === 'hi'
            ? `शानदार! आपकी प्रोफ़ाइल (${activeKeys.length} विवरण) सफलतापूर्वक दर्ज हो गई है। हम 8 आधिकारिक सरकारी योजनाओं के नियमों के अनुसार आपकी पात्रता निकाल रहे हैं...`
            : `Splendid! Your profile attributes (${activeKeys.length} verified fields) have been captured. Evaluating official deterministic rules for your eligible welfare schemes...`;

        const aiReadyMsg = {
          id: `ai-${Date.now()}`,
          sender: 'ai',
          text: readyMsgText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isReady: true,
        };

        setConversation((prev) => [...prev, aiReadyMsg]);

        if (isAudioEnabled) {
          setVoiceState('speaking');
          speakText(readyMsgText, language, () => {
            handleFinalEvaluation(merged);
          });
        } else {
          setTimeout(() => handleFinalEvaluation(merged), 1000);
        }
        return;
      }

      // 4. Formulate Multi-turn Voice Follow-up
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setProcessingStep(3);

      const aiMsg = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: nextFollowup.question,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        targetField: nextFollowup.targetField,
      };

      setConversation((prev) => [...prev, aiMsg]);

      // Speak AI response back to citizen
      if (isAudioEnabled) {
        setVoiceState('speaking');
        speakText(nextFollowup.question, language, () => {
          setVoiceState('idle');
          // Auto-prompt mic for smooth conversational flow
          setTimeout(() => {
            startListening();
          }, 350);
        });
      } else {
        setVoiceState('idle');
      }
    } catch (err) {
      console.error('Turn processing error:', err);
      setVoiceState('idle');
    }
  };

  // Final Transition to S4_ResultsScreen with 100% Deterministic Rules
  const handleFinalEvaluation = async (finalProfileToEval = accumulatedProfile) => {
    setVoiceState('processing');
    setProcessingStep(3);

    const activeKeys = Object.keys(finalProfileToEval).filter(
      (k) => finalProfileToEval[k] !== undefined && finalProfileToEval[k] !== null && finalProfileToEval[k] !== '' && k !== 'confirmed_fields'
    );

    const fullProfile = {
      ...finalProfileToEval,
      confirmed_fields: activeKeys,
    };

    setProfile(fullProfile);

    try {
      const evalResp = await evaluateCitizenProfile(fullProfile);
      setEvaluationResults(evalResp);
      stopSpeaking();
      // Smooth direct navigation to S4 as user requested!
      setCurrentScreen('S4');
    } catch (err) {
      console.error('Final evaluation failed:', err);
      stopSpeaking();
      setCurrentScreen('S4');
    }
  };

  // Fast Persona Speech Simulation for Hackathon Judges
  const triggerDemoSpeech = (personaType) => {
    stopSpeaking();
    if (personaType === 'farmer') {
      const text =
        language === 'hi'
          ? 'मैं 48 साल का किसान हूँ, मध्य प्रदेश के सीहोर में रहता हूँ। मेरे पास डेढ़ हेक्टेयर जमीन है और कच्चा मकान है।'
          : 'I am a 48 year old farmer living in Sehore, Madhya Pradesh with 1.5 hectares of land and a kutcha house.';
      handleCitizenTurn(text);
    } else if (personaType === 'widow') {
      const text =
        language === 'hi'
          ? 'मैं 52 वर्ष की विधवा महिला हूँ, मध्य प्रदेश में रहती हूँ। मेरे पास बीपीएल राशन कार्ड है और आय 24 हजार है।'
          : 'I am a 52 year old widow living in Madhya Pradesh. We have a BPL ration card and annual income under 25,000 INR.';
      handleCitizenTurn(text);
    } else if (personaType === 'student') {
      const text =
        language === 'hi'
          ? 'मैं 19 साल का छात्र हूँ, मध्य प्रदेश का निवासी हूँ। 12वीं में 86% अंक आए हैं और मैंने इंजीनियरिंग में प्रवेश लिया है।'
          : 'I am a 19 year old student from MP with 86% marks in Class 12 board exams and enrolled in an engineering degree.';
      handleCitizenTurn(text);
    }
  };

  const resetVoiceChat = () => {
    stopSpeaking();
    setAccumulatedProfile({});
    setConfirmedFields([]);
    setLiveInterim('');
    setVoiceState('idle');
    const welcome =
      language === 'hi'
        ? 'सत्र रीसेट हो गया है। अपने बारे में नए सिरे से बोलें, मैं आपकी पूरी बात सुन रहा हूँ।'
        : 'Session reset. Speak naturally about yourself to begin fresh eligibility matching.';
    setConversation([
      {
        id: `welcome-${Date.now()}`,
        sender: 'ai',
        text: welcome,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    if (isAudioEnabled) {
      speakText(welcome, language);
    }
  };

  // Format label for detected attributes
  const renderAttributeChip = (key, val) => {
    if (val === undefined || val === null || val === '') return null;
    let label = `${key}: ${val}`;
    if (key === 'age') label = `🎂 ${val} ${language === 'hi' ? 'वर्ष' : 'years'}`;
    if (key === 'occupation') {
      const map = { farmer: '🌾 किसान', student: '🎓 विद्यार्थी', homemaker: '👩 गृहिणी', agricultural_worker: '🌱 मजदूर' };
      label = map[val] || `💼 ${val}`;
    }
    if (key === 'state') label = `📍 ${val}`;
    if (key === 'landholding_hectares') label = `🌱 ${val} ha land`;
    if (key === 'student_class12_marks_percent') label = `⭐ ${val}% (Class 12)`;
    if (key === 'has_pucca_house') label = val ? '🏠 पक्का मकान' : '🛖 कच्चा मकान';
    if (key === 'bpl_card_holder') label = val ? '📋 बीपीएल कार्ड' : 'बिना बीपीएल';
    if (key === 'annual_income') label = `💰 ₹${val.toLocaleString('en-IN')}`;
    if (key === 'marital_status') label = val === 'widow' ? '🕊️ विधवा' : `💍 ${val}`;

    return (
      <span
        key={key}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-400/15 text-amber-300 border border-amber-400/30 backdrop-blur-xs animate-fade-in shadow-xs"
      >
        <span>{label}</span>
      </span>
    );
  };

  return (
    <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col justify-between space-y-5 animate-fade-in text-white">
      {/* 1. Header Bar: Navigation & Status */}
      <div className="flex items-center justify-between gap-3 pt-1">
        <button
          onClick={() => {
            stopSpeaking();
            setCurrentScreen('S0');
          }}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold transition-all shadow-xs"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t('back')}</span>
        </button>

        <div className="flex items-center gap-2">
          {/* Audio Output Mute / Unmute Toggle */}
          <button
            onClick={() => {
              if (isAudioEnabled) stopSpeaking();
              setIsAudioEnabled(!isAudioEnabled);
            }}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              isAudioEnabled
                ? 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300'
                : 'bg-slate-800/80 border-slate-700 text-slate-400'
            }`}
            title="Toggle AI Voice Response"
          >
            {isAudioEnabled ? <Volume2 className="w-3.5 h-3.5 text-emerald-400" /> : <VolumeX className="w-3.5 h-3.5 text-slate-400" />}
            <span className="hidden sm:inline">
              {isAudioEnabled ? (language === 'hi' ? 'आवाज़ सक्रिय' : 'Voice Output ON') : (language === 'hi' ? 'आवाज़ बंद' : 'Muted')}
            </span>
          </button>

<<<<<<< HEAD
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
                {lt('Describe Yourself in Your Own Words', 'अपने बारे में बोलें या लिखें')}
              </h2>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                {lt('Speak or type naturally about your age, work, state, income, and family. AI extracts details for your confirmation before eligibility is computed.', 'अपनी आयु, व्यवसाय, राज्य, आय और परिवार के बारे में स्वाभाविक रूप से बताएं। एआई केवल आवश्यक विवरण निकालेगा, जिसकी पुष्टि आप अगले चरण में कर सकेंगे।')}
              </p>
            </div>
            <AudioSpeaker
              text={
                lt('Describe yourself in your own words using voice or text.', 'अपनी आयु, व्यवसाय, राज्य और परिवार के बारे में बोलकर या लिखकर बताएं।')
              }
              className="mt-1 flex-shrink-0"
            />
=======
          {/* Reset Conversation */}
          <button
            onClick={resetVoiceChat}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-400 hover:text-rose-400 border border-slate-700 text-xs font-semibold transition-all"
            title="Reset Session"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{language === 'hi' ? 'पुनरारंभ' : 'Reset'}</span>
          </button>
        </div>
      </div>

      {/* 2. Main Luxury Conversational Stage (Cosmic Navy & Gold Glassmorphic) */}
      <div className="relative rounded-3xl bg-gradient-to-br from-[#070e24] via-[#0b183a] to-[#050916] border-2 border-blue-500/30 p-5 sm:p-8 shadow-2xl overflow-hidden flex flex-col justify-between min-h-[580px]">
        {/* Ambient Cosmic Radial Glows */}
        <div className="absolute -top-24 -right-24 w-80 h-80 bg-blue-600/15 rounded-full blur-3xl pointer-events-none animate-pulse" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Top Badges & Live Attributes Tray */}
        <div className="relative z-10 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-blue-900/50 pb-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-700/60 text-xs font-bold text-blue-200 backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
              <span>
                {language === 'hi'
                  ? '🎙️ दो-तरफ़ा एआई आवाज़ संचार मॉडल'
                  : '🎙️ Two-Way Conversational Voice AI Model'}
              </span>
            </div>

            <div className="flex items-center gap-2 text-[11px] font-semibold text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>
                {language === 'hi'
                  ? 'शून्य डेटा संचयन • 100% सटीक नियम'
                  : 'Zero Retention • 100% Deterministic'}
              </span>
            </div>
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
          </div>

          {/* Live Detected Profile Pills */}
          {confirmedFields.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[11px] font-bold text-slate-400 flex items-center gap-1 mr-1">
                <Sparkles className="w-3 h-3 text-amber-400" />
                <span>{language === 'hi' ? 'पहचाने गए विवरण:' : 'Extracted Attributes:'}</span>
              </span>
              {confirmedFields.map((fieldKey) =>
                renderAttributeChip(fieldKey, accumulatedProfile[fieldKey])
              )}
            </div>
          )}
        </div>

<<<<<<< HEAD
        {/* Text Area Card with Mic */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="relative">
            <textarea
              rows={5}
              value={descriptionText}
              onChange={(e) => setDescriptionText(e.target.value)}
              placeholder={
                lt('E.g., I am a 48 year old farmer living in Madhya Pradesh with 1.5 hectares of land and annual family income of 65,000 INR...', 'उदाहरण: मैं 48 साल का किसान हूँ, मध्य प्रदेश में रहता हूँ, मेरे पास 1.5 हेक्टेयर जमीन है और वार्षिक आय 65 हजार है...')
              }
              className="w-full text-sm sm:text-base text-slate-900 p-4 rounded-xl border border-slate-300 focus:border-blue-600 focus:outline-hidden bg-slate-50/50 leading-relaxed resize-none shadow-inner"
            />
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
            <div className="flex items-center gap-3">
              <VoiceMic onTranscriptChange={handleVoiceTranscript} />
              <div className="text-xs text-slate-600">
                <span className="font-semibold block">
                  {lt('Voice Microphone', 'आवाज से इनपुट (Voice Input)')}
                </span>
                <span className="text-slate-400">
                  {lt('Tap mic button and speak clearly', 'माइक बटन दबाएं और स्पष्ट बोलें')}
                </span>
=======
        {/* Centerpiece: Chat History Stream */}
        <div
          ref={chatScrollRef}
          className="relative z-10 flex-1 overflow-y-auto space-y-4 my-4 max-h-[290px] sm:max-h-[320px] pr-2 scrollbar-thin scrollbar-thumb-blue-800 scrollbar-track-transparent"
        >
          {conversation.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3 animate-fade-in ${
                msg.sender === 'citizen' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              {/* Avatar Icon */}
              <div
                className={`w-9 h-9 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md ${
                  msg.sender === 'citizen'
                    ? 'bg-gradient-to-tr from-cyan-600 to-teal-400 text-white font-bold text-xs'
                    : 'bg-gradient-to-tr from-amber-500 via-amber-600 to-orange-600 text-white shadow-amber-500/20'
                }`}
              >
                {msg.sender === 'citizen' ? 'ना.' : 'य'}
              </div>

              {/* Message Bubble with Glassmorphism */}
              <div
                className={`max-w-[82%] sm:max-w-[75%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed backdrop-blur-md shadow-lg ${
                  msg.sender === 'citizen'
                    ? 'bg-gradient-to-r from-teal-900/60 to-cyan-950/80 border border-teal-500/40 text-cyan-100 rounded-tr-xs'
                    : 'bg-gradient-to-r from-blue-950/80 via-slate-900/90 to-blue-950/80 border border-blue-700/50 text-slate-200 rounded-tl-xs'
                }`}
              >
                <div className="flex items-center justify-between gap-3 mb-1">
                  <span className="font-bold text-[11px] text-amber-400">
                    {msg.sender === 'citizen'
                      ? (language === 'hi' ? 'आप (Citizen Voice)' : 'You (Voice)')
                      : (language === 'hi' ? 'योजनासारथी एआई (Voice Assistant)' : 'YojnaSarthi Voice AI')}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">{msg.timestamp}</span>
                </div>
                <p className="whitespace-pre-line text-slate-100">{msg.text}</p>

                {/* Speaker Replay Button on AI messages */}
                {msg.sender === 'ai' && (
                  <button
                    onClick={() => {
                      setVoiceState('speaking');
                      speakText(msg.text, language, () => setVoiceState('idle'));
                    }}
                    className="mt-2.5 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-900/40 hover:bg-blue-800/60 text-blue-300 text-[11px] font-semibold transition-all border border-blue-700/30"
                  >
                    <Volume2 className="w-3 h-3 text-cyan-400" />
                    <span>{language === 'hi' ? 'पुनः सुनें' : 'Listen Again'}</span>
                  </button>
                )}
              </div>
            </div>
          ))}

          {/* Live Interim Transcription (while user speaks) */}
          {voiceState === 'listening' && liveInterim && (
            <div className="flex items-start gap-3 flex-row-reverse animate-pulse">
              <div className="w-9 h-9 rounded-2xl bg-cyan-600/60 flex items-center justify-center text-white text-xs font-bold">
                🎙️
              </div>
              <div className="max-w-[80%] rounded-2xl p-4 bg-teal-950/70 border border-teal-400/50 text-teal-200 text-xs sm:text-sm rounded-tr-xs shadow-lg">
                <span className="text-[10px] font-bold text-teal-400 block mb-1">
                  {language === 'hi' ? 'लाइव ध्वनि पहचान (Listening...):' : 'Live Speech Audio (Listening...):'}
                </span>
                <p className="italic">"{liveInterim}"</p>
              </div>
            </div>
          )}
        </div>

        {/* 3. The Lavish Futuristic Interactive Voice Orb (Core Vision Fulfillment) */}
        <div className="relative z-10 pt-4 border-t border-blue-900/60 flex flex-col items-center justify-center space-y-4">
          {/* Dynamic Status Pill */}
          <div className="text-center">
            {voiceState === 'idle' && (
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/70 border border-blue-700/50 text-blue-300 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping inline-block" />
                <span>
                  {language === 'hi'
                    ? 'नीचे दिए गए बटन को दबाकर बोलें (Tap Orb to Speak)'
                    : 'Tap the Voice Orb below and speak naturally'}
                </span>
              </span>
            )}
            {voiceState === 'listening' && (
              <span className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-950 border border-emerald-500 text-emerald-300 text-xs font-extrabold shadow-lg shadow-emerald-500/20 animate-pulse">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping inline-block" />
                <span>{language === 'hi' ? 'सुन रहा हूँ... बोलिए (Listening)' : 'Listening carefully... Speak now'}</span>
              </span>
            )}
            {voiceState === 'processing' && (
              <span className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-950/80 border border-amber-500 text-amber-300 text-xs font-extrabold shadow-lg shadow-amber-500/20">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-spin inline-block" />
                <span>
                  {processingStep === 1 && (language === 'hi' ? 'आवाज़ का विश्लेषण हो रहा है...' : 'Analyzing speech acoustics...')}
                  {processingStep === 2 && (language === 'hi' ? 'प्रोफ़ाइल विवरण निकाले जा रहे हैं...' : 'Extracting profile parameters...')}
                  {processingStep === 3 && (language === 'hi' ? 'सरकारी नियमों के डेटाबेस से मिलान...' : 'Matching with 8 verified schemes...')}
                </span>
              </span>
            )}
            {voiceState === 'speaking' && (
              <span className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-950 border border-cyan-500 text-cyan-300 text-xs font-extrabold shadow-lg shadow-cyan-500/20 animate-pulse">
                <Volume2 className="w-3.5 h-3.5 text-cyan-400 animate-bounce" />
                <span>{language === 'hi' ? 'एआई सहायक बोल रहा है... (AI Speaking)' : 'Assistant speaking back...'}</span>
              </span>
            )}
          </div>

          {/* Interactive Glowing Hologram Voice Orb with Animated Radial Waves */}
          <div className="relative flex items-center justify-center my-2">
            {/* Outer Concentric Animated Energy Rings */}
            <div
              className={`absolute w-36 h-36 rounded-full transition-all duration-700 pointer-events-none ${
                voiceState === 'listening'
                  ? 'bg-emerald-500/20 border-2 border-emerald-400/40 animate-ping'
                  : voiceState === 'processing'
                  ? 'bg-amber-500/20 border-2 border-amber-400/50 animate-spin'
                  : voiceState === 'speaking'
                  ? 'bg-cyan-500/20 border-2 border-cyan-400/40 animate-pulse'
                  : 'bg-blue-500/10 border border-blue-400/20'
              }`}
            />
            <div
              className={`absolute w-28 h-28 rounded-full transition-all duration-500 pointer-events-none ${
                voiceState === 'listening'
                  ? 'border-2 border-emerald-400/60 scale-110'
                  : voiceState === 'processing'
                  ? 'border-2 border-amber-400/80 animate-spin'
                  : voiceState === 'speaking'
                  ? 'border-2 border-cyan-400/70 scale-105'
                  : 'border border-blue-500/30'
              }`}
            />

            {/* Central Main Interactive Orb Button */}
            <button
              type="button"
              onClick={() => {
                if (voiceState === 'listening') {
                  stopListening();
                } else if (voiceState === 'speaking') {
                  stopSpeaking();
                  setVoiceState('idle');
                } else {
                  startListening();
                }
              }}
              className={`relative z-20 w-20 h-20 sm:w-22 sm:h-22 rounded-full flex items-center justify-center transition-all duration-300 shadow-2xl active:scale-95 group focus:outline-hidden ${
                voiceState === 'listening'
                  ? 'bg-gradient-to-tr from-emerald-600 via-teal-500 to-emerald-400 shadow-emerald-500/50 border-4 border-emerald-200'
                  : voiceState === 'processing'
                  ? 'bg-gradient-to-tr from-amber-600 via-orange-500 to-amber-400 shadow-amber-500/50 border-4 border-amber-200 animate-pulse'
                  : voiceState === 'speaking'
                  ? 'bg-gradient-to-tr from-cyan-600 via-blue-500 to-indigo-500 shadow-cyan-500/50 border-4 border-cyan-200'
                  : 'bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-700 hover:from-blue-600 hover:to-cyan-600 shadow-blue-500/30 border-4 border-blue-400/40'
              }`}
            >
              {voiceState === 'listening' ? (
                <div className="flex flex-col items-center">
                  <Mic className="w-8 h-8 text-white animate-bounce" />
                  <span className="text-[9px] font-black uppercase tracking-wider text-emerald-950 mt-0.5">
                    {language === 'hi' ? 'रोकें' : 'Stop'}
                  </span>
                </div>
              ) : voiceState === 'processing' ? (
                <div className="w-8 h-8 border-3 border-white border-t-transparent rounded-full animate-spin" />
              ) : voiceState === 'speaking' ? (
                <div className="flex flex-col items-center">
                  <Volume2 className="w-8 h-8 text-white animate-pulse" />
                  <span className="text-[9px] font-black uppercase tracking-wider text-cyan-950 mt-0.5">
                    {language === 'hi' ? 'विराम' : 'Pause'}
                  </span>
                </div>
              ) : (
                <div className="flex flex-col items-center group-hover:scale-110 transition-transform">
                  <Mic className="w-8 h-8 text-white" />
                  <span className="text-[9px] font-black uppercase tracking-wider text-blue-100 mt-0.5">
                    {language === 'hi' ? 'बोलें' : 'Speak'}
                  </span>
                </div>
              )}
            </button>
          </div>

          {/* Equalizer Bouncing Bars (while listening or speaking) */}
          {(voiceState === 'listening' || voiceState === 'speaking') && (
            <div className="flex items-center gap-1.5 h-6">
              {[40, 80, 60, 100, 75, 45, 90].map((h, i) => (
                <span
                  key={i}
                  className={`w-1 rounded-full transition-all duration-150 ${
                    voiceState === 'listening' ? 'bg-emerald-400' : 'bg-cyan-400'
                  }`}
                  style={{
                    height: `${Math.max(8, (h * Math.sin(Date.now() / 200 + i)) % 24)}px`,
                  }}
                />
              ))}
            </div>
          )}

          {/* 4. Action Row: View Schemes CTA & Manual Text Tray */}
          <div className="w-full space-y-3 pt-2">
            {/* Direct Instant Transition Button */}
            {confirmedFields.length >= 2 && (
              <div className="flex items-center justify-center">
                <button
                  type="button"
                  onClick={() => handleFinalEvaluation(accumulatedProfile)}
                  className="inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-600 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-slate-950 font-extrabold text-xs sm:text-sm shadow-xl shadow-amber-500/25 transition-all active:scale-98 animate-bounce min-h-[46px]"
                >
                  <Award className="w-4 h-4 text-slate-950" />
                  <span>
                    {language === 'hi'
                      ? '🎯 पात्र सरकारी योजनाएं देखें (View Eligible Schemes)'
                      : '🎯 Evaluate & View My Schemes Now'}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Quick Demo Voice Persona Chips for Hackathon Judges */}
            <div className="space-y-1.5 text-center">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>{language === 'hi' ? 'त्वरित आवाज सिमुलेशन (Judge Demo Persona):' : 'Instant Speech Simulation (Demo Persona):'}</span>
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => triggerDemoSpeech('farmer')}
                  className="p-2.5 rounded-xl bg-blue-950/60 hover:bg-emerald-950/60 border border-blue-800/60 hover:border-emerald-500/80 text-left text-xs font-semibold text-slate-200 transition-all flex items-center gap-2 group"
                >
                  <span className="text-lg">🌾</span>
                  <div>
                    <span className="block font-bold text-emerald-400 group-hover:text-emerald-300">
                      {language === 'hi' ? 'ग्रामीण किसान' : 'Rural Farmer'}
                    </span>
                    <span className="text-[10px] text-slate-400">48y, 1.5ha, MP</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => triggerDemoSpeech('widow')}
                  className="p-2.5 rounded-xl bg-blue-950/60 hover:bg-rose-950/60 border border-blue-800/60 hover:border-rose-500/80 text-left text-xs font-semibold text-slate-200 transition-all flex items-center gap-2 group"
                >
                  <span className="text-lg">👩</span>
                  <div>
                    <span className="block font-bold text-rose-400 group-hover:text-rose-300">
                      {language === 'hi' ? 'विधवा महिला' : 'Widowed Homemaker'}
                    </span>
                    <span className="text-[10px] text-slate-400">52y, BPL, MP</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => triggerDemoSpeech('student')}
                  className="p-2.5 rounded-xl bg-blue-950/60 hover:bg-cyan-950/60 border border-blue-800/60 hover:border-cyan-500/80 text-left text-xs font-semibold text-slate-200 transition-all flex items-center gap-2 group"
                >
                  <span className="text-lg">🎓</span>
                  <div>
                    <span className="block font-bold text-cyan-400 group-hover:text-cyan-300">
                      {language === 'hi' ? 'कॉलेज विद्यार्थी' : 'College Student'}
                    </span>
                    <span className="text-[10px] text-slate-400">19y, 86%, MMVY</span>
                  </div>
                </button>
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
              </div>
            </div>

            {/* Accessible Text Fallback Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (typedInput.trim()) {
                  handleCitizenTurn(typedInput.trim());
                  setTypedInput('');
                }
              }}
              className="flex items-center gap-2 bg-slate-900/80 border border-blue-800/60 rounded-xl p-1.5 focus-within:border-cyan-400 transition-colors shadow-inner"
            >
              <input
                type="text"
                value={typedInput}
                onChange={(e) => setTypedInput(e.target.value)}
                placeholder={
                  language === 'hi'
                    ? 'या यहाँ टाइप करके जवाब दें (उदा. हाँ, डेढ़ हेक्टेयर जमीन और कच्चा मकान है)...'
                    : 'Or type your reply here (e.g. Yes, 1.5 hectares land and kutcha house)...'
                }
                className="flex-1 bg-transparent px-3 py-1.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-hidden"
              />
              <button
                type="submit"
                disabled={!typedInput.trim() || voiceState === 'processing'}
                className="p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white transition-all shadow-xs"
                title="Send Text"
              >
<<<<<<< HEAD
                {lt('Clear Text', 'पाठ साफ़ करें (Clear)')}
=======
                <Send className="w-4 h-4" />
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
              </button>
            </form>
          </div>
        </div>
<<<<<<< HEAD

        {/* Sample Prompts */}
        <div className="space-y-2.5">
          <span className="text-xs font-bold text-slate-600 flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>{lt('Sample Prompts (Tap to fill):', 'त्वरित उदाहरण विवरण (Tap to fill):')}</span>
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {samplePrompts.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setDescriptionText(s.text)}
                className="p-3 bg-white hover:bg-blue-50/60 border border-slate-200 hover:border-blue-400 rounded-xl text-left text-xs font-semibold text-slate-700 transition-all shadow-2xs hover:shadow-xs group"
              >
                <span className="block text-slate-900 group-hover:text-blue-800">
                  {lt(s.label_en, s.label_hi)}
                </span>
                <span className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                  {s.text}
                </span>
              </button>
            ))}
          </div>
        </div>

        {errorMsg && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2.5 text-xs text-rose-700 font-medium">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* CTA Footer */}
      <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-end gap-3">
        <button
          onClick={handleSubmit}
          disabled={!descriptionText.trim() || isParsing}
          className="w-full sm:w-auto px-8 py-3.5 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 min-h-[48px]"
        >
          {isParsing ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>{lt('Extracting profile with AI...', 'विवरण निकाला जा रहा है...')}</span>
            </div>
          ) : (
            <>
              <span>{lt('Review & Confirm Profile', 'विवरण की समीक्षा करें')}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
=======
>>>>>>> 8ba64483fb397774ab2a0b224248a3bd2948e636
      </div>
    </div>
  );
}
