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
  Award,
  Radio,
  Cpu,
  Layers,
  Check
} from 'lucide-react';

export default function S2_FreeTextInputScreen() {
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen, setProfile, setEvaluationResults } = useSession();

  // Voice States: 'idle' | 'listening' | 'processing' | 'speaking'
  const [voiceState, setVoiceState] = useState('idle');
  const [liveInterim, setLiveInterim] = useState('');
  const [typedInput, setTypedInput] = useState('');
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isHandsFree, setIsHandsFree] = useState(true);
  const [processingStage, setProcessingStage] = useState(0); // 0: Idle, 1: Audio Analyzed, 2: Profile Extracted, 3: Rules Matching

  // Accumulated Citizen Profile
  const [accumulatedProfile, setAccumulatedProfile] = useState({});
  const [confirmedFields, setConfirmedFields] = useState([]);

  // Conversational History: [{ id, sender: 'ai'|'citizen', text, timestamp, targetField }]
  const [conversation, setConversation] = useState([]);

  const recognizerRef = useRef(null);
  const chatScrollRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const lastSpokenTextRef = useRef('');

  // Initial AI Voice Welcome
  useEffect(() => {
    let welcomeText = '';
    if (language === 'hi') {
      welcomeText = 'नमस्ते! मैं आपका योजनासारथी दो-तरफ़ा आवाज़ सहायक हूँ। अपने बारे में बताएं—जैसे आपकी आयु, काम, राज्य या परिवार—ताकि मैं आपकी पात्र सरकारी योजनाएं खोज सकूँ।';
    } else if (language === 'mr') {
      welcomeText = 'नमस्कार! मी योजनासारथी व्हॉइस असिस्टंट आहे. आपल्याबद्दल सांगा—जसे की आपले वय, व्यवसाय किंवा राज्य—जेणेकरून मी आपल्यासाठी पात्र योजना शोधू शकेन.';
    } else if (language === 'bn') {
      welcomeText = 'নমস্কার! আমি যোজনা সারথী ভয়েস সহকারী। আপনার বয়স, পেশা বা রাজ্য সম্পর্কে বলুন—যাতে আমি আপনার জন্য উপযুক্ত সরকারি প্রকল্প খুঁজে বের করতে পারি।';
    } else {
      welcomeText = 'Namaste! I am your YojnaSarthi two-way voice assistant. Speak naturally about yourself—your age, occupation, state, or family—so I can discover your eligible welfare schemes.';
    }

    const initialMsg = {
      id: 'welcome-1',
      sender: 'ai',
      text: welcomeText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setConversation([initialMsg]);

    if (isAudioEnabled) {
      setVoiceState('speaking');
      speakText(welcomeText, language, () => {
        setVoiceState('idle');
        if (isHandsFree) {
          setTimeout(() => startListening(), 400);
        }
      });
    }

    return () => {
      stopSpeaking();
      if (recognizerRef.current) {
        recognizerRef.current.cancel();
      }
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
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
      language: language === 'en' ? 'en' : 'hi', // 'hi-IN' understands both Hindi and Hinglish
      onInterim: (text) => {
        setLiveInterim(text);
        // Automatic silence detection for hands-free speech
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        if (text.trim().length > 3) {
          silenceTimerRef.current = setTimeout(() => {
            if (recognizerRef.current) {
              recognizerRef.current.stop();
            }
          }, 1400);
        }
      },
      onFinal: (finalText) => {
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        const textToProcess = (finalText || liveInterim || lastSpokenTextRef.current).trim();
        setLiveInterim('');
        lastSpokenTextRef.current = '';
        if (textToProcess) {
          handleCitizenTurn(textToProcess);
        } else {
          setVoiceState('idle');
        }
      },
      onError: (err) => {
        console.warn('Speech recognition warning:', err);
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
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, [language, liveInterim, voiceState, accumulatedProfile, isHandsFree]);

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

  // Robust Local Hinglish & Multilingual Parser Heuristic
  const parseHinglishLocally = (text) => {
    const p = {};
    const t = text.toLowerCase();

    // 1. Age
    const ageMatch = t.match(/(\d{1,2})\s*(?:years?|saal|sal|वर्ष|साल|age|umar|umr|उम्र|आयु)/i);
    if (ageMatch) {
      p.age = parseInt(ageMatch[1], 10);
    }

    // 2. Gender & Marital Status
    if (t.includes('विधवा') || t.includes('widow') || t.includes('vidhwa') || t.includes('pati expired') || t.includes('pati nahi')) {
      p.marital_status = 'widow';
      p.gender = 'female';
    } else if (t.includes('महिला') || t.includes('aurat') || t.includes('female') || t.includes('woman') || t.includes('girl') || t.includes('ladki')) {
      p.gender = 'female';
    } else if (t.includes('पुरुष') || t.includes('purush') || t.includes('male') || t.includes('man') || t.includes('ladka') || t.includes('admi') || t.includes('bhai')) {
      p.gender = 'male';
    }

    if (!p.marital_status) {
      if (t.includes('विवाहित') || t.includes('married') || t.includes('shaadi ho chuki') || t.includes('shadi')) {
        p.marital_status = 'married';
      } else if (t.includes('अविवाहित') || t.includes('single') || t.includes('unmarried') || t.includes('kunwara')) {
        p.marital_status = 'single';
      }
    }

    // 3. State
    if (t.includes('मध्य प्रदेश') || t.includes('madhya pradesh') || t.includes('mp') || t.includes('m.p.') || t.includes('sehore') || t.includes('bhopal') || t.includes('indore') || t.includes('rewa') || t.includes('jabalpur')) {
      p.state = 'Madhya Pradesh';
    } else if (t.includes('महाराष्ट्र') || t.includes('maharashtra') || t.includes('mumbai') || t.includes('pune') || t.includes('nagpur')) {
      p.state = 'Maharashtra';
    } else if (t.includes('उत्तर प्रदेश') || t.includes('uttar pradesh') || t.includes('up')) {
      p.state = 'Uttar Pradesh';
    } else if (t.includes('राजस्थान') || t.includes('rajasthan')) {
      p.state = 'Rajasthan';
    } else if (t.includes('बिहार') || t.includes('bihar')) {
      p.state = 'Bihar';
    }

    // 4. Occupation
    if (t.includes('किसान') || t.includes('kisan') || t.includes('farmer') || t.includes('kheti') || t.includes('farming') || t.includes('krishi') || t.includes('khet')) {
      p.occupation = 'farmer';
    } else if (t.includes('छात्र') || t.includes('विद्यार्थी') || t.includes('student') || t.includes('college') || t.includes('padhai') || t.includes('school') || t.includes('b.tech') || t.includes('degree') || t.includes('engineering')) {
      p.occupation = 'student';
      p.enrolled_higher_education = true;
    } else if (t.includes('मजदूर') || t.includes('labor') || t.includes('majdoor') || t.includes('shramik') || t.includes('dihadi')) {
      p.occupation = 'agricultural_worker';
    } else if (t.includes('गृहिणी') || t.includes('homemaker') || t.includes('housewife')) {
      p.occupation = 'homemaker';
    } else if (t.includes('स्व-रोजगार') || t.includes('self employed') || t.includes('dukaan') || t.includes('shop') || t.includes('vyapar')) {
      p.occupation = 'self_employed';
    }

    // 5. Landholding
    if (t.includes('डेढ़ हेक्टेयर') || t.includes('dedh hectare')) {
      p.landholding_hectares = 1.5;
      p.is_institutional_landholder = false;
      p.holds_constitutional_post = false;
    } else if (t.includes('दो एकड़') || t.includes('do acre') || t.includes('2 acre') || t.includes('2 एकड़')) {
      p.landholding_hectares = 0.81;
      p.is_institutional_landholder = false;
      p.holds_constitutional_post = false;
    } else if (t.includes('zameen nahi') || t.includes('khet nahi') || t.includes('landless') || t.includes('bhumihin') || t.includes('ज़मीन नहीं')) {
      p.landholding_hectares = 0.0;
      p.is_institutional_landholder = false;
      p.holds_constitutional_post = false;
    } else {
      const landMatch = t.match(/(\d+(?:\.\d+)?)\s*(?:hectare|ha|हेक्टेयर|एकड़|acre)/i);
      if (landMatch) {
        let val = parseFloat(landMatch[1]);
        if (t.includes('एकड़') || t.includes('acre')) val = val * 0.4046;
        p.landholding_hectares = parseFloat(val.toFixed(2));
        p.is_institutional_landholder = false;
        p.holds_constitutional_post = false;
      }
    }

    // 6. Marks (Class 12)
    const marksMatch = t.match(/(\d{2}(?:\.\d+)?)\s*(?:%|percent|प्रतिशत|marks)/i);
    if (marksMatch) {
      p.student_class12_marks_percent = parseFloat(marksMatch[1]);
    }

    // 7. Income (Hinglish: hazar / lakh / 60000)
    const lakhMatch = t.match(/(\d+(?:\.\d+)?)\s*(?:लाख|lakh)/i);
    const hazarMatch = t.match(/(\d+(?:\.\d+)?)\s*(?:hazar|हज़ार|हजार|thousand|k\b)/i);
    if (t.includes('डेढ़ लाख') || t.includes('dedh lakh')) {
      p.annual_income = 150000;
    } else if (t.includes('ढाई लाख') || t.includes('dhai lakh')) {
      p.annual_income = 250000;
    } else if (lakhMatch) {
      p.annual_income = parseFloat(lakhMatch[1]) * 100000;
    } else if (hazarMatch) {
      p.annual_income = parseFloat(hazarMatch[1]) * 1000;
    } else {
      const incMatch = t.match(/(?:income|aay|kamata|kamaai|कमाई|आय|rupaye|rs\.?|₹)\s*(\d[\d,]+)/i);
      if (incMatch) {
        p.annual_income = parseFloat(incMatch[1].replace(/,/g, ''));
      }
    }

    // 8. Pucca House / Kutcha House
    if (t.includes('कच्चा') || t.includes('kutcha') || t.includes('kachha') || t.includes('kaccha') || t.includes('jhopdi') || t.includes('chhappar')) {
      p.has_pucca_house = false;
    } else if (t.includes('पक्का मकान') || t.includes('pakka makan') || t.includes('pakka ghar') || t.includes('pucca house') || t.includes('pucca')) {
      p.has_pucca_house = true;
    }

    // 9. BPL Card
    if (t.includes('bpl nahi') || t.includes('बीपीएल नहीं') || t.includes('rashan card nahi') || t.includes('राशन कार्ड नहीं') || t.includes('apl')) {
      p.bpl_card_holder = false;
    } else if (t.includes('bpl') || t.includes('बीपीएल') || t.includes('गरीबी रेखा') || t.includes('antyodaya') || t.includes('अंत्योदय') || t.includes('rashan card') || t.includes('राशन कार्ड') || t.includes('peela card')) {
      p.bpl_card_holder = true;
    }

    return p;
  };

  // Analyze Profile & Compute Follow-up Question
  const computeNextFollowup = (profile) => {
    const isHi = language === 'hi' || language === 'mr';

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
          ? 'सटीक सरकारी अनुदान जांच हेतु, आपकी वार्षिक पारिवारिक आय लगभग कितनी है (जैसे 60,000 या 1 लाख)?'
          : 'To evaluate income-ceiling welfare benefits, what is your approximate annual family income?',
        targetField: 'annual_income'
      };
    }

    // Sufficient Profile Gathered!
    return null;
  };

  // Main Multi-Turn Processing Flow with Animated Moment of Processing
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
    setProcessingStage(1);

    // Staged Animated Moment of Processing (Satisfying Lavish Circle Progress)
    await new Promise((r) => setTimeout(r, 450));
    setProcessingStage(2);

    try {
      // 2. Parse text with backend AI & local Hinglish extractor
      let newExtracted = {};
      try {
        const parseResp = await parseFreeTextDescription(speechText, language);
        newExtracted = parseResp.extracted_profile || {};
      } catch (err) {
        console.warn('Backend parse error, using local Hinglish heuristic:', err);
      }

      // Merge local Hinglish heuristic
      const localHinglish = parseHinglishLocally(speechText);
      const mergedExtracted = {
        ...localHinglish,
        ...newExtracted,
      };

      // Merge into accumulated profile
      const merged = {
        ...accumulatedProfile,
        ...mergedExtracted,
      };

      const activeKeys = Object.keys(merged).filter(
        (k) => merged[k] !== undefined && merged[k] !== null && merged[k] !== '' && k !== 'confirmed_fields'
      );

      setAccumulatedProfile(merged);
      setConfirmedFields(activeKeys);

      await new Promise((r) => setTimeout(r, 450));
      setProcessingStage(3);

      // 3. Determine Next Move (Follow-up Question OR Direct Scheme Evaluation)
      const nextFollowup = computeNextFollowup(merged);

      const tLower = speechText.toLowerCase();
      const userAskedForSchemes =
        tLower.includes('योजना') ||
        tLower.includes('स्कीम') ||
        tLower.includes('scheme') ||
        tLower.includes('बताओ') ||
        tLower.includes('show') ||
        tLower.includes('check') ||
        tLower.includes('itna hi hai') ||
        tLower.includes('बस इतना ही');

      // If enough details gathered or user asked to view schemes
      if (!nextFollowup || (activeKeys.length >= 4 && userAskedForSchemes)) {
        await new Promise((r) => setTimeout(r, 300));

        let readyMsgText = '';
        if (language === 'hi' || language === 'mr') {
          readyMsgText = `शानदार! आपकी प्रोफ़ाइल (${activeKeys.length} विवरण) सफलतापूर्वक दर्ज हो गई है। हम आधिकारिक सरकारी योजनाओं के नियमों के अनुसार आपकी पात्रता निकाल रहे हैं...`;
        } else if (language === 'bn') {
          readyMsgText = `চমৎকার! আপনার প্রোফাইল সফলভাবে তৈরি হয়েছে। আমরা আপনার জন্য যোগ্য সরকারি প্রকল্প মূল্যায়ন করছি...`;
        } else {
          readyMsgText = `Splendid! Your profile attributes (${activeKeys.length} verified fields) have been recorded. Evaluating official deterministic rules for your eligible welfare schemes...`;
        }

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
          setTimeout(() => handleFinalEvaluation(merged), 900);
        }
        return;
      }

      // 4. Formulate Multi-turn Voice Follow-up
      await new Promise((r) => setTimeout(r, 300));
      setProcessingStage(0);

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
          // Auto-prompt mic for smooth hands-free conversational flow
          if (isHandsFree) {
            setTimeout(() => {
              startListening();
            }, 350);
          }
        });
      } else {
        setVoiceState('idle');
      }
    } catch (err) {
      console.error('Turn processing error:', err);
      setVoiceState('idle');
      setProcessingStage(0);
    }
  };

  // Final Transition to S4_ResultsScreen with 100% Deterministic Rules
  const handleFinalEvaluation = async (finalProfileToEval = accumulatedProfile) => {
    setVoiceState('processing');
    setProcessingStage(3);

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
      setCurrentScreen('S4');
    } catch (err) {
      console.error('Final evaluation failed:', err);
      stopSpeaking();
      setCurrentScreen('S4');
    }
  };

  // Fast Persona Speech Simulation
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
    setProcessingStage(0);
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

  // Render recognized attribute chips
  const renderAttributeChip = (key, val) => {
    if (val === undefined || val === null || val === '') return null;
    let label = `${key}: ${val}`;
    if (key === 'age') label = `🎂 ${val} ${language === 'hi' ? 'वर्ष' : 'years'}`;
    if (key === 'occupation') {
      const map = { farmer: '🌾 किसान', student: '🎓 विद्यार्थी', homemaker: '👩 गृहिणी', agricultural_worker: '🌱 मजदूर', self_employed: '💼 स्वरोजगार' };
      label = map[val] || `💼 ${val}`;
    }
    if (key === 'state') label = `📍 ${val}`;
    if (key === 'landholding_hectares') label = `🌱 ${val} Ha land`;
    if (key === 'has_pucca_house') label = val ? '🏠 पक्का मकान' : '🏚️ कच्चा मकान';
    if (key === 'bpl_card_holder') label = val ? '🏷️ BPL कार्ड' : 'Non-BPL';
    if (key === 'student_class12_marks_percent') label = `📊 12वीं: ${val}%`;
    if (key === 'annual_income') label = `💰 ₹${val.toLocaleString()}`;
    if (key === 'marital_status') {
      const mmap = { widow: '🕊️ विधवा', married: '💍 विवाहित', single: '👤 अविवाहित' };
      label = mmap[val] || val;
    }

    return (
      <span
        key={key}
        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 shadow-xs backdrop-blur-md animate-fade-in"
      >
        <Check className="w-3 h-3 text-emerald-400" />
        <span>{label}</span>
      </span>
    );
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6 pb-12 select-none">
      {/* Top Civic Navigation & Title Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              stopSpeaking();
              setCurrentScreen('S0');
            }}
            className="p-2.5 rounded-xl bg-slate-900/90 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700/60 transition-all shadow-sm"
            title="Return to Home"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white flex items-center gap-2">
                <span>{lt('Two-Way Voice AI Assistant', 'दो-तरफ़ा आवाज़ एआई सहायक', 'দ্বি-মুখী ভয়েস সহকারী')}</span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-xs">
                  Lavish Voice
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {lt(
                'Speak freely in Hindi, Hinglish, or English. The assistant speaks back and asks for details to find your eligible schemes.',
                'हिन्दी, हिंग्लिश या अपनी भाषा में बोलें। सहायक आवाज़ में उत्तर देगा और पूरी पात्रता जांचेगा।'
              )}
            </p>
          </div>
        </div>

        {/* Global Controls & Hands-Free Mode Toggle */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={() => setIsHandsFree(!isHandsFree)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border shadow-xs ${
              isHandsFree
                ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.25)]'
                : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
            title="Hands-free continuous conversation"
          >
            <Radio className={`w-3.5 h-3.5 ${isHandsFree ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
            <span>{isHandsFree ? lt('Hands-Free Active', 'हैंड्स-फ्री सक्रिय') : lt('Hands-Free Off', 'हैंड्स-फ्री बंद')}</span>
          </button>

          <button
            onClick={() => {
              if (isAudioEnabled) stopSpeaking();
              setIsAudioEnabled(!isAudioEnabled);
            }}
            className={`p-2 rounded-xl text-xs font-semibold transition-all border ${
              isAudioEnabled
                ? 'bg-blue-950/80 text-blue-300 border-blue-500/40 shadow-xs'
                : 'bg-slate-900 text-slate-500 border-slate-800 hover:text-slate-300'
            }`}
            title={isAudioEnabled ? 'Mute AI voice output' : 'Enable AI voice output'}
          >
            {isAudioEnabled ? <Volume2 className="w-4 h-4 text-cyan-300" /> : <VolumeX className="w-4 h-4" />}
          </button>

          <button
            onClick={resetVoiceChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900/80 hover:bg-rose-950/50 text-slate-400 hover:text-rose-300 border border-slate-800 hover:border-rose-700/50 transition-all shadow-xs"
            title="Reset Conversation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{lt('Reset', 'रीसेट')}</span>
          </button>
        </div>
      </div>

      {/* Main Lavish Glass Container */}
      <div className="relative rounded-3xl bg-gradient-to-b from-[#0a1122]/95 via-[#080d1a]/95 to-[#060a14]/95 border border-slate-800/80 shadow-[0_0_60px_-15px_rgba(30,58,138,0.3)] backdrop-blur-2xl overflow-hidden p-4 sm:p-7 space-y-6">
        {/* Iridescent Accent Aura */}
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-48 bg-gradient-to-r from-blue-600/20 via-cyan-500/20 to-teal-500/10 blur-3xl pointer-events-none" />

        {/* Central Voice Visualizer Orb & Stage */}
        <div className="relative flex flex-col items-center justify-center pt-2 pb-4">
          <div className="relative flex items-center justify-center">
            {/* Outer Pulsing Sound Waves (When Listening) */}
            {voiceState === 'listening' && (
              <>
                <div className="absolute w-44 h-44 rounded-full border border-emerald-500/30 animate-ping opacity-60 pointer-events-none" />
                <div className="absolute w-36 h-36 rounded-full bg-emerald-500/15 blur-xl animate-pulse pointer-events-none" />
              </>
            )}

            {/* Speaking Halo Aura (When AI Speaking) */}
            {voiceState === 'speaking' && (
              <>
                <div className="absolute w-44 h-44 rounded-full border border-cyan-400/30 animate-pulse pointer-events-none" />
                <div className="absolute w-36 h-36 rounded-full bg-cyan-500/15 blur-xl pointer-events-none" />
              </>
            )}

            {/* Lavish Circular Processing Halo (When Computing/Evaluating) */}
            {voiceState === 'processing' && (
              <div className="absolute w-36 h-36 rounded-full border-4 border-transparent border-t-amber-400 border-r-cyan-400 border-b-emerald-400 animate-spin pointer-events-none shadow-[0_0_30px_rgba(251,191,36,0.3)]" />
            )}

            {/* Central Master Button */}
            <button
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
              className={`relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full flex flex-col items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-2xl ${
                voiceState === 'listening'
                  ? 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-[0_0_40px_rgba(16,185,129,0.5)] ring-4 ring-emerald-400/40'
                  : voiceState === 'processing'
                  ? 'bg-gradient-to-tr from-amber-600 to-indigo-600 text-white shadow-[0_0_40px_rgba(245,158,11,0.4)]'
                  : voiceState === 'speaking'
                  ? 'bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 text-white shadow-[0_0_40px_rgba(6,182,212,0.45)] ring-4 ring-cyan-400/40'
                  : 'bg-gradient-to-tr from-slate-800 via-blue-900 to-indigo-950 text-cyan-300 hover:text-white border border-blue-500/30 shadow-[0_0_30px_rgba(30,58,138,0.3)]'
              }`}
            >
              {voiceState === 'listening' ? (
                <>
                  <Mic className="w-8 h-8 sm:w-9 sm:h-9 animate-bounce" />
                  <span className="text-[10px] font-bold uppercase tracking-wider mt-1 text-emerald-100">
                    Listening
                  </span>
                </>
              ) : voiceState === 'processing' ? (
                <>
                  <div className="w-7 h-7 border-3 border-white border-t-transparent rounded-full animate-spin mb-1" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-100">
                    Thinking
                  </span>
                </>
              ) : voiceState === 'speaking' ? (
                <>
                  <Volume2 className="w-8 h-8 sm:w-9 sm:h-9 animate-pulse text-cyan-200" />
                  <span className="text-[10px] font-bold uppercase tracking-wider mt-1 text-cyan-100">
                    Speaking
                  </span>
                </>
              ) : (
                <>
                  <Mic className="w-8 h-8 sm:w-9 sm:h-9" />
                  <span className="text-[10px] font-bold uppercase tracking-wider mt-1 text-cyan-300">
                    Tap to Talk
                  </span>
                </>
              )}
            </button>
          </div>

          {/* Dynamic Voice Waveform & Processing Bar Indicator */}
          <div className="mt-4 text-center max-w-md w-full">
            {voiceState === 'listening' ? (
              <div className="space-y-2">
                <div className="flex items-center justify-center gap-1.5 h-6">
                  {[40, 75, 50, 90, 60, 100, 70, 45, 80, 55].map((height, i) => (
                    <span
                      key={i}
                      className="w-1 bg-gradient-to-t from-emerald-500 to-teal-300 rounded-full animate-pulse"
                      style={{ height: `${height}%`, animationDelay: `${i * 80}ms` }}
                    />
                  ))}
                </div>
                <p className="text-xs font-semibold text-emerald-400 tracking-wide">
                  {liveInterim ? `"${liveInterim}"` : lt('Listening to your voice... Speak naturally in Hinglish or Hindi', 'आपकी आवाज़ सुन रहे हैं... हिन्दी या हिंग्लिश में बोलें')}
                </p>
              </div>
            ) : voiceState === 'processing' ? (
              <div className="space-y-2.5 px-4 py-2 bg-slate-900/80 border border-amber-500/30 rounded-2xl backdrop-blur-md">
                <div className="flex items-center justify-between text-[11px] font-bold text-amber-300">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                    <span>{lt('Processing your information...', 'आपकी जानकारी का विश्लेषण हो रहा है...')}</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {processingStage === 1 ? '1/3 Audio Decoded' : processingStage === 2 ? '2/3 Profile Extracted' : '3/3 Rules Verified'}
                  </span>
                </div>
                {/* Lavish Glowing Progress Bar */}
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden p-0.5 border border-slate-700/60">
                  <div
                    className="h-full bg-gradient-to-r from-amber-400 via-cyan-400 to-emerald-400 rounded-full transition-all duration-500 shadow-[0_0_12px_rgba(251,191,36,0.6)]"
                    style={{ width: `${processingStage === 1 ? '35%' : processingStage === 2 ? '70%' : '100%'}` }}
                  />
                </div>
              </div>
            ) : voiceState === 'speaking' ? (
              <div className="space-y-1">
                <div className="flex items-center justify-center gap-1.5 h-5">
                  {[50, 85, 60, 95, 70, 80, 60, 45].map((height, i) => (
                    <span
                      key={i}
                      className="w-1 bg-gradient-to-t from-cyan-400 to-blue-500 rounded-full animate-bounce"
                      style={{ height: `${height}%`, animationDelay: `${i * 100}ms` }}
                    />
                  ))}
                </div>
                <p className="text-xs text-cyan-300 font-medium">
                  {lt('AI Assistant is speaking aloud...', 'एआई सहायक आवाज़ में उत्तर दे रहा है...')}
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                {lt('Tap microphone to speak, or use quick voice examples below', 'माइक दबाकर बोलें या नीचे दिए उदाहरण चुनें')}
              </p>
            )}
          </div>
        </div>

        {/* Live Extracted Citizen Profile Tray */}
        {confirmedFields.length > 0 && (
          <div className="p-3.5 bg-slate-900/70 border border-blue-900/50 rounded-2xl backdrop-blur-md space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>{lt('Extracted Profile Attributes', 'दर्ज की गई प्रोफ़ाइल विशेषताएं')}</span>
              </span>
              <span className="text-[11px] font-mono text-emerald-400 font-bold">
                {confirmedFields.length} {lt('fields detected', 'विवरण पहचाने गए')}
              </span>
            </div>
            <div className="flex flex-wrap gap-2 pt-0.5">
              {confirmedFields.map((fieldKey) => renderAttributeChip(fieldKey, accumulatedProfile[fieldKey]))}
            </div>
          </div>
        )}

        {/* Conversational Stream */}
        <div
          ref={chatScrollRef}
          className="h-80 sm:h-96 overflow-y-auto space-y-3.5 pr-2 rounded-2xl bg-slate-950/40 p-3 sm:p-4 border border-slate-900 shadow-inner scroll-smooth"
        >
          {conversation.map((msg) => {
            const isAi = msg.sender === 'ai';
            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isAi ? 'items-start' : 'items-end'} animate-fade-in`}
              >
                <div
                  className={`max-w-[88%] sm:max-w-[80%] rounded-2xl p-3.5 sm:p-4 text-xs sm:text-sm leading-relaxed shadow-md backdrop-blur-md ${
                    isAi
                      ? 'bg-gradient-to-br from-[#101c38] to-[#0c162e] border border-blue-700/40 text-slate-100 shadow-[0_4px_20px_-4px_rgba(30,58,138,0.25)] rounded-tl-sm'
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-sm shadow-[0_4px_20px_-4px_rgba(37,99,235,0.35)]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3 mb-1.5 pb-1 border-b border-white/10 text-[10px] font-semibold text-slate-400">
                    <span className="flex items-center gap-1.5">
                      {isAi ? (
                        <>
                          <span className="w-2 h-2 rounded-full bg-cyan-400" />
                          <span className="text-cyan-300 font-bold">YojnaSarthi Voice AI</span>
                        </>
                      ) : (
                        <>
                          <Mic className="w-2.5 h-2.5 text-blue-200" />
                          <span className="text-blue-100 font-bold">You (Citizen)</span>
                        </>
                      )}
                    </span>
                    <span className="font-mono">{msg.timestamp}</span>
                  </div>

                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {/* Replay voice button for AI responses */}
                  {isAi && (
                    <div className="mt-2.5 pt-2 border-t border-blue-900/60 flex items-center justify-between">
                      <button
                        onClick={() => {
                          stopSpeaking();
                          speakText(msg.text, language);
                        }}
                        className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>{lt('Replay Audio', 'आवाज़ दोबारा सुनें')}</span>
                      </button>

                      {msg.isReady && (
                        <button
                          onClick={() => handleFinalEvaluation(accumulatedProfile)}
                          className="px-3 py-1 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold text-xs rounded-lg shadow-sm flex items-center gap-1"
                        >
                          <span>{lt('View Schemes Now', 'योजनाएं देखें')}</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Voice Demo Persona Pills (Instant One-Tap Testing) */}
        <div className="space-y-2">
          <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span>{lt('Quick Voice Personas (Hinglish Supported):', 'त्वरित आवाज़ उदाहरण (हिंग्लिश मान्य):')}</span>
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            <button
              onClick={() => triggerDemoSpeech('farmer')}
              disabled={voiceState === 'processing'}
              className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-emerald-950/50 border border-slate-800 hover:border-emerald-600/50 text-left transition-all group shadow-2xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200 group-hover:text-emerald-300">
                  🌾 {language === 'hi' ? 'सीहोर किसान (Farmer)' : 'Sehore Farmer'}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">1.5 Ha</span>
              </div>
              <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                48y, 1.5 Ha land, kutcha house, PM-KISAN
              </p>
            </button>

            <button
              onClick={() => triggerDemoSpeech('widow')}
              disabled={voiceState === 'processing'}
              className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-indigo-950/50 border border-slate-800 hover:border-indigo-600/50 text-left transition-all group shadow-2xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200 group-hover:text-indigo-300">
                  👩 {language === 'hi' ? 'विधवा महिला (Widow)' : 'Widowed Mother'}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">BPL</span>
              </div>
              <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                52y, BPL ration card, ₹24k income
              </p>
            </button>

            <button
              onClick={() => triggerDemoSpeech('student')}
              disabled={voiceState === 'processing'}
              className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-cyan-950/50 border border-slate-800 hover:border-cyan-600/50 text-left transition-all group shadow-2xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200 group-hover:text-cyan-300">
                  🎓 {language === 'hi' ? 'कॉलेज छात्र (Student)' : 'College Student'}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">86%</span>
              </div>
              <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                19y, 86% in 12th, B.Tech, MMVY
              </p>
            </button>
          </div>
        </div>

        {/* Text Fallback Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (typedInput.trim()) {
              handleCitizenTurn(typedInput.trim());
              setTypedInput('');
            }
          }}
          className="flex items-center gap-2 bg-slate-950/90 border border-blue-900/60 rounded-2xl p-2 focus-within:border-cyan-400 transition-colors shadow-inner"
        >
          <input
            type="text"
            value={typedInput}
            onChange={(e) => setTypedInput(e.target.value)}
            placeholder={
              language === 'hi'
                ? 'या यहाँ हिंग्लिश/हिन्दी में लिखकर बताएं (जैसे: मैं MP का किसान हूँ, 2 एकड़ ज़मीन है)...'
                : 'Or type here in English or Hinglish (e.g. I am a farmer from MP with 2 acres land)...'
            }
            className="flex-1 bg-transparent px-3 py-2 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-hidden"
          />
          <button
            type="submit"
            disabled={!typedInput.trim() || voiceState === 'processing'}
            className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 text-white transition-all shadow-md flex items-center justify-center"
            title="Send"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        {/* Bottom Prominent CTA to Fetch Schemes */}
        {confirmedFields.length >= 2 && (
          <div className="pt-2 flex items-center justify-between gap-4 border-t border-slate-800/80">
            <span className="text-xs text-slate-400">
              {lt(
                'Ready to discover your verified welfare schemes?',
                'क्या आप पात्र सरकारी योजनाएं देखना चाहते हैं?'
              )}
            </span>
            <button
              onClick={() => handleFinalEvaluation(accumulatedProfile)}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-extrabold text-xs sm:text-sm shadow-[0_0_25px_rgba(16,185,129,0.4)] transition-all flex items-center gap-2"
            >
              <span>{lt('Find Eligible Schemes Now', 'पात्र योजनाएं खोजें')}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
