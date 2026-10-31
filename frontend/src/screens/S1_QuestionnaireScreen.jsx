import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useSession } from '../context/SessionContext';
import { fetchNextQuestion, evaluateCitizenProfile } from '../services/api';
import { ArrowLeft, ArrowRight, SkipForward, Check, HelpCircle, Info, Lightbulb, Sparkles } from 'lucide-react';
import AudioSpeaker from '../components/AudioSpeaker';

export default function S1_QuestionnaireScreen() {
  const { language, t, getBilingualText, lt } = useLanguage();
  const { profile, updateProfile, setCurrentScreen, setEvaluationResults } = useSession();

  // Questionnaire history: stack of questions visited [{ field, questionData }]
  const [questionStack, setQuestionStack] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedValue, setSelectedValue] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showExplanation, setShowExplanation] = useState(true);

  // Initial load
  useEffect(() => {
    loadFirstQuestion();
  }, []);

  const loadFirstQuestion = async () => {
    setIsLoading(true);
    try {
      const resp = await fetchNextQuestion(profile);
      if (!resp.has_more || !resp.question) {
        finishAndEvaluate(profile);
        return;
      }
      setQuestionStack([{ field: resp.question.field, questionData: resp.question }]);
      setCurrentIndex(0);
      const existingVal = profile[resp.question.field];
      setSelectedValue(existingVal !== undefined && existingVal !== null ? existingVal : '');
    } catch (err) {
      console.error('Failed to load initial question:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const currentItem = questionStack[currentIndex];
  const questionData = currentItem?.questionData;

  const handleSelectOption = (val) => {
    setSelectedValue(val);
  };

  const handleNext = async () => {
    if (!questionData) return;
    const fieldKey = questionData.field;
    let finalVal = selectedValue;

    if (questionData.type === 'number') {
      finalVal = selectedValue !== '' ? parseFloat(selectedValue) : null;
    }

    const prevValInProfile = profile[fieldKey];
    const isAnswerChanged = prevValInProfile !== finalVal;

    const cleanSkipped = (profile.skipped_fields || []).filter((f) => f !== fieldKey);
    const updatedProfile = {
      ...profile,
      [fieldKey]: finalVal,
      skipped_fields: cleanSkipped,
      confirmed_fields: Array.from(new Set([...(profile.confirmed_fields || []), fieldKey]))
    };
    updateProfile(updatedProfile);

    // If we are revisiting an earlier question in the stack:
    if (currentIndex < questionStack.length - 1) {
      if (!isAnswerChanged) {
        const nextIdx = currentIndex + 1;
        const nextItem = questionStack[nextIdx];
        setCurrentIndex(nextIdx);
        const nextExisting = updatedProfile[nextItem.field];
        setSelectedValue(nextExisting !== undefined && nextExisting !== null ? nextExisting : '');
        return;
      }
      // Answer changed: truncate forward stack to re-evaluate downstream
      setQuestionStack((prev) => prev.slice(0, currentIndex + 1));
    }

    // Otherwise, fetch next dynamic question from the rule engine
    setIsLoading(true);
    try {
      const resp = await fetchNextQuestion(updatedProfile);
      if (!resp.has_more || !resp.question) {
        await finishAndEvaluate(updatedProfile);
        return;
      }

      setQuestionStack((prev) => [...prev, { field: resp.question.field, questionData: resp.question }]);
      setCurrentIndex((prev) => prev + 1);
      const existingInNext = updatedProfile[resp.question.field];
      setSelectedValue(existingInNext !== undefined && existingInNext !== null ? existingInNext : '');
    } catch (err) {
      console.error('Failed to load next question:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkip = async () => {
    if (!questionData) return;
    const fieldKey = questionData.field;

    const prevSkipped = profile.skipped_fields || [];
    const updatedSkipped = Array.from(new Set([...prevSkipped, fieldKey]));
    const cleanConfirmed = (profile.confirmed_fields || []).filter((f) => f !== fieldKey);

    // Mark as intentionally skipped in profile so answer is preserved as unknown
    const updatedProfile = {
      ...profile,
      [fieldKey]: null,
      skipped_fields: updatedSkipped,
      confirmed_fields: cleanConfirmed
    };
    updateProfile(updatedProfile);

    if (currentIndex < questionStack.length - 1) {
      const nextIdx = currentIndex + 1;
      setCurrentIndex(nextIdx);
      const nextItem = questionStack[nextIdx];
      const nextExisting = updatedProfile[nextItem.field];
      setSelectedValue(nextExisting !== undefined && nextExisting !== null ? nextExisting : '');
      return;
    }

    setIsLoading(true);
    try {
      const resp = await fetchNextQuestion(updatedProfile);
      if (!resp.has_more || !resp.question) {
        await finishAndEvaluate(updatedProfile);
        return;
      }
      setQuestionStack((prev) => [...prev, { field: resp.question.field, questionData: resp.question }]);
      setCurrentIndex((prev) => prev + 1);
      const existingInNext = updatedProfile[resp.question.field];
      setSelectedValue(existingInNext !== undefined && existingInNext !== null ? existingInNext : '');
    } catch (err) {
      console.error('Failed to load after skip:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (currentIndex === 0) {
      setCurrentScreen('S0');
      return;
    }

    const prevIndex = currentIndex - 1;
    setCurrentIndex(prevIndex);
    const prevItem = questionStack[prevIndex];
    const prevVal = profile[prevItem.field];
    setSelectedValue(prevVal !== undefined && prevVal !== null ? prevVal : '');
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
        <div className="w-12 h-12 border-3 border-teal-700 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-semibold text-slate-700">
          {t('selecting_question')}
        </p>
      </div>
    );
  }

  const title = getBilingualText(questionData, 'title');
  const subtitle = getBilingualText(questionData, 'subtitle');
  const explanation = getBilingualText(questionData, 'explanation');
  const examples = getBilingualText(questionData, 'examples');
  
  const totalEst = questionData?.total_estimated || 8;
  const currentStep = currentIndex + 1;
  const progressPercent = Math.min(100, Math.round((currentStep / totalEst) * 100));

  const audioSpeechText = `${title}। ${subtitle || ''} ${explanation ? 'स्पष्टीकरण: ' + explanation : ''}`;

  return (
    <div className="max-w-3xl mx-auto w-full space-y-6 animate-fade-in flex-1 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Top Navigation & Progress Bar */}
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <button
              onClick={handleBack}
              className="inline-flex items-center gap-1.5 text-slate-700 hover:text-slate-900 font-semibold py-1.5 px-3 rounded-lg hover:bg-slate-200/60 transition-colors touch-target"
              aria-label={t('back')}
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{t('back')}</span>
            </button>

            <span className="bg-teal-50 text-teal-900 border border-teal-200 px-3.5 py-1 rounded-full text-xs font-bold tracking-wide">
              {lt(`Question ${currentStep} of ~${totalEst}`, `प्रश्न ${currentStep} / ~${totalEst}`)}
            </span>
          </div>

          {/* Attractive Progress Bar */}
          <div className="w-full bg-slate-200/80 h-2.5 rounded-full overflow-hidden shadow-inner">
            <div
              className="bg-gradient-to-r from-teal-600 to-blue-700 h-full transition-all duration-300 rounded-full"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white border border-slate-200/90 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1.5 flex-1">
              <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight leading-snug">
                {title}
              </h2>
              {subtitle && (
                <p className="text-sm text-slate-600 leading-relaxed font-medium">
                  {subtitle}
                </p>
              )}
              {profile.skipped_fields?.includes(questionData?.field) && (
                <div className="pt-1">
                  <span className="inline-block px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold">
                    {lt('⚠️ Previously skipped (You can answer or skip again)', '⚠️ यह प्रश्न पहले छोड़ा गया था (आप अब विकल्प चुन सकते हैं)')}
                  </span>
                </div>
              )}
            </div>
            <AudioSpeaker text={audioSpeechText} className="mt-0.5 flex-shrink-0" />
          </div>

          {/* Simple Explanation & Examples Banner (Issue #9) */}
          {explanation && (
            <div className="bg-slate-50 border border-teal-100/80 rounded-xl p-4 space-y-2 text-xs sm:text-sm">
              <div className="flex items-center gap-2 text-teal-900 font-bold">
                <Lightbulb className="w-4 h-4 text-teal-700 flex-shrink-0" />
                <span>{t('why_we_ask')}</span>
              </div>
              <p className="text-slate-700 leading-relaxed">
                {explanation}
              </p>
              {examples && (
                <p className="text-slate-500 text-xs pt-1 border-t border-slate-200/60">
                  <strong className="text-slate-700">{t('examples')}:</strong> {examples}
                </p>
              )}
            </div>
          )}

          {/* Input Controls */}
          <div>
            {/* Options grid for choices */}
            {(questionData?.type === 'single_choice' || questionData?.type === 'boolean') && questionData?.options && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {questionData.options.map((opt, idx) => {
                  const isSelected = selectedValue === opt.value;
<<<<<<< HEAD
                  const label = language === 'hi' ? opt.label_hi : (language === 'bn' ? (opt.label_bn || opt.label_hi || opt.label_en) : opt.label_en);
                  const desc = language === 'hi' ? opt.description_hi : (language === 'bn' ? (opt.description_bn || opt.description_hi || opt.description_en) : opt.description_en);
=======
                  const label = lt(opt.label_en, opt.label_hi);
                  const desc = lt(opt.description_en, opt.description_hi);
>>>>>>> shreya/main

                  return (
                    <div
                      key={idx}
                      onClick={() => handleSelectOption(opt.value)}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col justify-between gap-2 min-h-[64px] ${
                        isSelected
                          ? 'border-teal-700 bg-teal-50/70 shadow-xs'
                          : 'border-slate-200 hover:border-teal-300 hover:bg-slate-50/70 bg-white'
                      }`}
                      role="radio"
                      aria-checked={isSelected}
                      tabIndex={0}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <span className={`text-sm ${isSelected ? 'text-teal-950 font-bold' : 'text-slate-900 font-semibold'}`}>
                          {label}
                        </span>
                        <div
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors mt-0.5 ${
                            isSelected ? 'border-teal-700 bg-teal-700 text-white' : 'border-slate-300'
                          }`}
                        >
                          {isSelected && <Check className="w-3 h-3 stroke-3" />}
                        </div>
                      </div>

                      {desc && (
                        <p className={`text-xs leading-normal ${isSelected ? 'text-teal-800' : 'text-slate-500'}`}>
                          {desc}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Numeric input */}
            {questionData?.type === 'number' && (
              <div className="max-w-md space-y-2">
                <div className="relative">
                  <input
                    type="number"
                    min={questionData.min_val}
                    max={questionData.max_val}
                    value={selectedValue}
                    onChange={(e) => setSelectedValue(e.target.value)}
                    placeholder={lt('Enter amount/number', 'मान दर्ज करें')}
                    className="w-full text-xl font-bold text-slate-900 p-4 rounded-xl border-2 border-slate-300 focus:border-teal-600 focus:outline-hidden bg-white min-h-[56px] pr-16"
                  />
                  {questionData.unit && (
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-slate-400">
                      {questionData.unit}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500">
                  {lt('Enter numerical digits only (e.g. 29, 65000)', 'केवल संख्या दर्ज करें (जैसे 29, 65000)')}
                </p>
              </div>
            )}

            {/* Free text input */}
            {questionData?.type === 'text' && (
              <input
                type="text"
                value={selectedValue}
                onChange={(e) => setSelectedValue(e.target.value)}
                placeholder={lt('Enter details', 'उत्तर लिखें')}
                className="w-full text-base font-medium text-slate-900 p-4 rounded-xl border-2 border-slate-300 focus:border-teal-600 focus:outline-hidden bg-white min-h-[56px]"
              />
            )}
          </div>
        </div>
      </div>

      {/* Footer Navigation Buttons */}
      <div className="pt-6 border-t border-slate-200 flex flex-col-reverse sm:flex-row items-center justify-between gap-3">
        <button
          onClick={handleSkip}
          className="w-full sm:w-auto px-4 py-2.5 text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5 transition-colors rounded-lg hover:bg-slate-100 min-h-[44px]"
        >
          <SkipForward className="w-4 h-4" />
          <span>{t('skip')}</span>
        </button>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button
            onClick={handleNext}
            disabled={selectedValue === '' || selectedValue === null || selectedValue === undefined}
            className="w-full sm:w-auto px-6 py-3 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl text-xs sm:text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 min-h-[48px]"
          >
            <span>{t('next')}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
