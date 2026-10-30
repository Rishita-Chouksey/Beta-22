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
  const { language, t } = useLanguage();
  const { setCurrentScreen } = useSession();

  const [inputField, setInputField] = useState('');
  const [photoPreview, setPhotoPreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [explanations, setExplanations] = useState(null);
  const [generalAdvice, setGeneralAdvice] = useState('');

  const quickCommonFields = [
    { label_hi: 'खसरा / खतौनी नंबर', label_en: 'Khasra Number', val: 'खसरा / खतौनी क्रमांक' },
    { label_hi: 'आधार एनपीसीआई / डीबीटी', label_en: 'NPCI / DBT Seeding', val: 'आधार बैंक डीबीटी मैपिंग' },
    { label_hi: 'समग्र आईडी', label_en: 'Samagra ID', val: 'समग्र परिवार एवं सदस्य आईडी' },
    { label_hi: 'राशन कार्ड क्रमांक', label_en: 'Ration Card No.', val: 'राशन कार्ड क्रमांक' }
  ];

  const handlePhotoUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleExplain = async (fieldToUse = inputField) => {
    setIsAnalyzing(true);
    try {
      const resp = await requestFormHelp(fieldToUse || null, photoPreview || null, language);
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
                language === 'hi'
                  ? 'सरकारी आवेदन फॉर्म के कठिन शब्दों को समझने के लिए शब्द लिखें या फोटो अपलोड करें।'
                  : 'Enter complex terms or upload a photo of your application form for simple explanations.'
              }
              className="mt-1 flex-shrink-0"
            />
          </div>
        </div>

        {/* AI Disclaimer Alert */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3 text-xs sm:text-sm text-amber-900">
          <Info className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            {t('ai_disclaimer')} {language === 'hi' ? 'अपलोड की गई फोटो सर्वर पर कभी स्थायी रूप से सहेजी नहीं जाती।' : 'Uploaded photos are processed in-memory only and never saved.'}
          </p>
        </div>

        {/* Search & Photo Input Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 block uppercase tracking-wider">
              {language === 'hi' ? 'फॉर्म का शब्द या कॉलम का नाम खोजें:' : 'Search Form Term / Field:'}
            </label>
            <div className="flex flex-col sm:flex-row gap-2.5">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={inputField}
                  onChange={(e) => setInputField(e.target.value)}
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
              {language === 'hi' ? 'लोकप्रिय सरकारी शब्दावली:' : 'Common Terms:'}
            </span>
            <div className="flex flex-wrap gap-2">
              {quickCommonFields.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setInputField(q.val);
                    handleExplain(q.val);
                  }}
                  className="text-xs font-semibold bg-slate-100 hover:bg-blue-50 hover:text-blue-900 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors"
                >
                  {language === 'hi' ? q.label_hi : q.label_en}
                </button>
              ))}
            </div>
          </div>

          {/* Optional Photo Upload */}
          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <label className="cursor-pointer bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs px-4 py-2.5 rounded-xl border border-slate-300 inline-flex items-center gap-2 min-h-[40px] transition-colors">
              <Camera className="w-4 h-4 text-blue-700" />
              <span>{language === 'hi' ? 'फॉर्म की फोटो चुनें (Upload Photo)' : 'Upload Form Photo'}</span>
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
                <button
                  type="button"
                  onClick={() => setPhotoPreview(null)}
                  className="text-xs text-rose-600 font-bold underline"
                >
                  {language === 'hi' ? 'फोटो हटाएं' : 'Remove Photo'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results / Explanations Display */}
        {isAnalyzing ? (
          <div className="text-center py-12 bg-white border border-slate-200 rounded-2xl">
            <div className="w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-600">
              {language === 'hi' ? 'सरकारी शब्दावली का सरल विश्लेषण हो रहा है...' : 'Analyzing terminology with AI assistant...'}
            </p>
          </div>
        ) : explanations && (
          <div className="space-y-4">
            {generalAdvice && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs sm:text-sm text-emerald-950 leading-relaxed font-medium">
                <strong className="text-emerald-900 block mb-0.5">
                  {language === 'hi' ? '💡 महत्वपूर्ण आधिकारिक सलाह: ' : '💡 Administrative Tip: '}
                </strong>
                {generalAdvice}
              </div>
            )}

            <div className="space-y-3">
              {explanations.map((item, idx) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-xs">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="font-bold text-base text-blue-950">
                      {language === 'hi' ? item.field_name_hi || item.field_name : item.field_name}
                    </h4>
                    <AudioSpeaker text={`${item.field_name}। ${item.explanation}`} className="w-7 h-7" />
                  </div>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                    {item.explanation}
                  </p>
                  <div className="text-xs text-slate-600 bg-slate-50 border border-slate-100 p-3 rounded-xl">
                    <strong className="text-slate-900 block mb-0.5">
                      {language === 'hi' ? 'फॉर्म में क्या भरें (उदाहरण): ' : 'Example Value: '}
                    </strong>
                    {item.example}
                  </div>
                </div>
              ))}
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
