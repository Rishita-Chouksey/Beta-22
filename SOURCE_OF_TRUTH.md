# 🏛️ YojnaSarthi (योजनासारथी) — Living Source of Truth

> **DOCUMENT STATUS:** Active & Authoritative  
> **LAST UPDATED:** 2026-10-31  
> **PURPOSE:** This is the single, authoritative living reference document for the entire YojnaSarthi codebase. Developers and AI assistants (Claude, GPT, Gemini) must consult and update this document whenever modifying, adding, or refactoring capabilities.

---

## 📑 Table of Contents
1. [Core Purpose & Architectural Invariants](#1-core-purpose--architectural-invariants)
2. [Complete Implemented Tech Stack](#2-complete-implemented-tech-stack)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [User Journey & Screen Flow (S0 to S9)](#4-user-journey--screen-flow-s0-to-s9)
5. [Database Architecture & Relational Schema](#5-database-architecture--relational-schema)
6. [Voice & Audio Assistance Stack](#6-voice--audio-assistance-stack)
7. [Deterministic Rule Engine vs Generative AI](#7-deterministic-rule-engine-vs-generative-ai)
8. [Automated Scheme Intelligence & Catalogue Monitoring](#8-automated-scheme-intelligence--catalogue-monitoring)
9. [AI Helpdesk & Conversational Intelligence](#9-ai-helpdesk--conversational-intelligence)
10. [Document Guide & Form Field Assistance](#10-document-guide--form-field-assistance)
11. [Complete API Endpoint Registry](#11-complete-api-endpoint-registry)
12. [Privacy, Security & Rate Limiting Model](#12-privacy-security--rate-limiting-model)
13. [Directory Tree & File Responsibilities](#13-directory-tree--file-responsibilities)
14. [Test Suite & Quality Verification](#14-test-suite--quality-verification)
15. [How to Maintain & Update This Living Document](#15-how-to-maintain--update-this-living-document)

---

## 1. Core Purpose & Architectural Invariants

**YojnaSarthi (योजनासारथी)** is a privacy-first, bilingual (Hindi & English), AI-assisted government scheme eligibility and civic assistance platform designed specifically for Indian citizens, especially rural and low-digital-literacy users.

### Non-Negotiable Invariants:
1. **Rule Engine Is the Sole Eligibility Authority**:
   - The Python deterministic AST rule engine (`evaluator.py`) is the **sole decision-maker** for eligibility verdicts (`ELIGIBLE`, `NOT_ELIGIBLE`, `NOT_SURE`).
   - Generative AI (Gemini) **never** decides or overrides eligibility. AI only extracts profile attributes from natural language, explains results, and assists with form fields.
2. **Zero Persistent Citizen PII Storage (Privacy-First)**:
   - Citizen personal profile data (income, caste, gender, marital status, landholding) is stored **strictly in-memory** in React state.
   - **No `localStorage` or `sessionStorage`** is ever used for citizen profiles.
   - Database tables store zero personal citizen data. Chat audit logs store anonymous queries only.
   - Built-in **9-minute idle warning** and **10-minute automatic memory wipe**.
3. **True Dual-Language Parity (100% Bilingual)**:
   - Every heading, button, form placeholder, dropdown option, checklist item, and evaluation reason exists in both Hindi and English.
   - Switching language toggles 100% of the UI immediately without page reload or state loss.
4. **No Mandatory External API Credentials**:
   - The application does not require API Setu or myScheme credentials to function.
   - If Bhashini, Gemini, or external APIs are unavailable, deterministic offline fallbacks take over seamlessly.
5. **Human-in-the-Loop Approval for Scheme Catalogue Updates**:
   - The automated scheme monitor detects web updates from official portals and uses AI to summarize diffs.
   - Unapproved scraped changes **never reach the active eligibility evaluator**. Only human-approved versions are published.

---

## 2. Complete Implemented Tech Stack

| Layer | Technology | Version / Specifics | Responsibility |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React** | 19.3.1 | Core UI component hierarchy |
| **Frontend Bundler** | **Vite** | 8.3.5 | Build system, hot module reloading, production bundling |
| **Styling & Theme** | **Tailwind CSS** | 4.3.3 (`@tailwindcss/vite`) | Navy (`#0A192F`), Teal (`#0D9488`), and Slate (`#F8FAFC`) civic palette |
| **Icon Library** | **Lucide React** | 1.65.0 | Clean accessible UI iconography |
| **Frontend Linting** | **Oxlint** | 1.89.0 | Fast JavaScript & JSX linting |
| **Backend Framework** | **FastAPI** | >=0.110.0 | Async Python REST API server & auto OpenAPI docs |
| **ASGI Server** | **Uvicorn** | >=0.28.0 | High-performance asynchronous web server |
| **Data Validation** | **Pydantic** | >=2.6.0 (v2) | Strict schema validation for profiles, rules, and responses |
| **Database** | **SQLite 3** | File: `backend/data/yojnasarthi.db` | WAL mode, indexed relational store with automatic schema init |
| **Async HTTP Client** | **HTTPX** | >=0.27.0 | Non-blocking HTTP calls for Bhashini and polite crawler |
| **Generative AI** | **Google Gemini** | `google-genai` (2.5 Flash) | Natural language profile extraction and helpdesk reasoning |
| **Voice Speech-to-Text** | **Web Speech API** | Native `webkitSpeechRecognition` | Continuous streaming in-browser STT (`hi-IN` & `en-IN`) |
| **Voice Text-to-Speech** | **Web Speech Synthesis** | Native `speechSynthesis` | Local TTS with Indian voice selection & Devanagari acronym map |
| **Govt Voice API** | **Bhashini ULCA** | NLTM Dhruva Pipeline | Official Govt ASR & TTS integration with browser fallback |
| **Automated Testing** | **Pytest** | 9.2.0 + AnyIO | 78 automated unit, persona, eligibility, and monitoring tests |

---

## 3. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CITIZEN USER INTERFACE                             │
│   S0 Start  •  S1 Dynamic Questionnaire  •  S2 Voice/Text  •  S3 Confirm Profile │
│   S4 Results  •  S5 Scheme Modal  •  S6 Document Checklist  •  S7 Form Explainer │
│   S8 Document Guide  •  S9 Admin Scheme Monitor  •  ChatbotDrawer (AI Helpdesk)  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ JSON over HTTP REST
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND (Python 3.11)                         │
│   • SecurityAndPrivacyMiddleware (40 req/min sliding rate limit + security hdrs)│
│   • Background Scheduler (Daily automated official portal checks)               │
└──────────────┬─────────────────────────┬──────────────────────────┬─────────────┘
               │                         │                          │
               ▼                         ▼                          ▼
┌───────────────────────────┐ ┌─────────────────────────┐ ┌───────────────────────┐
│   DETERMINISTIC ENGINE    │ │    AI & NLP SERVICES    │ │  DATABASE & PERSISTENCE│
│ • AST Rule Evaluator      │ │ • Gemini 2.5 Flash SDK  │ │ • SQLite 3 (WAL Mode) │
│ • 3-Valued Logic Outcomes │ │ • 5 Semantic Handlers   │ │ • Schemes Catalog     │
│ • Info-Gain Questioner    │ │ • Grounded Diff Engine  │ │ • Version History     │
│ • Bilingual Reason Arrays │ │ • Bhashini ASR/TTS Fall.│ │ • Anonymous Audit Logs│
└───────────────────────────┘ └─────────────────────────┘ └───────────────────────┘
```

---

## 4. User Journey & Screen Flow (S0 to S9)

The frontend operates as a state machine managed by `SessionContext.jsx` with screens `S0` through `S9`:

```
[S0] Start Screen (Language Selector, Hero, Scheme Discovery, 3 Demo Personas)
  │
  ├──► [S1] Dynamic Adaptive Questionnaire (Information-gain optimized, <= 8 questions)
  │      │
  │      ▼
  └──► [S2] Voice / Free-Text Screen (Devanagari mic STT + Gemini profile parsing)
         │
         ▼
       [S3] Confirm Profile Screen (Explicit citizen confirmation with bilingual dropdowns)
         │
         ▼
       [S4] Results Screen (Eligible, Maybe Eligible, Ineligible tabs with criteria breakdown)
         │
         ├──► [S5] Scheme Details Modal (Full policy deep-dive & official portal links)
         ├──► [S6] Document Checklist Screen (De-duplicated document guide & print PDF)
         └──► [S7] Form Help Screen (Field-by-field guidance for official forms)

* Dedicated Standalone Portals:
  ├──► [S8] Document Guide Screen (Searchable 11+ document procurement catalog)
  └──► [S9] Admin Scheme Monitor (Protected dashboard for official portal tracking & approvals)

* Global Floating Widget:
  └──► [ChatbotDrawer] Persistent AI Helpdesk with multi-turn memory & voice read-aloud
```

---

## 5. Database Architecture & Relational Schema

Located at `backend/data/yojnasarthi.db`. Auto-initialized on startup by `init_db()` in WAL mode.

### Database Tables:
1. **`schemes`**: Verified government welfare scheme repository.
   - `scheme_id` (TEXT PK), `name_en`, `name_hi`, `level`, `category`, `applicable_states`, `benefit_en`, `benefit_hi`, `description_en`, `description_hi`, `rules_json`, `required_documents_json`, `application_procedure_json`, `restrictions_json`, `official_source_url`, `helpline`, `last_verified_date`.
2. **`scheme_versions`**: Immutable historical archive of approved scheme rules.
   - `id` (INTEGER PK AUTOINCREMENT), `scheme_id`, `version_number`, `review_status`, `scheme_data_json`, `approved_by`, `approved_at`, `change_summary`, `created_at`.
3. **`pending_scheme_updates`**: Web updates detected by crawler awaiting human review.
   - `update_id` (TEXT PK), `scheme_id`, `scheme_name_en`, `scheme_name_hi`, `source_id`, `source_url`, `detected_at`, `change_type`, `old_version_id`, `old_content_snippet`, `new_content_snippet`, `proposed_changes_json`, `ai_analysis_summary`, `status` (`PENDING`, `APPROVED`, `REJECTED`), `decision_reason`, `decision_by`, `decision_at`, `is_demo`.
4. **`monitoring_sources`**: Registry of monitored official government portals.
   - `source_id` (TEXT PK), `name`, `category`, `official_url`, `source_type` (`HTML`, `PDF`, `RSS`, `API`), `monitoring_frequency`, `target_scheme_ids`, `automated_monitoring_permitted`, `last_successful_check`, `last_detected_change`, `accessibility_status`, `error_details`, `content_hash`, `last_content_preview`.
5. **`monitoring_activity_logs`**: Chronological monitoring event log.
   - `id` (INTEGER PK AUTOINCREMENT), `source_id`, `scheme_id`, `timestamp`, `status`, `change_type`, `details`, `is_demo`.
6. **`chat_audit_logs`**: Anonymous AI Helpdesk interaction logs (**Zero Citizen PII**).
   - `id` (INTEGER PK AUTOINCREMENT), `session_id`, `user_query`, `detected_scheme_id`, `detected_intent`, `bot_response_preview`, `language`, `created_at`.
7. **`citizen_feedback`**: Anonymous scheme feedback and ratings (1 to 5).
   - `id` (INTEGER PK AUTOINCREMENT), `scheme_id`, `rating`, `is_helpful`, `comment`, `language`, `created_at`.
8. **`rate_limit_records`**: Sliding-window IP rate limiter records.
   - `id` (INTEGER PK AUTOINCREMENT), `client_ip`, `endpoint`, `timestamp`.

---

## 6. Voice & Audio Assistance Stack

### Speech-to-Text (Voice Mic):
- Implemented in [`frontend/src/services/speech.js`](file:///c:/Users/Lenovo/OneDrive/Desktop/YojnaSarthi/frontend/src/services/speech.js) and [`VoiceMic.jsx`](file:///c:/Users/Lenovo/OneDrive/Desktop/YojnaSarthi/frontend/src/components/VoiceMic.jsx).
- Uses native `webkitSpeechRecognition` with continuous listening (`recognition.continuous = true`).
- Emits real-time live interim transcripts (`onInterim`) into input fields.
- Language binding: `hi-IN` for Hindi, `en-IN` for English.
- Optional backend Bhashini ASR endpoint at `POST /api/bhashini/speech-to-text`.

### Text-to-Speech (Read-Aloud Speaker):
- Implemented in [`frontend/src/services/speech.js`](file:///c:/Users/Lenovo/OneDrive/Desktop/YojnaSarthi/frontend/src/services/speech.js) and [`AudioSpeaker.jsx`](file:///c:/Users/Lenovo/OneDrive/Desktop/YojnaSarthi/frontend/src/components/AudioSpeaker.jsx).
- Uses native `window.speechSynthesis` with Indian voice auto-selection (`Swara`, `Hemant`, `Kalpana` for Hindi; `en-IN`, `Ravi`, `Heera` for English).
- **Phonetic Acronym Engine**: Translates government abbreviations before speaking:
  - `MMVY` &rarr; *"एम.एम.वी.वाई."*
  - `PM-KISAN` &rarr; *"पीएम किसान"*
  - `DBT` &rarr; *"डीबीटी"* | `NPCI` &rarr; *"एनपीसीआई"* | `BPL` &rarr; *"बीपीएल"*
  - `₹500` &rarr; *"500 रुपये"* | `ha` &rarr; *"हेक्टेयर"*
- Strips markdown formatting so raw symbols (`*`, `#`, `•`) are never spoken out loud.
- Measured pacing: `0.90` speed for Hindi, `0.95` speed for Indian English.

---

## 7. Deterministic Rule Engine vs Generative AI

### The Separation Rule:
- **Generative AI (Gemini)** understands citizen natural language, extracts candidate profile fields, explains results in simple terms, and assists with form questions.
- **Python Rule Engine** evaluates citizen eligibility with mathematical certainty. Gemini is never permitted to emit or alter eligibility verdicts.

### Evaluation Mechanism (`backend/app/engine/`):
- `rules.py`: Evaluates comparison operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `between`.
- `evaluator.py`: Implements three-valued logic:
  - `ELIGIBLE`: All mandatory conditions pass.
  - `NOT_ELIGIBLE`: At least one mandatory condition fails.
  - `NOT_SURE`: Profile has missing or unconfirmed fields.
  - `STALE_RULES`: Rule verification age exceeds threshold (180 days).
  - `UNVERIFIED`: Scheme rules have not been vetted by a human reviewer.
- Emits bilingual criteria arrays on every run: `satisfied_conditions` / `satisfied_conditions_hi`, `failed_conditions` / `failed_conditions_hi`, `unknown_conditions` / `unknown_conditions_hi`.
- `question_selector.py`: Uses an information-gain algorithm to dynamically pick the next question that resolves the highest number of pending schemes, minimizing questionnaire length.

---

## 8. Automated Scheme Intelligence & Catalogue Monitoring

Located in `backend/app/monitoring/`:

1. **Official Source Registry (`source_registry.py`)**:
   - Central & MP government portals tracked independently (PM-KISAN, PM-JAY, PMAY-G, NSAP, NSP, Ladli Behna, MP Scholarship 2.0 MMVY, MP e-District, MP Farmer DBT, myScheme public reference, data.gov.in).
2. **Polite Web Crawler (`crawler.py`)**:
   - Checks `robots.txt` before fetching (`urllib.robotparser`).
   - Identifies with respectful civic User-Agent: `YojnaSarthi-SchemeMonitor/1.0 (+https://yojnasarthi.in/civic-bot)`.
   - Domain rate-limiting (1.0s delay), 12s timeout, max 2 retries.
   - Handles HTML pages, downloadable PDFs, and RSS/Atom feeds.
   - **Fault Isolation**: If one government server times out, all other sources continue monitoring.
3. **Content Fingerprinting (`fingerprint.py`)**:
   - Strips `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, dynamic session tokens, and timestamps.
   - Computes deterministic SHA-256 fingerprint.
   - Compares token deltas; ignores pure whitespace and trivial punctuation changes.
4. **AI-Assisted Policy Diff Analyzer (`change_analyzer.py`)**:
   - When a meaningful change is detected, invokes Gemini 2.5 Flash to summarize potential changes in income limits, age brackets, deadlines, required documents, and benefits.
   - Fallbacks to deterministic line-diff engine when Gemini is offline.
5. **Human Approval Workflow (`admin_monitoring.py`)**:
   - Detected changes are quarantined as `PENDING` updates in `pending_scheme_updates`.
   - Authorized reviewer inspects diffs on the Admin Dashboard (`S9`).
   - Reviewer enters audit reason and approves or rejects.
   - **Approval Action**: Archives previous version (v1 &rarr; v2), updates active rules in `schemes` table, and reloads in-memory cache.
   - **Rollback Action**: One-click rollback restores any historical version.

---

## 9. AI Helpdesk & Conversational Intelligence

Located in `backend/app/services/gemini_service.py` & `frontend/src/components/ChatbotDrawer.jsx`:

1. **Unrestricted Natural Language Queries**:
   - Handles manually typed queries in both Hindi and English across discovery, eligibility, document guidance, and policy questions.
2. **Conversational Multi-Turn Context**:
   - The `/api/chat` endpoint receives full message `history`. Resolves follow-ups (e.g. Turn 1: *"What is MMVY?"* &rarr; Turn 2: *"What documents are required for it?"*).
3. **Deterministic Semantic Fallback Handlers**:
   - If Gemini API is unconfigured or offline, 5 local intent handlers handle:
     - Beneficiary Discovery (widows, students, farmers, elderly).
     - Financial Threshold Inquiries (₹3 Lakh income comparisons).
     - Dual-Scholarship Policy Guidance (DBT single-benefit restrictions).
     - Built-in Document Knowledge Base (Income, Domicile, Bank DBT, Samagra ID, Death Certificate).
     - In-memory profile eligibility queries.
4. **UI Micro-Interactions**:
   - 3-dot animated typing indicator (`.typing-dot-1`, `.typing-dot-2`, `.typing-dot-3`).
   - Predefined quick-prompt suggestion chips.
   - Integrated microphone input button and read-aloud voice playback button on every bot message.

---

## 10. Document Guide & Form Field Assistance

1. **Document Guide Screen (`S8`) & Service (`document_service.py`)**:
   - Comprehensive procurement catalog of 11+ essential Indian documents (Aadhaar, MP Domicile, Income Certificate, Samagra ID, Bank Passbook with DBT, BPL Ration Card, Land Records Khasra, Death Certificate, Caste Certificate, Class 12 Marksheet, Disability Certificate).
   - Provides issuing authorities, online portal links, physical offices, estimated processing time, fee structure, and interactive synthetic document previews.
2. **Document Checklist Screen (`S6`) & Service (`checklist_service.py`)**:
   - Given a citizen's eligible schemes, generates a de-duplicated, consolidated checklist.
   - Cross-scheme document sharing (e.g., Aadhaar applies to all schemes once).
   - One-click Printable PDF view for offline submission.
3. **Form Field Explainer Screen (`S7`)**:
   - Demystifies complex government form terms (e.g. *NPCI/DBT Seeding, Khasra Number, Samagra ID, Domicile Certificate*) with real-world examples, tips, and voice read-aloud.

---

## 11. Complete API Endpoint Registry

All backend endpoints are prefixed with `/api` (except `/health` and `/`):

| Method | Endpoint | Protection | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | Public | System status, database health, scheme count, monitoring counts |
| `GET` | `/api/integrations/status` | Public | Detailed status of all 8 subsystems (myScheme, Bhashini, Monitoring, Engine, etc.) |
| `GET` | `/api/schemes` | Public | Lists all verified official government schemes |
| `GET` | `/api/schemes/{id}` | Public | Full scheme details, rules, required documents, and application steps |
| `GET` | `/api/schemes/{id}/rules-status` | Public | Rule verification age audit and staleness tracking |
| `POST` | `/api/evaluate` | Public | Evaluates citizen profile against all schemes deterministically |
| `POST` | `/api/next-question` | Public | Returns the next most informative question to minimize questionnaire length |
| `POST` | `/api/checklist` | Public | Generates de-duplicated document checklist for eligible schemes |
| `POST` | `/api/parse-text` | Rate Limited (40/min) | Extracts citizen profile fields from natural language text using Gemini/NLP |
| `POST` | `/api/chat` | Rate Limited (40/min) | Conversational AI Helpdesk supporting multi-turn chat in Hindi & English |
| `POST` | `/api/form-help` | Rate Limited (40/min) | Explains confusing government application form fields |
| `GET` | `/api/documents` | Public | Lists document procurement guides with category filtering and search |
| `GET` | `/api/documents/{doc_id}` | Public | Detailed document procurement instructions and synthetic sample |
| `POST` | `/api/bhashini/translate` | Public | Translates text between English and Hindi with glossary preservation |
| `POST` | `/api/bhashini/speech-to-text` | Public | Bhashini voice transcription endpoint (with browser fallback advice) |
| `POST` | `/api/bhashini/text-to-speech` | Public | Bhashini speech synthesis endpoint |
| `POST` | `/api/feedback` | Public | Anonymous scheme rating and feedback submission |
| `GET` | `/api/admin/monitoring/summary` | `X-Admin-Key` | System monitoring metrics, total sources, pending updates, verified schemes |
| `GET` | `/api/admin/monitoring/sources` | `X-Admin-Key` | Lists all monitored portals with health status and robots.txt permissions |
| `GET` | `/api/admin/monitoring/changes` | `X-Admin-Key` | Chronological audit trail of monitoring checks and detected changes |
| `GET` | `/api/admin/monitoring/pending-updates`| `X-Admin-Key` | Lists updates detected by crawler awaiting human verification |
| `GET` | `/api/admin/monitoring/schemes/{id}/history`| `X-Admin-Key`| Retrieves immutable version history for a specific scheme |
| `POST` | `/api/admin/monitoring/run` | `X-Admin-Key` | Triggers an on-demand polite monitoring check across official portals |
| `POST` | `/api/admin/monitoring/updates/{id}/approve`| `X-Admin-Key`| Approves a scheme update, publishes a new version, and reloads active rules |
| `POST` | `/api/admin/monitoring/updates/{id}/reject` | `X-Admin-Key`| Rejects a proposed update with an audit rationale |
| `POST` | `/api/admin/monitoring/schemes/{id}/rollback`| `X-Admin-Key`| Restores a scheme to a previous approved version |

---

## 12. Privacy, Security & Rate Limiting Model

1. **Security & Privacy Middleware (`backend/app/main.py`)**:
   - **Sliding-Window IP Rate Limiter**: Limits sensitive AI endpoints (`/api/chat`, `/api/parse-text`, `/api/form-help`) to **40 requests per minute** per client IP. Returns HTTP 429 when exceeded.
   - **Security Headers Injected**:
     - `X-Content-Type-Options: nosniff`
     - `X-Frame-Options: DENY`
     - `Referrer-Policy: strict-origin-when-cross-origin`
     - `X-XSS-Protection: 1; mode=block`
   - **Privacy-First Logging**: Omit personal citizen input fields, questionnaire answers, and audio payloads from application logs.
2. **Administrative Endpoint Security**:
   - Administrative endpoints (`/api/admin/monitoring/*`) require an `X-Admin-Key` header matching `ADMIN_API_KEY` from the backend environment.
   - Missing or invalid keys return HTTP 401/403.
   - Keys are held strictly in React component memory; never saved to browser storage.
3. **Git Hygiene & Virtual Environment Isolation**:
   - `backend_venv/`, `venv/`, `.env*`, `node_modules/`, `*.db`, and `__pycache__/` are untracked and strictly ignored via root `.gitignore`.
   - Virtual environments are **never** committed or pushed to Git.

---

## 13. Directory Tree & File Responsibilities

```
YojnaSarthi/
├── .gitignore                          # Root ignore: venv, .env, db, node_modules, pycache
├── README.md                           # Quickstart and overview guide
├── SOURCE_OF_TRUTH.md                  # THIS FILE: Master technical specification
│
├── backend/
│   ├── pytest.ini                      # Pytest configuration
│   ├── requirements.txt                # Python dependencies
│   ├── app/
│   │   ├── config.py                   # Pydantic Settings & environment variables
│   │   ├── main.py                     # FastAPI app, lifespan, security middleware, endpoints
│   │   ├── db/
│   │   │   ├── database.py             # SQLite connection, WAL mode, schema init, seeders
│   │   │   └── repository.py           # Repositories: Scheme, Audit, Feedback, RateLimiter, Monitoring
│   │   ├── engine/
│   │   │   ├── rules.py                # Deterministic AST rule operators (eq, lte, between, etc.)
│   │   │   ├── evaluator.py            # 3-valued scheme evaluator emitting bilingual condition reasons
│   │   │   └── question_selector.py    # Information-gain dynamic question selector
│   │   ├── models/
│   │   │   ├── api.py                  # API request/response schemas
│   │   │   ├── evaluation.py           # Evaluation models (bilingual criteria arrays)
│   │   │   ├── profile.py              # CitizenProfile model with strict validation
│   │   │   ├── scheme.py               # SchemeDefinition and SchemeRule models
│   │   │   └── document.py             # DocumentGuideItem model
│   │   ├── monitoring/
│   │   │   ├── models.py               # SourceDefinition, PendingUpdate, MonitoringSummary
│   │   │   ├── source_registry.py      # Central registry of official government portals
│   │   │   ├── crawler.py              # Polite web crawler checking robots.txt & domain delays
│   │   │   ├── fingerprint.py          # HTML/RSS cleaner & SHA-256 content fingerprinting
│   │   │   ├── change_analyzer.py      # Gemini 2.5 Flash diff analyzer + deterministic fallback
│   │   │   ├── monitor_service.py      # Central monitoring orchestrator
│   │   │   └── scheduler.py            # Async background task scheduler
│   │   ├── routes/
│   │   │   ├── eligibility.py          # /evaluate and /next-question
│   │   │   ├── schemes.py              # /schemes and /rules-status
│   │   │   ├── checklist.py            # /checklist
│   │   │   ├── ai.py                   # /chat, /parse-text, /form-help
│   │   │   ├── documents.py            # /documents catalog
│   │   │   ├── bhashini.py             # /bhashini integration endpoints
│   │   │   ├── voice.py                # Legacy voice endpoints
│   │   │   └── admin_monitoring.py     # /admin/monitoring/* (protected by X-Admin-Key)
│   │   └── services/
│   │       ├── scheme_service.py       # Scheme catalog (SQLite primary + JSON fallback)
│   │       ├── document_service.py     # Document guide procurement data
│   │       ├── checklist_service.py    # Document requirements & issuing authority service
│   │       ├── gemini_service.py       # Gemini AI client + 5 deterministic intent handlers
│   │       ├── bhashini_adapter.py     # Bhashini NMT, ASR, and TTS adapter
│   │       ├── bhashini_service.py     # Bhashini API client
│   │       └── myscheme_adapter.py     # myScheme / API Setu adapter with local fallback
│   ├── data/
│   │   ├── yojnasarthi.db              # SQLite relational database (WAL mode)
│   │   ├── schemes.json                # Verified government scheme repository
│   │   └── schemes/                    # Individual scheme JSON definitions
│   └── tests/
│       ├── test_api.py                 # 21 API tests (Chat, Feedback, Security, DB)
│       ├── test_monitoring.py          # 13 Scheme monitoring, crawler, approve/reject tests
│       ├── test_bhashini_adapter.py    # 5 Bhashini NMT, ASR, TTS tests
│       ├── test_document_guide.py      # 5 Document guide search & sample tests
│       ├── test_eligibility_accuracy.py# 9 Deterministic accuracy & persona tests
│       ├── test_evaluator.py           # 5 Evaluator unit tests
│       ├── test_integration_status.py  # 2 Integration status reporting tests
│       ├── test_myscheme_adapter.py    # 3 myScheme adapter & normalization tests
│       ├── test_personas.py            # 3 Real-world golden persona journey tests
│       ├── test_question_selector.py   # 2 Information-gain selection tests
│       └── test_rules.py               # 10 Rule operator unit tests (78 tests total)
│
└── frontend/
    ├── package.json                    # React 19, Vite 8, Tailwind CSS v4, Lucide React
    ├── vite.config.js                  # Vite configuration
    ├── index.html                      # HTML entry with responsive viewport
    └── src/
        ├── App.jsx                     # Root screen router switching between S0–S9
        ├── main.jsx                    # Application bootstrapping with providers
        ├── index.css                   # Tailwind v4 directives, custom colors, animations
        ├── components/
        │   ├── Header.jsx              # App header, language selector, admin monitor pill
        │   ├── ChatbotDrawer.jsx       # Floating AI Helpdesk (typing dots, mic, speaker)
        │   ├── AudioSpeaker.jsx        # Universal TTS read-aloud button
        │   ├── VoiceMic.jsx            # Universal continuous STT microphone input button
        │   ├── IdleWarningModal.jsx    # 9-minute citizen inactivity warning modal
        │   └── ClearExitModal.jsx      # Session reset confirmation modal
        ├── context/
        │   ├── LanguageContext.jsx     # Bilingual state provider (Hindi & English)
        │   └── SessionContext.jsx      # In-memory session state, profile, and 10-min auto-wipe
        ├── screens/
        │   ├── S0_StartScreen.jsx      # Start screen, hero, scheme discovery, 3 demo personas
        │   ├── S1_QuestionnaireScreen.jsx # Dynamic adaptive questions with read-aloud voice
        │   ├── S2_FreeTextInputScreen.jsx # Natural language / voice speech-to-text input screen
        │   ├── S3_ConfirmProfileScreen.jsx# Profile confirmation with bilingual dropdown options
        │   ├── S4_ResultsScreen.jsx    # Eligibility results (Eligible, Maybe, Ineligible tabs)
        │   ├── S5_SchemeDetailsModal.jsx  # Scheme deep-dive modal with official portal links
        │   ├── S6_DocumentChecklistScreen.jsx # Interactive checklist with issuing authorities
        │   ├── S7_FormHelpScreen.jsx   # Form field explainer for official applications
        │   ├── S8_DocumentGuideScreen.jsx # Comprehensive 11+ document procurement catalog
        │   └── S9_AdminMonitoringScreen.jsx # Scheme Intelligence Monitor dashboard
        ├── services/
        │   ├── api.js                  # Frontend API client communicating with FastAPI
        │   └── speech.js               # Web Speech STT & TTS engine with phonetic Devanagari map
        └── translations/
            ├── en.json                 # English dictionary (130+ translation keys)
            └── hi.json                 # Hindi dictionary (130+ translation keys)
```

---

## 14. Test Suite & Quality Verification

All 78 automated backend tests pass with 100% success rate:

```bash
.\backend_venv\Scripts\python.exe -m pytest backend/tests/ -v
# Output: 78 passed, 1 warning in ~13s
```

Frontend production build compiles cleanly with zero errors:

```bash
npm --prefix frontend run build
# Output: built in ~1.8s (dist/assets/index.js: ~442 kB)
```

---

## 15. How to Maintain & Update This Living Document

Whenever a new feature, screen, API endpoint, or database table is added or modified in YojnaSarthi:
1. **Update Section 2** if any dependency or tool version changes.
2. **Update Section 4 & 13** if a new screen, component, or file is introduced.
3. **Update Section 5** if new database tables, columns, or indexes are created.
4. **Update Section 11** whenever adding or changing API endpoints.
5. **Update Section 14** whenever new tests are added to the test suite.
6. **Preserve Section 1 Invariants**: Under no circumstance should a change violate the non-negotiable principles of rule engine authority, zero PII retention, or 100% bilingual parity.
