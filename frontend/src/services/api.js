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
// Offline Translation API (local engine on our own backend - no third-party API)
// ==============================================================================
export async function translateText(text, sourceLanguage = 'auto', targetLanguage = 'hi') {
  const resp = await fetch(`${API_BASE_URL}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, sourceLanguage, targetLanguage }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || `Translation failed: ${resp.status}`);
  }
  return await resp.json();
}

/** Translate many dynamic strings in one round trip. Resolves to an array aligned with `texts`. */
export async function translateBatch(texts, targetLanguage = 'hi', sourceLanguage = 'auto') {
  const resp = await fetch(`${API_BASE_URL}/translate/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texts, target_language: targetLanguage, source_language: sourceLanguage }),
  });
  if (!resp.ok) throw new Error(`Batch translation failed: ${resp.status}`);
  const data = await resp.json();
  return data.translations;
}

export async function fetchTranslatorStatus() {
  const resp = await fetch(`${API_BASE_URL}/translate/status`);
  if (!resp.ok) throw new Error(`Fetch translator status failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchIntegrationsStatus() {
  const resp = await fetch(`${API_BASE_URL}/integrations/status`);
  if (!resp.ok) throw new Error(`Fetch integration status failed: ${resp.status}`);
  return await resp.json();
}



// ==============================================================================
// Admin APIs use signed HttpOnly sessions and CSRF-protected mutations.
// ==============================================================================
let adminCsrfToken = '';
function getCsrfToken() { return adminCsrfToken; }

function adminRequest(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const method = (options.method || 'GET').toUpperCase();
  if (method !== 'GET' && method !== 'HEAD') headers.set('X-CSRF-Token', getCsrfToken());
  return fetch(url, { ...options, headers, credentials: 'include' }).then((resp) => {
    if (resp.status === 401) {
      adminCsrfToken = '';
      window.dispatchEvent(new Event('admin-session-expired'));
    }
    return resp;
  });
}

export async function fetchAdminSession() {
  const resp = await fetch(`${API_BASE_URL}/admin/auth/session`, { credentials: 'include' });
  if (!resp.ok) throw new Error(`Admin session check failed: ${resp.status}`);
  const data = await resp.json();
  adminCsrfToken = data.csrf_token || '';
  return data;
}

export async function loginAdmin(username, password) {
  const resp = await fetch(`${API_BASE_URL}/admin/auth/login`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    throw new Error(data.detail || `Admin login failed: ${resp.status}`);
  }
  const data = await resp.json();
  adminCsrfToken = data.csrf_token || '';
  return data;
}

export async function logoutAdmin() {
  const resp = await adminRequest(`${API_BASE_URL}/admin/auth/logout`, { method: 'POST' });
  if (!resp.ok) throw new Error(`Admin logout failed: ${resp.status}`);
  const data = await resp.json();
  adminCsrfToken = '';
  return data;
}

function getAdminHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCsrfToken(),
  };
}

export async function fetchMonitoringSummary() {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/summary`, {
    headers: getAdminHeaders(),
  });
  if (!resp.ok) throw new Error(`Monitoring summary failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringSources() {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/sources`, {
    headers: getAdminHeaders(),
  });
  if (!resp.ok) throw new Error(`Monitoring sources failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringChanges(limit = 50) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/changes?limit=${limit}`, {
    headers: getAdminHeaders(),
  });
  if (!resp.ok) throw new Error(`Monitoring changes failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchPendingUpdates(includeDemo = false) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/pending-updates?include_demo=${includeDemo}`, {
    headers: getAdminHeaders(),
  });
  if (!resp.ok) throw new Error(`Pending updates failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeVersionHistory(schemeId) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/schemes/${schemeId}/history`, {
    headers: getAdminHeaders(),
  });
  if (!resp.ok) throw new Error(`Scheme history failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerMonitoringRun(sourceId = null) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/run`, {
    method: 'POST',
    headers: getAdminHeaders(),
    body: JSON.stringify({ source_id: sourceId }),
  });
  if (!resp.ok) throw new Error(`Run monitoring failed: ${resp.status}`);
  return await resp.json();
}

