import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { parseFreeTextDescription } from '../services/api';
import { ArrowLeft, ArrowRight, Mic, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import VoiceMic from '../components/VoiceMic';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S2_FreeTextInputScreen() {
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen, setProfile } = useSession();

  const [descriptionText, setDescriptionText] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

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
    }
  ];

  const handleVoiceTranscript = (text) => {
    setDescriptionText((prev) => (prev ? `${prev} ${text}` : text));
  };

  const handleSubmit = async () => {
    if (!descriptionText.trim()) return;
    setIsParsing(true);
    setErrorMsg('');

    try {
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
      );
    } finally {
      setIsParsing(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Navigation & Header */}
        <div className="space-y-2">
          <button
            onClick={() => setCurrentScreen('S0')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t('back')}</span>
          </button>

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
          </div>
        </div>

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
              </div>
            </div>

            {descriptionText && (
              <button
                type="button"
                onClick={() => setDescriptionText('')}
                className="text-xs text-slate-500 hover:text-rose-600 font-semibold underline transition-colors self-end sm:self-auto"
              >
                {lt('Clear Text', 'पाठ साफ़ करें (Clear)')}
              </button>
            )}
          </div>
        </div>

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
      </div>
    </div>
  );
}
