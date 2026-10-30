import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchNextQuestion, evaluateCitizenProfile } from '../services/api';
import { ArrowLeft, ArrowRight, SkipForward, Check, HelpCircle, Sparkles } from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S1_QuestionnaireScreen() {
  const { language, t, getBilingualText } = useLanguage();
  const { profile, updateProfile, setCurrentScreen, setEvaluationResults } = useSession();

  const [questionData, setQuestionData] = useState(null);
  const [selectedValue, setSelectedValue] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [stepNumber, setStepNumber] = useState(1);
  const [historyStack, setHistoryStack] = useState([]);

  useEffect(() => {
    loadNext();
  }, []);

  const loadNext = async (currentProf = profile) => {
    setIsLoading(true);
    try {
      const resp = await fetchNextQuestion(currentProf);
      if (!resp.has_more || !resp.question) {
        finishAndEvaluate(currentProf);
        return;
      }
      setQuestionData(resp.question);
      const existing = currentProf[resp.question.field];
      setSelectedValue(existing !== undefined && existing !== null ? existing : '');
      setStepNumber(resp.question.progress_index || stepNumber + 1);
    } catch (err) {
      console.error('Failed to load next question:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectOption = (val) => {
    setSelectedValue(val);
  };

  const handleNext = async () => {
    if (!questionData) return;
    const fieldKey = questionData.field;
    let finalVal = selectedValue;

    if (questionData.type === 'number') {
      finalVal = parseFloat(selectedValue) || 0;
    }

    const updated = {
      ...profile,
      [fieldKey]: finalVal,
      confirmed_fields: Array.from(new Set([...(profile.confirmed_fields || []), fieldKey]))
    };

    updateProfile(updated);
    setHistoryStack((prev) => [...prev, { field: fieldKey, value: profile[fieldKey] }]);
    setSelectedValue('');
    await loadNext(updated);
  };

  const handleSkip = async () => {
    if (!questionData) return;
    setHistoryStack((prev) => [...prev, { field: questionData.field, value: undefined }]);
    setSelectedValue('');
    await loadNext(profile);
  };

  const handleBack = () => {
    if (historyStack.length === 0) {
      setCurrentScreen('S0');
      return;
    }
    const lastItem = historyStack[historyStack.length - 1];
    setHistoryStack((prev) => prev.slice(0, -1));

    const updated = { ...profile };
    delete updated[lastItem.field];
    if (updated.confirmed_fields) {
      updated.confirmed_fields = updated.confirmed_fields.filter((f) => f !== lastItem.field);
    }
    updateProfile(updated);
    loadNext(updated);
  };

  const finishAndEvaluate = async (finalProf) => {
    setIsLoading(true);
    try {
      const evalResp = await evaluateCitizenProfile(finalProf);
      setEvaluationResults(evalResp);
      setCurrentScreen('S4');
    } catch (err) {
      console.error('Evaluation failed:', err);
      setCurrentScreen('S4');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !questionData) {
    return (
      <div className="max-w-2xl mx-auto w-full flex-1 flex flex-col items-center justify-center p-12 space-y-4">
        <div className="w-12 h-12 border-3 border-blue-700 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-semibold text-slate-700">
          {language === 'hi' ? 'अगला प्रासंगिक प्रश्न तैयार हो रहा है...' : 'Selecting next impactful question...'}
        </p>
      </div>
    );
  }

  const title = getBilingualText(questionData, 'title');
  const subtitle = getBilingualText(questionData, 'subtitle');
  const totalEst = questionData?.total_estimated || 8;
  const currentStep = questionData?.progress_index || stepNumber;
  const progressPercent = Math.min(100, Math.round(((currentStep - 1) / totalEst) * 100));

  return (
    <div className="max-w-3xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Progress & Top Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <button
              onClick={handleBack}
              className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 font-semibold py-1.5 px-3 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{t('back')}</span>
            </button>

            <span className="bg-blue-50 text-blue-900 border border-blue-200 px-3 py-1 rounded-full text-xs font-bold tracking-wide">
              {language === 'hi' ? `प्रश्न ${currentStep} / ~${totalEst}` : `Question ${currentStep} of ~${totalEst}`}
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
            <div
              className="bg-blue-600 h-full transition-all duration-300 rounded-full"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1.5 flex-1">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
                {title}
              </h2>
              {subtitle && (
                <p className="text-sm text-slate-500 leading-relaxed">
                  {subtitle}
                </p>
              )}
            </div>
            <AudioSpeaker text={`${title}। ${subtitle || ''}`} className="mt-0.5 flex-shrink-0" />
          </div>

          {/* Input Controls */}
          <div>
            {/* Options grid for choices */}
            {(questionData.type === 'single_choice' || questionData.type === 'boolean') && questionData.options && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {questionData.options.map((opt, idx) => {
                  const isSelected = selectedValue === opt.value;
                  const label = language === 'hi' ? opt.label_hi : opt.label_en;
                  return (
                    <div
                      key={idx}
                      onClick={() => handleSelectOption(opt.value)}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-center justify-between gap-3 min-h-[58px] ${
                        isSelected
                          ? 'border-blue-600 bg-blue-50/70 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60 bg-white'
                      }`}
                      role="radio"
                      aria-checked={isSelected}
                      tabIndex={0}
                    >
                      <span className={`text-sm font-semibold ${isSelected ? 'text-blue-950 font-bold' : 'text-slate-800'}`}>
                        {label}
                      </span>
                      <div
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                          isSelected ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300'
                        }`}
                      >
                        {isSelected && <Check className="w-3.5 h-3.5 stroke-3" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Numeric input */}
            {questionData.type === 'number' && (
              <div className="max-w-md">
                <div className="relative">
                  <input
                    type="number"
                    min={questionData.min_val}
                    max={questionData.max_val}
                    value={selectedValue}
                    onChange={(e) => setSelectedValue(e.target.value)}
                    placeholder={language === 'hi' ? 'मान दर्ज करें' : 'Enter amount/number'}
                    className="w-full text-xl font-bold text-slate-900 p-4 rounded-xl border-2 border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white min-h-[56px] pr-16"
                  />
                  {questionData.unit && (
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-slate-400">
                      {questionData.unit}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Free text input */}
            {questionData.type === 'text' && (
              <input
                type="text"
                value={selectedValue}
                onChange={(e) => setSelectedValue(e.target.value)}
                placeholder={language === 'hi' ? 'उत्तर लिखें' : 'Enter details'}
                className="w-full text-base font-medium text-slate-900 p-4 rounded-xl border-2 border-slate-300 focus:border-blue-600 focus:outline-hidden bg-white min-h-[56px]"
              />
            )}
          </div>
        </div>
      </div>

      {/* Footer Navigation Buttons */}
      <div className="pt-6 border-t border-slate-200 flex flex-col-reverse sm:flex-row items-center justify-between gap-3">
        <button
          onClick={handleSkip}
          className="w-full sm:w-auto px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center justify-center gap-1.5 transition-colors rounded-lg hover:bg-slate-100 min-h-[44px]"
        >
          <SkipForward className="w-4 h-4" />
          <span>{language === 'hi' ? 'यह प्रश्न छोड़ें (Skip)' : 'Skip Question'}</span>
        </button>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button
            onClick={handleNext}
            disabled={selectedValue === '' || selectedValue === null || isLoading}
            className="w-full sm:w-auto px-8 py-3 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 text-white font-semibold rounded-xl text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 min-h-[48px]"
          >
            <span>{t('next')}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