export async function approveSchemeUpdate(updateId, reason) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/updates/${updateId}/approve`, {
    method: 'POST',
    headers: getAdminHeaders(),
    body: JSON.stringify({ reason }),
  });
  if (!resp.ok) throw new Error(`Approve update failed: ${resp.status}`);
  return await resp.json();
}

export async function rejectSchemeUpdate(updateId, reason) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/updates/${updateId}/reject`, {
    method: 'POST',
    headers: getAdminHeaders(),
    body: JSON.stringify({ reason }),
  });
  if (!resp.ok) throw new Error(`Reject update failed: ${resp.status}`);
  return await resp.json();
}

export async function rollbackSchemeVersion(schemeId, targetVersionId) {
  const resp = await adminRequest(`${API_BASE_URL}/admin/monitoring/schemes/${schemeId}/rollback`, {
    method: 'POST',
    headers: getAdminHeaders(),
    body: JSON.stringify({ target_version_id: targetVersionId }),
  });
  if (!resp.ok) throw new Error(`Rollback version failed: ${resp.status}`);
  return await resp.json();
}

// ==============================================================================
// Multi-Agent Discovery & Scheme Intelligence API
// ==============================================================================
export async function fetchAgentsStatus() {
  const resp = await adminRequest(`${API_BASE_URL}/agents/status`);
  if (!resp.ok) throw new Error(`Fetch agents status failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentRuns(limit = 50) {
  const resp = await adminRequest(`${API_BASE_URL}/agents/runs?limit=${limit}`);
  if (!resp.ok) throw new Error(`Fetch agent runs failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentDiscover(seeds = null, maxLinks = 15) {
  const resp = await adminRequest(`${API_BASE_URL}/agents/discover`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seeds, max_links_per_seed: maxLinks }),
  });
  if (!resp.ok) throw new Error(`Discover failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentCrawl(sourceIds = null, maxSources = 10) {
  const resp = await adminRequest(`${API_BASE_URL}/agents/crawl`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_ids: sourceIds, max_sources: maxSources }),
  });
  if (!resp.ok) throw new Error(`Crawl failed: ${resp.status}`);
  return await resp.json();
}

export async function triggerAgentMonitor(sourceIds = null, maxSources = 10) {
  const resp = await adminRequest(`${API_BASE_URL}/agents/monitor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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
  const resp = await adminRequest(url);
  if (!resp.ok) throw new Error(`Fetch sources failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSourceDetail(sourceId) {
  const resp = await fetch(`${API_BASE_URL}/sources/${sourceId}`);
  if (!resp.ok) throw new Error(`Fetch source detail failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentUpdates(status = null) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  const url = `${API_BASE_URL}/updates${params.toString() ? `?${params.toString()}` : ''}`;
  const resp = await adminRequest(url);
  if (!resp.ok) throw new Error(`Fetch updates failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchAgentUpdateDetail(updateId) {
  const resp = await adminRequest(`${API_BASE_URL}/updates/${updateId}`);
  if (!resp.ok) throw new Error(`Fetch update detail failed: ${resp.status}`);
  return await resp.json();
}

export async function approveAgentUpdate(updateId, reason = 'Verified against official notification') {
  const resp = await adminRequest(`${API_BASE_URL}/updates/${updateId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!resp.ok) throw new Error(`Approve update failed: ${resp.status}`);
  return await resp.json();
}

export async function rejectAgentUpdate(updateId, reason = 'Discrepancy with official circular') {
  const resp = await adminRequest(`${API_BASE_URL}/updates/${updateId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!resp.ok) throw new Error(`Reject update failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchSchemeVersions(schemeId) {
  const resp = await adminRequest(`${API_BASE_URL}/schemes/${schemeId}/versions`);
  if (!resp.ok) throw new Error(`Fetch scheme versions failed: ${resp.status}`);
  return await resp.json();
}

export async function fetchMonitoringOverview() {
  const resp = await adminRequest(`${API_BASE_URL}/monitoring/status`);
  if (!resp.ok) throw new Error(`Fetch monitoring overview failed: ${resp.status}`);
  return await resp.json();
}
