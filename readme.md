# 🏛️ YojnaSarthi (योजनासारथी)
### AI-Powered Government Scheme Eligibility Assistant for Indian Citizens

> **Core Product Principle**:  
> *The AI understands the citizen. The rule engine decides eligibility. The application helps the citizen take the next step.*

---

## 🌟 Overview

**YojnaSarthi** is a mobile-first, privacy-respecting, bilingual (Hindi & English) AI-powered assistant designed for Indian citizens. It enables anyone—regardless of literacy level or technical background—to easily discover government welfare schemes, understand exact eligibility criteria with deterministic proof, generate a personalized de-duplicated document checklist, and demystify complex government application forms.

### Key Pillars
1. **Deterministic Rule Engine**: Eligibility is computed by an audited Python rules engine (`eq`, `ne`, `in`, `not_in`, `lte`, `gte`, `between`). AI **never** makes unauthorized eligibility claims.
2. **Intelligent Dynamic Question Selection**: Backend TRD algorithm calculates remaining undecided schemes, selects the single most impactful question, breaks ties using cognitive ease, and guarantees reaching a decision in 8 questions or fewer.
3. **Privacy First (Zero Persistence)**:
   - No login or registration required.
   - Answers kept strictly in-memory during the browser tab session.
   - No `localStorage` or `sessionStorage` for personal profile answers.
   - Zero personal information (PII) logged on backend servers.
   - Idle alert at 9 minutes with automatic memory wipe at 10 minutes.
   - Closing or refreshing the tab wipes all data.
   - A persistent **"Clear & Exit"** button on every single screen.
4. **Bilingual & Voice-First**: Hindi and English interface with Speech-to-Text (mic input) and Text-to-Speech (read-aloud), with graceful browser Web Speech API fallback when network voice services are offline.
5. **Personalised Document Checklist**: Consolidated list across all qualified schemes, complete with where to apply, online links, physical offices, readiness tracking, and a **one-click Printable PDF view**.
6. **Form Field Explainer**: Simplifies complex terms like *NPCI / DBT Seeding, Khasra Number, Samagra ID, Domicile* with real examples and transparent AI assistance labeling.

---

## 🏛️ State-Scope Resolution (Central, MP & Maharashtra)
To cleanly address the scope context between central and state schemes:
- **Central Schemes** (`"applicable_states": ["ALL"]`) apply across all of India:
  - **PM Kisan Samman Nidhi (PM-KISAN)** — Agriculture income support
  - **Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)** — Rural housing assistance
  - **Ayushman Bharat PM-JAY** — ₹5 Lakh cashless health cover
  - **Indira Gandhi National Widow Pension Scheme (IGNWPS)** — Social security
- **State Schemes** apply specifically to residents of the state:
  - **Mukhyamantri Medhavi Vidyarthi Yojana (MMVY)** — Madhya Pradesh higher education 100% tuition fee scholarship
  - **Mukhyamantri Ladli Behna Yojana** — Madhya Pradesh women monthly aid
  - **Sanjay Gandhi Niradhar Anudan Yojana** — Maharashtra destitute & widow pension

---

## 🎭 The Three Golden Demo Personas

You can test the entire end-to-end journey for each persona with **one-click shortcut buttons on Screen S0**:

### 1. Rural Farmer
- **Profile**: 48-year-old male farmer in Madhya Pradesh, 1.5 hectares cultivable land, annual income ₹65,000, lives in kutcha house, BPL ration card.
- **Outcomes**:
  - `PM-KISAN`: **ELIGIBLE** (land <= 2 ha, farmer, non-institutional)
  - `PMAY-G`: **ELIGIBLE** (rural, kutcha house, low income)
  - `MMVY`: **NOT ELIGIBLE** (not a student)
- **Checklist**: Aadhaar, Land Record (Khasra/Khatauni), Bank Passbook, MGNREGA Job Card.

### 2. Widowed Woman
- **Profile**: 52-year-old widow in Madhya Pradesh, annual family income ₹24,000, BPL card holder.
- **Outcomes**:
  - `IGNWPS (Widow Pension)`: **ELIGIBLE** (widow, age 40-79, BPL)
  - `Ladli Behna (MP)`: **ELIGIBLE** (female, MP domicile, age 21-60, income <= 2.5 Lakhs)
  - `PM-KISAN`: **NOT ELIGIBLE** (not a farmer)
- **Checklist**: Aadhaar, Husband's Death Certificate, Samagra ID, BPL Card, DBT Bank Account.

### 3. College-going Student
- **Profile**: 19-year-old student residing in Madhya Pradesh, 86% in Class 12 board examination, enrolled in undergraduate engineering, annual family income ₹4,50,000.
- **Outcomes**:
  - `MMVY Scholarship`: **ELIGIBLE** (MP domicile, 12th marks >= 70% MPBSE / 85% CBSE, income <= 6 Lakhs, higher education admission)
  - `PM-KISAN`: **NOT ELIGIBLE** (not a farmer)
  - `IGNWPS`: **NOT ELIGIBLE** (not a widow)
- **Checklist**: Aadhaar, MP Domicile Certificate, Class 12th Marksheet, Income Certificate (<₹6 Lakhs), College Admission Allotment Letter.

---

## 🌐 Offline Dynamic Translation (no external API)

All translation runs on our own backend with **Argos Translate** (open-source, offline MT): no API keys, no per-request cost, and citizen text never leaves the server.

