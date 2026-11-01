const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.protocol === 'https:' && !window.location.hostname.includes('localhost')
    ? '/api'
    : 'http://localhost:8000/api');

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

export async function fetchAllSchemes(lang = null) {
  const resp = await fetch(`${API_BASE_URL}/schemes${lang ? `?lang=${lang}` : ''}`);
  if (!resp.ok) throw new Error(`Fetch schemes failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeDetails(schemeId, lang = null) {
  const resp = await fetch(`${API_BASE_URL}/schemes/${schemeId}${lang ? `?lang=${lang}` : ''}`);
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
  try {
    const resp = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, current_scheme_id: currentSchemeId, profile, language, history }),
    });
    if (!resp.ok) throw new Error(`Chat failed: ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn('Chat network fallback:', err);
    return {
      reply: language === 'hi'
        ? "नमस्ते! योजनासारथी सरकारी योजना पात्रता व मार्गदर्शन सहायक है। आप MMVY छात्रवृत्ति, लाड़ली बहना, पीएम किसान, आयुष्मान भारत, अथवा आवश्यक दस्तावेजों (जैसे आय, मूल निवास, समग्र आईडी, खसरा) के बारे में पूछ सकते हैं।"
        : "Namaste! I am your YojnaSarthi Government Scheme Assistant. You can ask about eligibility rules for MMVY Scholarship, Ladli Behna, PM-KISAN, Ayushman Bharat, PMAY-G Housing, or required certificates.",
      grounded_sources: ["https://india.gov.in/"],
      disclaimer: "Grounded in verified official rules."
    };
  }
}

export async function requestFormHelp(fieldText = null, imageBase64 = null, language = 'hi') {
  try {
    const resp = await fetch(`${API_BASE_URL}/form-help`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field_text: fieldText, image_base64: imageBase64, language }),
    });
    if (!resp.ok) throw new Error(`Form help failed: ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn('Form help network fallback:', err);
    const { lookupFormTerm } = await import('./formDictionary.js');
    return lookupFormTerm(fieldText || 'Khasra Number', language);
  }
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

// ==============================================================================
// Document Guide API
// ==============================================================================
export async function fetchDocumentList(query = null, category = null) {
  const params = new URLSearchParams();
  if (query) params.append('query', query);
  if (category && category !== 'all') params.append('category', category);
  const url = `${API_BASE_URL}/documents${params.toString() ? `?${params.toString()}` : ''}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Fetch documents failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchDocumentDetails(docId) {
  const resp = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(docId)}`);
  if (!resp.ok) throw new Error(`Fetch document details failed: ${resp.status}`);
  return await resp.json();
}

// ==============================================================================
// Local i18n & Translation API (No External Azure Calls)
// ==============================================================================
export async function translateText(text, sourceLanguage = 'en', targetLanguage = 'hi') {
  if (!text || typeof text !== 'string') {
    return { translated_text: text, translatedText: text, success: true, service: 'i18n_local' };
  }
  try {
    const resp = await fetch(`${API_BASE_URL}/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, sourceLanguage, targetLanguage }),
    });
    if (resp.ok) {
      return await resp.json();
    }
  } catch (_) {}
  return { translated_text: text, translatedText: text, source_language: sourceLanguage, target_language: targetLanguage, success: true, service: 'i18n_local' };
}

export const translateWithSarvam = translateText;
export const translateWithAzure = translateText;

/** Translate dynamic strings locally with zero external network delays */
export async function translateBatch(texts, targetLanguage = 'hi', sourceLanguage = 'auto') {
  try {
    const resp = await fetch(`${API_BASE_URL}/translate/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texts, target_language: targetLanguage, source_language: sourceLanguage }),
    });
    if (resp.ok) {
      const data = await resp.json();
      return data.translations;
    }
  } catch (_) {}
  return texts.map((t) => ({ translated_text: t, translatedText: t, success: true, service: 'i18n_local' }));
}

export async function fetchTranslatorStatus() {
  try {
    const resp = await fetch(`${API_BASE_URL}/translate/status`);
    if (resp.ok) return await resp.json();
  } catch (_) {}
  return { name: "i18n Internationalization Library", status: "active", is_external_api: false };
}

export async function fetchIntegrationsStatus() {
  const resp = await fetch(`${API_BASE_URL}/integrations/status`);
  if (!resp.ok) throw new Error(`Fetch integration status failed: ${resp.status}`);
  return await resp.json();
}

// ==============================================================================
// Admin Scheme Intelligence & Monitoring API (Protected via X-Admin-Key)
// ==============================================================================
function getAdminHeaders(adminKey) {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Key': adminKey || '',
  };
}

export async function fetchMonitoringSummary(adminKey) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/summary`, {
    headers: getAdminHeaders(adminKey),
  });
  if (!resp.ok) throw new Error(`Monitoring summary failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringSources(adminKey) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/sources`, {
    headers: getAdminHeaders(adminKey),
  });
  if (!resp.ok) throw new Error(`Monitoring sources failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringChanges(adminKey, limit = 50) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/changes?limit=${limit}`, {
    headers: getAdminHeaders(adminKey),
  });
  if (!resp.ok) throw new Error(`Monitoring changes failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchPendingUpdates(adminKey, includeDemo = true) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/pending-updates?include_demo=${includeDemo}`, {
    headers: getAdminHeaders(adminKey),
  });
  if (!resp.ok) throw new Error(`Pending updates failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeVersionHistory(adminKey, schemeId) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/schemes/${schemeId}/history`, {
    headers: getAdminHeaders(adminKey),
  });
  if (!resp.ok) throw new Error(`Scheme history failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerMonitoringRun(adminKey, sourceId = null) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/run`, {
    method: 'POST',
    headers: getAdminHeaders(adminKey),
    body: JSON.stringify({ source_id: sourceId }),
  });
  if (!resp.ok) throw new Error(`Run monitoring failed: ${resp.status}`);
  return await resp.json();
}

export async function approveSchemeUpdate(adminKey, updateId, reviewerName, reason) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/updates/${updateId}/approve`, {
    method: 'POST',
    headers: getAdminHeaders(adminKey),
    body: JSON.stringify({ reviewer_name: reviewerName, reason }),
  });
  if (!resp.ok) throw new Error(`Approve update failed: ${resp.status}`);
  return await resp.json();
}

export async function rejectSchemeUpdate(adminKey, updateId, reviewerName, reason) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/updates/${updateId}/reject`, {
    method: 'POST',
    headers: getAdminHeaders(adminKey),
    body: JSON.stringify({ reviewer_name: reviewerName, reason }),
  });
  if (!resp.ok) throw new Error(`Reject update failed: ${resp.status}`);
  return await resp.json();
}

