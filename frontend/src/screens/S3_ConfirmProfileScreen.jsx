import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { evaluateCitizenProfile } from '../services/api';
import { ArrowLeft, CheckCircle2, ShieldCheck, ArrowRight, Info, AlertTriangle } from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S3_ConfirmProfileScreen() {
  const { language, t, lt } = useLanguage();
  const { profile, setProfile, setCurrentScreen, setEvaluationResults } = useSession();

  const [editableProfile, setEditableProfile] = useState({ ...profile });
  const [isEvaluating, setIsEvaluating] = useState(false);

  const handleFieldChange = (key, val) => {
    setEditableProfile((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const handleConfirmAndEvaluate = async () => {
    setIsEvaluating(true);
    const activeKeys = Object.keys(editableProfile).filter(
      (k) => editableProfile[k] !== null && editableProfile[k] !== undefined && editableProfile[k] !== '' && k !== 'confirmed_fields'
    );
    const finalProfile = {
      ...editableProfile,
      confirmed_fields: activeKeys,
    };

    setProfile(finalProfile);

    try {
      const evalResp = await evaluateCitizenProfile(finalProfile);
      setEvaluationResults(evalResp);
      setCurrentScreen('S4');
    } catch (err) {
      console.error('Evaluation failed:', err);
      setCurrentScreen('S4');
    } finally {
      setIsEvaluating(false);
    }
  };

  const fieldLabels = {
    age: { hi: 'आयु (वर्ष)', en: 'Age (Years)' },
    gender: { hi: 'लिंग (Gender)', en: 'Gender' },
    marital_status: { hi: 'वैवाहिक स्थिति (Marital Status)', en: 'Marital Status' },
    state: { hi: 'राज्य (Domicile State)', en: 'State' },
    residence_type: { hi: 'क्षेत्र (Rural/Urban)', en: 'Residence' },
    occupation: { hi: 'व्यवसाय (Occupation)', en: 'Occupation' },
    annual_income: { hi: 'वार्षिक आय (Annual Income ₹)', en: 'Annual Family Income (₹)' },
    landholding_hectares: { hi: 'कृषि भूमि (Land in Hectares)', en: 'Agricultural Land (Hectares)' },
    student_class12_marks_percent: { hi: '12वीं बोर्ड प्रतिशत (Class 12 %)', en: 'Class 12th Marks (%)' },
    enrolled_higher_education: { hi: 'उच्च शिक्षा में प्रवेश', en: 'Higher Education Admission' },
    has_pucca_house: { hi: 'पक्का मकान है?', en: 'Owns a Pucca House?' },
    bpl_card_holder: { hi: 'बीपीएल राशन कार्ड?', en: 'BPL Card Holder?' },
  };

  return (
    <div className="max-w-4xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Navigation & Header */}
        <div className="space-y-2">
          <button
            onClick={() => setCurrentScreen('S2')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t('back')}</span>
          </button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
                {t('confirm_profile_title')}
              </h2>
              <p className="text-sm text-slate-500 mt-1 leading-relaxed">
                {t('confirm_profile_subtitle')}
              </p>
            </div>
            <AudioSpeaker
              text={`${t('confirm_profile_title')}। ${t('confirm_profile_subtitle')}`}
              className="mt-1 flex-shrink-0"
            />
          </div>
        </div>

        {/* Verification Guarantee Alert */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs sm:text-sm text-blue-900 flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-700 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            {lt('Deterministic Rules Guarantee: Review the extracted attributes below. You can modify any value. Only confirmed values will be processed by the official rule engine.', 'गोपनीयता एवं सटीकता नियम: एआई द्वारा निकाले गए विवरण की नीचे समीक्षा करें। आप किसी भी मान को बदल सकते हैं। केवल आपके द्वारा पुष्ट जानकारी के आधार पर ही सरकारी नियमों का मूल्यांकन होगा।')}
          </p>
        </div>

        {/* Responsive Grid of Profile Field Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Age */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.age.en, fieldLabels.age.hi)}
            </label>
            <input
              type="number"
              value={editableProfile.age !== undefined && editableProfile.age !== null ? editableProfile.age : ''}
              onChange={(e) => handleFieldChange('age', e.target.value ? parseInt(e.target.value) : null)}
              placeholder={lt('e.g. 48', 'उदा. 48')}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-slate-50/50"
            />
          </div>

          {/* Gender */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.gender.en, fieldLabels.gender.hi)}
            </label>
            <select
              value={editableProfile.gender || ''}
              onChange={(e) => handleFieldChange('gender', e.target.value || null)}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white"
            >
              <option value="">{lt('-- Select --', '-- चयन करें --')}</option>
              <option value="male">{lt('Male', 'पुरुष (Male)')}</option>
              <option value="female">{lt('Female', 'महिला (Female)')}</option>
              <option value="transgender">{lt('Transgender', 'ट्रांसजेंडर (Transgender)')}</option>
            </select>
          </div>

          {/* Marital Status */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.marital_status.en, fieldLabels.marital_status.hi)}
            </label>
            <select
              value={editableProfile.marital_status || ''}
              onChange={(e) => handleFieldChange('marital_status', e.target.value || null)}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white"
            >
              <option value="">{lt('-- Select --', '-- चयन करें --')}</option>
              <option value="widow">{lt('Widow', 'विधवा (Widow)')}</option>
              <option value="married">{lt('Married', 'विवाहित (Married)')}</option>
              <option value="single">{lt('Single', 'अविवाहित (Single)')}</option>
              <option value="divorced">{lt('Divorced / Deserted', 'तलाकशुदा / परित्यक्ता')}</option>
            </select>
          </div>

          {/* State */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.state.en, fieldLabels.state.hi)}
            </label>
            <select
              value={editableProfile.state || ''}
              onChange={(e) => handleFieldChange('state', e.target.value || null)}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white"
            >
              <option value="">{lt('-- Select --', '-- चयन करें --')}</option>
              <option value="Madhya Pradesh">{lt('Madhya Pradesh', 'मध्य प्रदेश (Madhya Pradesh)')}</option>
              <option value="Maharashtra">{lt('Maharashtra', 'महाराष्ट्र (Maharashtra)')}</option>
              <option value="Uttar Pradesh">{lt('Uttar Pradesh', 'उत्तर प्रदेश (Uttar Pradesh)')}</option>
              <option value="Rajasthan">{lt('Rajasthan', 'राजस्थान (Rajasthan)')}</option>
              <option value="Bihar">{lt('Bihar', 'बिहार (Bihar)')}</option>
              <option value="Other">{lt('Other State / UT', 'अन्य राज्य / केंद्र शासित प्रदेश')}</option>
            </select>
          </div>

          {/* Occupation */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.occupation.en, fieldLabels.occupation.hi)}
            </label>
            <select
              value={editableProfile.occupation || ''}
              onChange={(e) => handleFieldChange('occupation', e.target.value || null)}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white"
            >
              <option value="">{lt('-- Select --', '-- चयन करें --')}</option>
              <option value="farmer">{lt('Farmer', 'किसान (Farmer)')}</option>
              <option value="student">{lt('Student', 'छात्र (Student)')}</option>
              <option value="agricultural_worker">{lt('Agricultural Worker', 'खेतिहर मजदूर')}</option>
              <option value="homemaker">{lt('Homemaker', 'गृहिणी (Homemaker)')}</option>
              <option value="self_employed">{lt('Self Employed', 'स्व-रोजगार')}</option>
              <option value="unemployed">{lt('Unemployed', 'बेरोजगार')}</option>
            </select>
          </div>

          {/* Annual Income */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.annual_income.en, fieldLabels.annual_income.hi)}
            </label>
            <input
              type="number"
              value={editableProfile.annual_income !== undefined && editableProfile.annual_income !== null ? editableProfile.annual_income : ''}
              onChange={(e) => handleFieldChange('annual_income', e.target.value ? parseFloat(e.target.value) : null)}
              placeholder={lt('e.g. ₹65,000', '₹ 65,000')}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-slate-50/50"
            />
          </div>

          {/* Landholding Hectares (always shown or dynamic) */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.landholding_hectares.en, fieldLabels.landholding_hectares.hi)}
            </label>
            <input
              type="number"
              step="0.1"
              value={editableProfile.landholding_hectares !== undefined && editableProfile.landholding_hectares !== null ? editableProfile.landholding_hectares : ''}
              onChange={(e) => handleFieldChange('landholding_hectares', e.target.value !== '' ? parseFloat(e.target.value) : null)}
              placeholder={lt('1.5 (Hectares)', '1.5 (हेक्टेयर)')}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-slate-50/50"
            />
          </div>

          {/* Student Class 12 Marks */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-1.5">
            <label className="text-xs font-bold text-slate-700 block">
              {lt(fieldLabels.student_class12_marks_percent.en, fieldLabels.student_class12_marks_percent.hi)}
            </label>
            <input
              type="number"
              step="0.5"
              value={editableProfile.student_class12_marks_percent !== undefined && editableProfile.student_class12_marks_percent !== null ? editableProfile.student_class12_marks_percent : ''}
              onChange={(e) => handleFieldChange('student_class12_marks_percent', e.target.value !== '' ? parseFloat(e.target.value) : null)}
              placeholder={lt('86 %', '86 %')}
              className="w-full p-2.5 text-sm font-semibold border rounded-lg border-slate-300 focus:border-blue-600 focus:outline-hidden bg-slate-50/50"
            />
          </div>
        </div>
      </div>

      {/* Primary CTA */}
      <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-end gap-3">
        <button
          onClick={handleConfirmAndEvaluate}
          disabled={isEvaluating}
          className="w-full sm:w-auto px-8 py-3.5 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 min-h-[48px]"
        >
          {isEvaluating ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>{lt('Evaluating official rules...', 'पात्रता नियम जाँचे जा रहे हैं...')}</span>
            </div>
          ) : (
            <>
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span>{t('confirm_and_evaluate')}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
