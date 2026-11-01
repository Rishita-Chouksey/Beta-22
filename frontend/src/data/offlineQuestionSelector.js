import questionsData from './questions.json';

const FIELD_EASINESS_RANK = {
  state: 1,
  residence_type: 2,
  gender: 3,
  age: 4,
  marital_status: 5,
  occupation: 6,
  category: 7,
  annual_income: 8,
  bpl_card_holder: 9,
  has_pucca_house: 10,
  landholding_hectares: 11,
  student_class12_marks_percent: 12,
  enrolled_higher_education: 13,
  disability_status: 14,
};

const EXCLUDED_FIELDS = new Set([
  'holds_constitutional_post',
  'is_institutional_landholder',
  'confirmed_fields',
  'skipped_fields',
  'income_band',
  'disability_percent',
]);

export function getNextQuestionOffline(profile = {}) {
  const answeredFields = new Set(
    Object.keys(profile || {}).filter(
      (k) => profile[k] !== undefined && profile[k] !== null && profile[k] !== '' && !EXCLUDED_FIELDS.has(k)
    )
  );
  const skippedFields = new Set(profile?.skipped_fields || []);

  const allQuestions = questionsData?.questions || [];

  // Filter out already answered or explicitly skipped questions
  let candidateQuestions = allQuestions.filter((q) => {
    if (EXCLUDED_FIELDS.has(q.field)) return false;
    if (answeredFields.has(q.field)) return false;
    if (skippedFields.has(q.field)) return false;

    // Smart demographic pruning:
    // If citizen is not a farmer, skip landholding question
    if (q.field === 'landholding_hectares' && profile.occupation && profile.occupation !== 'farmer') {
      return false;
    }
    // If citizen is older than 30, skip class 12 marks and higher education questions
    if ((q.field === 'student_class12_marks_percent' || q.field === 'enrolled_higher_education') && profile.age && Number(profile.age) > 28) {
      return false;
    }

    return true;
  });

  // Sort candidates by easiness rank
  candidateQuestions.sort((a, b) => {
    const rankA = FIELD_EASINESS_RANK[a.field] || 99;
    const rankB = FIELD_EASINESS_RANK[b.field] || 99;
    return rankA - rankB;
  });

  // Stop questionnaire if no more questions, or if we have collected enough high-impact answers (>= 8 answered)
  const answeredCount = answeredFields.size;
  if (candidateQuestions.length === 0 || (answeredCount >= 8 && candidateQuestions.length <= 2)) {
    return {
      has_more: false,
      question: null,
      resolved_message_en: 'Sufficient profile information gathered to evaluate government schemes.',
      resolved_message_hi: 'योजना पात्रता मूल्यांकन के लिए पर्याप्त जानकारी प्राप्त हो चुकी है।',
    };
  }

  const nextQ = candidateQuestions[0];
  const totalEstimated = Math.min(8, Math.max(answeredCount + candidateQuestions.length, answeredCount + 1));

  return {
    has_more: true,
    question: {
      ...nextQ,
      current_step: answeredCount + 1,
      progress_index: answeredCount + 1,
      total_estimated: totalEstimated,
    },
  };
}