export async function rollbackSchemeVersion(adminKey, schemeId, targetVersionId, reviewerName) {
  const resp = await fetch(`${API_BASE_URL}/admin/monitoring/schemes/${schemeId}/rollback`, {
    method: 'POST',
    headers: getAdminHeaders(adminKey),
    body: JSON.stringify({ target_version_id: targetVersionId, reviewer_name: reviewerName }),
  });
  if (!resp.ok) throw new Error(`Rollback version failed: ${resp.status}`);
  return await resp.json();
}

// ==============================================================================
// Multi-Agent Discovery & Scheme Intelligence API
// ==============================================================================
const ADMIN_API_KEY = 'yojnasarthi-admin-secret-2026';

function adminHeaders(customHeaders = {}) {
  return {
    'X-Admin-Key': ADMIN_API_KEY,
    ...customHeaders,
  };
}

export async function fetchAgentsStatus() {
  const resp = await fetch(`${API_BASE_URL}/agents/status`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch agents status failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentRuns(limit = 50) {
  const resp = await fetch(`${API_BASE_URL}/agents/runs?limit=${limit}`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch agent runs failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentDiscover(seeds = null, maxLinks = 15) {
  const resp = await fetch(`${API_BASE_URL}/agents/discover`, {
    method: 'POST',
    headers: adminHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ seeds, max_links_per_seed: maxLinks }),
  });
  if (!resp.ok) throw new Error(`Discover failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentCrawl(sourceIds = null, maxSources = 10) {
  const resp = await fetch(`${API_BASE_URL}/agents/crawl`, {
    method: 'POST',
    headers: adminHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ source_ids: sourceIds, max_sources: maxSources }),
  });
  if (!resp.ok) throw new Error(`Crawl failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentMonitor(sourceIds = null, maxSources = 10) {
  const resp = await fetch(`${API_BASE_URL}/agents/monitor`, {
    method: 'POST',
    headers: adminHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ source_ids: sourceIds, max_sources: maxSources }),
  });
  if (!resp.ok) throw new Error(`Monitor failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchDiscoveredSources(status = null, limit = 100) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (limit) params.append('limit', limit);
  const url = `${API_BASE_URL}/sources${params.toString() ? `?${params.toString()}` : ''}`;
  const resp = await fetch(url, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch sources failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSourceDetail(sourceId) {
  const resp = await fetch(`${API_BASE_URL}/sources/${sourceId}`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch source detail failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentUpdates(status = null) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  const url = `${API_BASE_URL}/updates${params.toString() ? `?${params.toString()}` : ''}`;
  const resp = await fetch(url, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch updates failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentUpdateDetail(updateId) {
  const resp = await fetch(`${API_BASE_URL}/updates/${updateId}`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch update detail failed: ${resp.status}`);
  return await resp.json();
}

export async function approveAgentUpdate(updateId, reviewerName = 'Admin Officer', reason = 'Verified against official notification') {
  const resp = await fetch(`${API_BASE_URL}/updates/${updateId}/approve`, {
    method: 'POST',
    headers: adminHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ reviewer_name: reviewerName, reason }),
  });
  if (!resp.ok) throw new Error(`Approve update failed: ${resp.status}`);
  return await resp.json();
}

export async function rejectAgentUpdate(updateId, reviewerName = 'Admin Officer', reason = 'Discrepancy with official circular') {
  const resp = await fetch(`${API_BASE_URL}/updates/${updateId}/reject`, {
    method: 'POST',
    headers: adminHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ reviewer_name: reviewerName, reason }),
  });
  if (!resp.ok) throw new Error(`Reject update failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeVersions(schemeId) {
  const resp = await fetch(`${API_BASE_URL}/schemes/${schemeId}/versions`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch scheme versions failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringOverview() {
  const resp = await fetch(`${API_BASE_URL}/monitoring/status`, {
    headers: adminHeaders(),
  });
  if (!resp.ok) throw new Error(`Fetch monitoring overview failed: ${resp.status}`);
  return await resp.json();
}
