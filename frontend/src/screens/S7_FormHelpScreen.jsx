import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { requestFormHelp } from '../services/api';
import {
  ArrowLeft,
  Camera,
  Upload,
  HelpCircle,
  FileQuestion,
  Sparkles,
  Info,
  CheckCircle,
  AlertCircle,
  Search
} from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S7_FormHelpScreen() {
  const { language, t, lt } = useLanguage();
  const { setCurrentScreen } = useSession();

  const [inputField, setInputField] = useState('');
  const [photoPreview, setPhotoPreview] = useState(null);
  const [analyzedFromPhoto, setAnalyzedFromPhoto] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [explanations, setExplanations] = useState(null);
  const [generalAdvice, setGeneralAdvice] = useState('');

  const quickCommonFields = [
    {
      label_en: 'Khasra Number',
      label_hi: 'खसरा / खतौनी नंबर',
      label_mr: 'सातबारा / खसरा नंबर',
      label_bn: 'খতিয়ান / দাগ নম্বর',
      val: 'खसरा / खतौनी क्रमांक'
    },
    {
      label_en: 'NPCI / DBT Seeding',
      label_hi: 'आधार एनपीसीआई / डीबीटी',
      label_mr: 'आधार बँक डीबीटी मॅपिंग',
      label_bn: 'আধার ব্যাঙ্ক ডিবিটি ম্যাপিং',
      val: 'आधार बैंक डीबीटी मैपिंग'
    },
    {
      label_en: 'Samagra ID',
      label_hi: 'समग्र आईडी',
      label_mr: 'समग्र कुटुंब व सदस्य आयडी',
      label_bn: 'সমগ্র পরিবার ও সদস্য আইডি',
      val: 'समग्र परिवार एवं सदस्य आईडी'
    },
    {
      label_en: 'Ration Card No.',
      label_hi: 'राशन कार्ड क्रमांक',
      label_mr: 'रेशन कार्ड क्रमांक',
      label_bn: 'রেশন কার্ড নম্বর',
      val: 'राशन कार्ड क्रमांक'
    },
    {
      label_en: 'Income Certificate',
      label_hi: 'आय प्रमाण पत्र',
      label_mr: 'उत्पन्न दाखला',
      label_bn: 'আয়ের শংসাপত্র',
      val: 'आय प्रमाण पत्र'
    },
    {
      label_en: 'Domicile Certificate',
      label_hi: 'मूल निवास प्रमाण पत्र',
      label_mr: 'अधिवास दाखला',
      label_bn: 'আবাসিক শংসাপত্র',
      val: 'मूल निवास प्रमाण पत्र'
    }
  ];

  const handlePhotoUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = reader.result;
        setPhotoPreview(base64Data);
        setAnalyzedFromPhoto(true);
        // Automatically analyze photo fields immediately without requiring manual click
        handleExplain(inputField, base64Data);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleExplain = async (fieldToUse = inputField, photoToUse = photoPreview) => {
    setIsAnalyzing(true);
    try {
      const resp = await requestFormHelp(fieldToUse || null, photoToUse || null, language);
      setExplanations(resp.explanations || []);
      setGeneralAdvice(resp.general_guidance || '');
    } catch (err) {
      console.error('Form help error:', err);
    } finally {
      setIsAnalyzing(false);
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
                {t('form_help_title')}
              </h2>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                {t('form_help_subtitle')}
              </p>
            </div>
            <AudioSpeaker
              text={
                lt('Enter complex terms or upload a photo of your application form for simple explanations.', 'सरकारी आवेदन फॉर्म के कठिन शब्दों को समझने के लिए शब्द लिखें या फोटो अपलोड करें।')
              }
              className="mt-1 flex-shrink-0"
            />
          </div>
        </div>

        {/* AI Disclaimer Alert */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3 text-xs sm:text-sm text-amber-900">
          <Info className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            {t('ai_disclaimer')} {lt('Uploaded photos are processed in-memory only and never saved.', 'अपलोड की गई फोटो सर्वर पर कभी स्थायी रूप से सहेजी नहीं जाती।')}
          </p>
        </div>

        {/* Search & Photo Input Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 block uppercase tracking-wider">
              {lt('Search Form Term / Field:', 'फॉर्म का शब्द या कॉलम का नाम खोजें:')}
            </label>
            <div className="flex flex-col sm:flex-row gap-2.5">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={inputField}
                  onChange={(e) => setInputField(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleExplain(inputField, photoPreview);
                    }
                  }}
                  placeholder={t('form_field_input_placeholder')}
                  className="w-full text-sm sm:text-base p-3.5 pl-10 border border-slate-300 rounded-xl focus:border-blue-600 focus:outline-hidden bg-slate-50/50 min-h-[48px]"
                />
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              </div>
              <button
                type="button"
                onClick={() => handleExplain()}
                disabled={isAnalyzing}
                className="px-6 py-3 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 text-white font-semibold text-sm rounded-xl flex items-center justify-center gap-2 min-h-[48px] shadow-xs"
              >
                <Sparkles className="w-4 h-4 text-amber-300" />
                <span>{t('explain_field')}</span>
              </button>
            </div>
          </div>

          {/* Quick suggestions */}
          <div className="space-y-1.5 pt-1">
            <span className="text-xs font-semibold text-slate-500 block">
              {lt('Common Terms:', 'लोकप्रिय सरकारी शब्दावली:')}
            </span>
            <div className="flex flex-wrap gap-2">
              {quickCommonFields.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setInputField(q.val);
                    handleExplain(q.val, photoPreview);
                  }}
                  className="text-xs font-semibold bg-slate-100 hover:bg-blue-50 hover:text-blue-900 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors"
                >
                  {lt(q.label_en, q.label_hi, q.label_mr, q.label_bn)}
                </button>
              ))}
            </div>
          </div>

          {/* Optional Photo Upload */}
          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <label className="cursor-pointer bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs px-4 py-2.5 rounded-xl border border-slate-300 inline-flex items-center gap-2 min-h-[40px] transition-colors">
              <Camera className="w-4 h-4 text-blue-700" />
              <span>{lt('Upload Form Photo', 'फॉर्म की फोटो चुनें (Upload Photo)')}</span>
              <input
                type="file"
                accept="image/*"
                onChange={handlePhotoUpload}
                className="hidden"
              />
            </label>

            {photoPreview && (
              <div className="flex items-center gap-3">
                <img
                  src={photoPreview}
                  alt="Form preview"
                  className="w-10 h-10 object-cover rounded-lg border border-slate-300 shadow-2xs"
                />
                <div className="flex flex-col">
                  <span className="text-[11px] font-bold text-emerald-700 flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    {lt('Photo Analyzed', 'फोटो का विश्लेषण पूर्ण', 'फोटोचे विश्लेषण पूर्ण', 'ছবির বিশ্লেষণ সম্পন্ন')}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      setPhotoPreview(null);
                      setAnalyzedFromPhoto(false);
                    }}
                    className="text-xs text-rose-600 font-bold underline text-left cursor-pointer"
                  >
                    {lt('Remove Photo', 'फोटो हटाएं', 'फोटो काढा', 'ছবি সরান')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results / Explanations Display */}
        {isAnalyzing ? (
          <div className="text-center py-12 bg-white border border-slate-200 rounded-2xl shadow-xs">
            <div className="w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-700">
              {lt(
                'Analyzing official form terminology with AI assistant...',
                'सरकारी शब्दावली एवं फॉर्म कॉलम का सरल विश्लेषण हो रहा है...',
                'शासकीय अर्ज व शब्दावलीचे सोप्या भाषेत विश्लेषण करत आहोत...',
                'সরকারি পরিভাষা ও ফর্মের তথ্যের সহজ বিশ্লেষণ করা হচ্ছে...'
              )}
            </p>
          </div>
        ) : explanations && (
          <div className="space-y-4">
            {generalAdvice && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs sm:text-sm text-emerald-950 leading-relaxed font-medium">
                <strong className="text-emerald-900 block mb-0.5">
                  {lt('💡 Administrative Tip: ', '💡 महत्वपूर्ण आधिकारिक सलाह: ', '💡 महत्त्वाची प्रशासकीय सूचना: ', '💡 গুরুত্বপূর্ণ সরকারি পরামর্শ: ')}
                </strong>
                {generalAdvice}
              </div>
            )}

            <div className="space-y-3">
              {explanations.map((item, idx) => {
                const titleText = language === 'mr'
                  ? (item.field_name_mr || item.field_name_hi || item.field_name)
                  : language === 'bn'
                  ? (item.field_name_bn || item.field_name_hi || item.field_name)
                  : language === 'hi'
                  ? (item.field_name_hi || item.field_name)
                  : item.field_name;

                return (
                  <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-xs hover:border-blue-300 transition-colors">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-bold text-base text-blue-950">
                        {titleText}
                      </h4>
                      <AudioSpeaker text={`${titleText}। ${item.explanation}`} className="w-7 h-7" />
                    </div>
                    <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                      {item.explanation}
                    </p>
                    <div className="text-xs text-slate-600 bg-slate-50 border border-slate-100 p-3 rounded-xl">
                      <strong className="text-slate-900 block mb-0.5">
                        {lt('Example Value: ', 'फॉर्म में क्या भरें (उदाहरण): ', 'अर्जात काय भरावे (उदाहरण): ', 'ফর্মে কী লিখবেন (উদাহরণ): ')}
                      </strong>
                      {item.example}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer Navigation */}
      <div className="pt-6 border-t border-slate-200">
        <button
          onClick={() => setCurrentScreen('S0')}
          className="w-full sm:w-auto px-6 py-3 border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold rounded-xl text-sm transition-colors min-h-[48px]"
        >
          {t('back')}
        </button>
      </div>
    </div>
  );
}
