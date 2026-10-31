path = "frontend/src/services/api.js"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """// ==============================================================================
// Microsoft Azure AI Translator API
// ==============================================================================
export async function translateWithAzure(text, sourceLanguage = 'en', targetLanguage = 'hi') {
  const resp = await fetch(${API_BASE_URL}/translate, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, sourceLanguage, targetLanguage }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || Azure translation failed: );
  }
  return await resp.json();
}

export async function fetchTranslatorStatus() {
  const resp = await fetch(${API_BASE_URL}/translate/status);
  if (!resp.ok) throw new Error(Fetch translator status failed: );
  return await resp.json();
}"""

replacement = """// ==============================================================================
// Microsoft Azure AI Translator API
// ==============================================================================
export async function translateWithAzure(text, sourceLanguage = 'en', targetLanguage = 'hi') {
  const resp = await fetch(`${API_BASE_URL}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, sourceLanguage, targetLanguage }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || `Azure translation failed: ${resp.status}`);
  }
  return await resp.json();
}

export async function fetchTranslatorStatus() {
  const resp = await fetch(`${API_BASE_URL}/translate/status`);
  if (!resp.ok) throw new Error(`Fetch translator status failed: ${resp.status}`);
  return await resp.json();
}"""

assert target in text, "Target not found in api.js!"
text = text.replace(target, replacement)
with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Successfully replaced with backticks!")