- **Dynamic, not static**: `en` is the source of truth. Any text without a hand-written Hindi/Bengali version (new schemes, restrictions, procedures, chat prompts, new UI strings) is translated on the fly and cached in memory. `hi.json` / `bn.json` are optional curated overrides.
- **Safe for civic content**: scheme/document names come from `data/glossary.json`; URLs, ₹ amounts, numbers and acronyms are shielded from the model.
- **Endpoints**: `POST /api/translate`, `POST /api/translate/batch`, `GET /api/translate/status`, and `?lang=hi|bn` on `/api/schemes[/{id}]`.
- **Frontend**: `useLanguage()` exposes `t(key)`, `lt(en, hi?, bn?)`, `tr(text)`, `getBilingualText(obj, field)` and `<Tr>`.
- **One-time setup** (internet only for the model download):
  ```bash
  cd backend && pip install -r requirements.txt
  python -m scripts.install_translation_models   # en<->hi, en<->bn; hi<->bn pivots via English
  # blocked network? download the .argosmodel files elsewhere, then add: --dir <folder>
  ```
  Until models are installed the app still works; untranslated text shows in its original language.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS, Lucide Icons, Web Speech API |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| **Data** | Independent verified JSON files per scheme in `backend/data/schemes/` |
| **AI** | Gemini 2.5 Flash via `google-genai` (with intelligent deterministic offline fallback) |
| **Voice & Lang** | Bhashini API with native Web Speech API fallback |
| **Testing** | Pytest (28 automated tests covering rules, boundary conditions, and personas) |

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API will be running at `http://localhost:8000`  
Interactive OpenAPI Swagger docs: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite dev server
npm run dev
```
Open `http://localhost:5173` in your browser. (Switch to responsive mobile view in DevTools for the best 360px–640px citizen experience!)

---

## 🧪 Running Automated Tests

Run the full backend test suite:
```bash
cd backend
python -m pytest -v
```

### Test Coverage Highlights:
- **`tests/test_rules.py`**: Validates every operator (`eq`, `ne`, `in`, `not_in`, `lte`, `gte`, `between`), borderline conditions (within 1% threshold), income bands crossing limits, unconfirmed field safety, and missing values.
- **`tests/test_evaluator.py`**: Tests scheme outcomes (`ELIGIBLE`, `NOT ELIGIBLE`, `NOT SURE`, `NO CURRENT RULES`), stale scheme verification threshold (>180 days), and state filtering.
- **`tests/test_question_selector.py`**: Validates dynamic question selection, maximum remaining scheme frequency, easiness tie-breaker, and stopping condition.
- **`tests/test_personas.py`**: End-to-end integration tests for the Rural Farmer, Widowed Woman, and College Student.
- **`tests/test_api.py`**: FastAPI route integration tests for all REST endpoints using `TestClient`.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/next-question` | Intelligent next question selection based on remaining undecided schemes |
| `POST` | `/api/evaluate` | Evaluates citizen profile against all official scheme rules |
| `GET` | `/api/schemes` | Returns list of all available official government schemes |
| `GET` | `/api/schemes/{id}` | Retrieves complete scheme definition, rules, and application procedure |
| `POST` | `/api/checklist` | Generates consolidated and de-duplicated document checklist |
| `POST` | `/api/parse-text` | Extracts permitted profile fields from citizen natural language |
| `POST` | `/api/chat` | Conversational assistant strictly grounded in verified scheme rules |
| `POST` | `/api/form-help` | Explains complicated government form fields and terminology |
| `POST` | `/api/speech-to-text` | Bhashini voice transcription with browser fallback |
| `POST` | `/api/text-to-speech` | Bhashini speech synthesis with browser fallback |
| `GET` | `/api/rules-status` | Verification and staleness audit report for all schemes |

---

## 🚀 Deployment Instructions

### Local admin setup (PowerShell)
The Admin Monitor is disabled until a username, PBKDF2 password hash, and 32+ character session secret are configured. From `backend`:

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "from getpass import getpass; from app.admin_auth import hash_admin_password; print(hash_admin_password(getpass('Admin password: ')))"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated password hash and session secret in `backend/.env`, set `ADMIN_USERNAME`, and keep `ADMIN_COOKIE_SECURE=false` only for local HTTP development. Production must use HTTPS, `ADMIN_COOKIE_SECURE=true`, and set `CORS_ALLOWED_ORIGINS` to the deployed frontend origin. For a separate frontend/backend site (for example Vercel + Render), also set `ADMIN_COOKIE_SAMESITE=none`; keep the CSRF header protection enabled. A same-site custom domain can use `strict`. Login is rate-limited; sessions expire after 30 minutes and use HttpOnly cookies plus CSRF checks. Do not use `X-Admin-Key`; shared-key access has been removed. Citizen scheme details are served from the local JSON catalogue, with myScheme page links; no myScheme API credentials are required and scheduled scraping is disabled by default.

`ENABLE_MONITORING_DEMO_DATA` defaults to `false`. Set it to `true` only for a demo database; synthetic rows are excluded from normal monitoring counts and lists.

### Frontend (Vercel)
1. Push repository to GitHub.
2. In Vercel, import the repository and set **Root Directory** to `frontend`.
3. Set Environment Variable: `VITE_API_URL=https://your-backend-service.onrender.com/api`.
4. Deploy!

### Backend (Render / Railway)
1. In Render, create a new **Web Service**.
2. Set **Root Directory** to `backend`.
3. Build Command: `pip install -r requirements.txt`.
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Add backend environment variables from `backend/.env.example`; generate the admin password hash as shown above. Set `ADMIN_COOKIE_SECURE=true` and the deployed frontend origin in `CORS_ALLOWED_ORIGINS`.
6. Deploy!

---

## 📄 License & Public Service Integrity
Built for citizen empowerment, transparency, and accessible public service delivery.
