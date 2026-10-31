const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function fetchNextQuestion(profile) {
  const resp = await fetch(`${API_BASE_URL}/next-question`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile }),
  });
  if (!resp.ok) throw new Error(`Next question failed: ${resp.status}`);
  return await resp.json();
}

export async function evaluateCitizenProfile(profile) {
  const resp = await fetch(`${API_BASE_URL}/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile }),
  });
  if (!resp.ok) throw new Error(`Evaluation failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAllSchemes() {
  const resp = await fetch(`${API_BASE_URL}/schemes`);
  if (!resp.ok) throw new Error(`Fetch schemes failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeDetails(schemeId) {
  const resp = await fetch(`${API_BASE_URL}/schemes/${schemeId}`);
  if (!resp.ok) throw new Error(`Fetch scheme details failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchDocumentChecklist(schemeIds) {
  const resp = await fetch(`${API_BASE_URL}/checklist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scheme_ids: schemeIds }),
  });
  if (!resp.ok) throw new Error(`Checklist failed: ${resp.status}`);
  return await resp.json();
}

export async function parseFreeTextDescription(text, language = 'hi') {
  const resp = await fetch(`${API_BASE_URL}/parse-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  });
  if (!resp.ok) throw new Error(`Parse text failed: ${resp.status}`);
  return await resp.json();
}

export async function sendChatMessage(message, currentSchemeId = null, profile = null, language = 'hi', history = null) {
  const resp = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, current_scheme_id: currentSchemeId, profile, language, history }),
  });
  if (!resp.ok) throw new Error(`Chat failed: ${resp.status}`);
  return await resp.json();
}

export async function requestFormHelp(fieldText = null, imageBase64 = null, language = 'hi') {
  const resp = await fetch(`${API_BASE_URL}/form-help`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field_text: fieldText, image_base64: imageBase64, language }),
  });
  if (!resp.ok) throw new Error(`Form help failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchRulesStatus() {
  const resp = await fetch(`${API_BASE_URL}/rules-status`);
  if (!resp.ok) throw new Error(`Rules status failed: ${resp.status}`);
  return await resp.json();
}

export async function submitFeedback(schemeId = null, rating = 5, isHelpful = true, comment = '', language = 'hi') {
  const resp = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scheme_id: schemeId, rating, is_helpful: isHelpful, comment, language }),
  });
  if (!resp.ok) throw new Error(`Feedback failed: ${resp.status}`);
  return await resp.json();
}
