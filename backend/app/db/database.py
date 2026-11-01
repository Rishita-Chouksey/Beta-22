import sqlite3
import os
import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("yojnasarthi_db")

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DB_PATH = os.path.join(DB_DIR, "yojnasarthi.db")

_tables_initialized = False

def init_db_schema(conn: sqlite3.Connection):
    """Initializes tables on the given connection."""
    cursor = conn.cursor()

    # 1. Schemes table - persistent verified scheme catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        scheme_id TEXT PRIMARY KEY,
        name_en TEXT NOT NULL,
        name_hi TEXT NOT NULL,
        level TEXT NOT NULL,
        category TEXT NOT NULL,
        applicable_states TEXT NOT NULL,
        benefit_en TEXT NOT NULL,
        benefit_hi TEXT NOT NULL,
        description_en TEXT NOT NULL,
        description_hi TEXT NOT NULL,
        rules_json TEXT NOT NULL,
        required_documents_json TEXT NOT NULL,
        application_procedure_json TEXT NOT NULL,
        restrictions_json TEXT NOT NULL,
        official_source_url TEXT NOT NULL,
        helpline TEXT,
        last_verified_date TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'verified',
        verified_by_json TEXT NOT NULL DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    scheme_cols = {col[1] for col in cursor.execute("PRAGMA table_info(schemes)").fetchall()}
    if "review_status" not in scheme_cols:
        cursor.execute("ALTER TABLE schemes ADD COLUMN review_status TEXT NOT NULL DEFAULT 'verified'")
    if "verified_by_json" not in scheme_cols:
        cursor.execute("ALTER TABLE schemes ADD COLUMN verified_by_json TEXT NOT NULL DEFAULT '[]'")

    # 2. Chat Audit Logs table - tracks helpdesk interactions (ZERO Citizen PII)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        user_query TEXT NOT NULL,
        detected_scheme_id TEXT,
        detected_intent TEXT,
        bot_response_preview TEXT,
        language TEXT DEFAULT 'hi',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Older versions stored free-text citizen queries; scrub them on startup.
    cursor.execute("UPDATE chat_audit_logs SET session_id = NULL, user_query = '', bot_response_preview = NULL")
    cursor.execute("DELETE FROM chat_audit_logs WHERE created_at < datetime('now', '-30 days')")

    # 3. Citizen Feedback table - anonymous scheme feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizen_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id TEXT,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        is_helpful BOOLEAN,
        comment TEXT,
        language TEXT DEFAULT 'hi',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. Rate Limiting records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rate_limit_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_ip TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        timestamp REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_sessions (
        session_id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        expires_at INTEGER NOT NULL,
        revoked_at INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("DELETE FROM rate_limit_records WHERE timestamp < CAST(strftime('%s', 'now') AS REAL) - 60")
    cursor.execute("""DELETE FROM admin_sessions
        WHERE expires_at < CAST(strftime('%s', 'now') AS INTEGER) - 86400
           OR (revoked_at IS NOT NULL AND revoked_at < CAST(strftime('%s', 'now') AS INTEGER) - 86400)""")

    # 5. Monitoring Sources Registry table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_sources (
        source_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        official_url TEXT NOT NULL,
        source_type TEXT NOT NULL,
        monitoring_frequency TEXT NOT NULL,
        target_scheme_ids TEXT NOT NULL,
        automated_monitoring_permitted BOOLEAN DEFAULT 1,
        last_successful_check TEXT,
        last_detected_change TEXT,
        accessibility_status TEXT DEFAULT 'pending',
        error_details TEXT,
        content_hash TEXT,
        last_content_preview TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Scheme Version History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scheme_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id TEXT NOT NULL,
        version_number INTEGER NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'VERIFIED',
        scheme_data_json TEXT NOT NULL,
        approved_by TEXT,
        approved_at TEXT,
        change_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. Pending Scheme Updates table (Awaiting Human Approval)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pending_scheme_updates (
        update_id TEXT PRIMARY KEY,
        scheme_id TEXT NOT NULL,
        scheme_name_en TEXT NOT NULL,
        scheme_name_hi TEXT NOT NULL,
        source_id TEXT NOT NULL,
        source_url TEXT NOT NULL,
        detected_at TEXT NOT NULL,
        change_type TEXT NOT NULL,
        old_version_id INTEGER,
        old_content_snippet TEXT,
        new_content_snippet TEXT,
        proposed_changes_json TEXT,
        ai_analysis_summary TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        decision_reason TEXT,
        decision_by TEXT,
        decision_at TEXT,
        is_demo BOOLEAN DEFAULT 0
    )
    """)

    # 8. Monitoring Activity Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT,
        scheme_id TEXT,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        change_type TEXT,
        details TEXT,
        is_demo BOOLEAN DEFAULT 0
    )
    """)

    # 9. Multi-Agent Discovery: sources table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        url TEXT UNIQUE NOT NULL,
        domain TEXT NOT NULL,
        source_type TEXT NOT NULL,
        discovered_from TEXT,
        status TEXT DEFAULT 'discovered',
        last_checked_at TEXT,
        last_successful_fetch_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 10. Multi-Agent Discovery: source_snapshots table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_snapshots (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        extracted_content TEXT NOT NULL,
        retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        document_type TEXT NOT NULL,
        previous_snapshot_id TEXT,
        FOREIGN KEY(source_id) REFERENCES sources(id)
    )
    """)

    # 11. Multi-Agent Discovery: discovered_schemes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovered_schemes (
        id TEXT PRIMARY KEY,
        scheme_name TEXT NOT NULL,
        department TEXT,
        state TEXT,
        source_id TEXT NOT NULL,
        source_url TEXT NOT NULL,
        extracted_data TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        first_discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(source_id) REFERENCES sources(id)
    )
    """)

    # 12. Multi-Agent Discovery: proposed_updates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proposed_updates (
        id TEXT PRIMARY KEY,
        scheme_id TEXT NOT NULL,
        change_type TEXT NOT NULL,
        old_value TEXT,
        proposed_value TEXT,
        evidence TEXT,
        source_url TEXT NOT NULL,
        confidence REAL DEFAULT 0.85,
        review_status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP
    )
    """)
    proposed_cols = {col[1] for col in cursor.execute("PRAGMA table_info(proposed_updates)").fetchall()}
    if "reviewed_by" not in proposed_cols:
        cursor.execute("ALTER TABLE proposed_updates ADD COLUMN reviewed_by TEXT")
    if "review_reason" not in proposed_cols:
        cursor.execute("ALTER TABLE proposed_updates ADD COLUMN review_reason TEXT")

    # 13. Multi-Agent Discovery: agent_runs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_runs (
        id TEXT PRIMARY KEY,
        agent_name TEXT NOT NULL,
        status TEXT NOT NULL,
        input_summary TEXT,
        output_summary TEXT,
        error_message TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    """)

    # Ensure scheme_versions columns exist for Section 5 schema compatibility
    cursor.execute("PRAGMA table_info(scheme_versions)")
    existing_cols = {col[1] for col in cursor.fetchall()}
    if "source_url" not in existing_cols:
        cursor.execute("ALTER TABLE scheme_versions ADD COLUMN source_url TEXT")
    if "scheme_data" not in existing_cols:
        cursor.execute("ALTER TABLE scheme_versions ADD COLUMN scheme_data TEXT")
    if "approval_status" not in existing_cols:
        cursor.execute("ALTER TABLE scheme_versions ADD COLUMN approval_status TEXT DEFAULT 'APPROVED'")
    if "is_demo" not in existing_cols:
        cursor.execute("ALTER TABLE scheme_versions ADD COLUMN is_demo BOOLEAN DEFAULT 0")
    cursor.execute("""UPDATE scheme_versions SET is_demo = 1
        WHERE scheme_id = 'ladli_behna_mp'
          AND approved_by = 'Senior Verification Officer (Govt of MP)'
          AND change_summary = 'Initial audited baseline rules verified.'""")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit ON rate_limit_records (client_ip, endpoint, timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes (category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_level ON schemes (level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheme_versions ON scheme_versions (scheme_id, version_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pending_updates ON pending_scheme_updates (scheme_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitoring_logs ON monitoring_activity_logs (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_domain ON sources (domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_status ON sources (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_source ON source_snapshots (source_id, retrieved_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disc_schemes_src ON discovered_schemes (source_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prop_updates_status ON proposed_updates (review_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_runs_name ON agent_runs (agent_name, started_at)")
    seed_agent_sources(conn)
    conn.commit()

def get_db_connection() -> sqlite3.Connection:
    """Returns a thread-safe connection to the SQLite database."""
    global _tables_initialized
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    conn.execute("PRAGMA busy_timeout = 10000;")
    conn.row_factory = sqlite3.Row
    if not _tables_initialized:
        _tables_initialized = True
        init_db_schema(conn)
        # Check if monitoring sources need seeding
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM monitoring_sources")
        if cursor.fetchone()[0] == 0:
            seed_monitoring_sources(conn)
    return conn

def init_db():
    """Initializes database schema and tables."""
    conn = get_db_connection()
    conn.close()
    logger.info(f"Database initialized successfully at {DB_PATH}")

def seed_schemes_from_json():
    """Syncs verified scheme JSON files into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    root_schemes_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "schemes"))
    backend_schemes_dir = os.path.join(DB_DIR, "schemes")
    schemes_dir = root_schemes_dir if os.path.exists(root_schemes_dir) else backend_schemes_dir

    if not os.path.exists(schemes_dir):
        conn.close()
        return

    json_files = [f for f in os.listdir(schemes_dir) if f.endswith(".json")]
    seeded_count = 0

    for jf in json_files:
        fpath = os.path.join(schemes_dir, jf)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            scheme_id = data.get("id")
            if not scheme_id:
                continue

            cursor.execute("""
            INSERT INTO schemes (
                scheme_id, name_en, name_hi, level, category, applicable_states,
                benefit_en, benefit_hi, description_en, description_hi,
                rules_json, required_documents_json, application_procedure_json,
                restrictions_json, official_source_url, helpline, last_verified_date, updated_at
                , review_status, verified_by_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            ON CONFLICT(scheme_id) DO UPDATE SET
                name_en=excluded.name_en,
                name_hi=excluded.name_hi,
                level=excluded.level,
                category=excluded.category,
                applicable_states=excluded.applicable_states,
                benefit_en=excluded.benefit_en,
                benefit_hi=excluded.benefit_hi,
                description_en=excluded.description_en,
                description_hi=excluded.description_hi,
                rules_json=excluded.rules_json,
                required_documents_json=excluded.required_documents_json,
                application_procedure_json=excluded.application_procedure_json,
                restrictions_json=excluded.restrictions_json,
                official_source_url=excluded.official_source_url,
                helpline=excluded.helpline,
                last_verified_date=excluded.last_verified_date,
                review_status=excluded.review_status,
                verified_by_json=excluded.verified_by_json,
                updated_at=CURRENT_TIMESTAMP
            """, (
                scheme_id,
                data.get("name_en", ""),
                data.get("name_hi", ""),
                data.get("level", "central"),
                data.get("category", "General"),
                json.dumps(data.get("applicable_states", [])),
                data.get("benefit_en", ""),
                data.get("benefit_hi", ""),
                data.get("description_en", ""),
                data.get("description_hi", ""),
                json.dumps(data.get("rules", [])),
                json.dumps(data.get("required_documents", [])),
                json.dumps(data.get("application_procedure", [])),
                json.dumps(data.get("restrictions", [])),
                data.get("official_source_url", ""),
                data.get("helpline", ""),
                data.get("last_verified_date", ""),
                data.get("review_status", "verified"),
                json.dumps(data.get("verified_by", []), ensure_ascii=False)
            ))
            seeded_count += 1
        except Exception as e:
            logger.error(f"Failed to seed scheme from {jf}: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Seeded/synced {seeded_count} schemes into database.")

def seed_monitoring_sources(conn: Optional[sqlite3.Connection] = None):
    """Initializes official sources registry into SQLite database."""
    from ..monitoring.source_registry import OFFICIAL_SOURCE_CATALOG
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    cursor = conn.cursor()

    # Keep historical monitoring rows, but retire previous sources; the current
    # catalogue is manually curated from myScheme pages, not crawled in the background.
    active_reference_urls = [src.official_url for src in OFFICIAL_SOURCE_CATALOG]
    placeholders = ", ".join("?" for _ in active_reference_urls)
    cursor.execute(f"""
        UPDATE monitoring_sources
        SET automated_monitoring_permitted = 0,
            error_details = 'RETIRED: replaced by the manually curated myScheme scheme pages.'
        WHERE official_url NOT IN ({placeholders})
    """, active_reference_urls)

    for src in OFFICIAL_SOURCE_CATALOG:
        cursor.execute("""
        INSERT INTO monitoring_sources (
            source_id, name, category, official_url, source_type, monitoring_frequency,
            target_scheme_ids, automated_monitoring_permitted, accessibility_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            name=excluded.name,
            category=excluded.category,
            official_url=excluded.official_url,
            source_type=excluded.source_type,
            monitoring_frequency=excluded.monitoring_frequency,
            target_scheme_ids=excluded.target_scheme_ids,
            automated_monitoring_permitted=excluded.automated_monitoring_permitted
        """, (
            src.source_id,
            src.name,
            src.category.value,
            src.official_url,
            src.source_type.value,
            src.monitoring_frequency.value,
            json.dumps(src.target_scheme_ids),
            src.automated_monitoring_permitted,
            src.accessibility_status.value
        ))

    conn.commit()
    if should_close:
        conn.close()

def seed_monitoring_demo_data(conn: Optional[sqlite3.Connection] = None, *, enabled: bool = False):
    """
    Seeds clearly labelled demonstration monitoring data per Requirement 12:
    - 1 unchanged scheme (pm_kisan - VERIFIED)
    - 1 scheme with detected source change (ladli_behna_mp - UPDATE_DETECTED)
    - 1 newly discovered scheme (mp_udyami_yojana - DRAFT / UNDER_REVIEW)
    - 1 source temporarily unavailable (src_mp_agri_portal - UNAVAILABLE)
    - 1 pending approval (demo_upd_01 - PENDING)
    All records explicitly labelled with is_demo = 1.
    """
    if not enabled:
        logger.info("Monitoring demo data disabled; no synthetic records seeded.")
        return
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    cursor = conn.cursor()

    # 1. Update source status for demo unavailable source
    cursor.execute("""
    INSERT INTO monitoring_sources (
        source_id, name, category, official_url, source_type, monitoring_frequency,
        target_scheme_ids, automated_monitoring_permitted, accessibility_status, error_details
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(source_id) DO UPDATE SET
        accessibility_status=excluded.accessibility_status,
        error_details=excluded.error_details
    """, (
        "src_mp_farmer_dbt",
        "Madhya Pradesh Kisan Kalyan & Agriculture DBT Portal",
        "madhya_pradesh",
        "https://dbt.mp.gov.in/",
        "HTML",
        "weekly",
        json.dumps(["mp_kisan_kalyan"]),
        1,
        "unavailable",
        "DEMO/SYNTHETIC: Gateway Timeout (504) - Connection to departmental server timed out."
    ))

    # 2. Add an initial scheme version for ladli_behna_mp if not present
    cursor.execute("SELECT id FROM scheme_versions WHERE scheme_id = 'ladli_behna_mp'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO scheme_versions (
            scheme_id, version_number, review_status, scheme_data_json, approved_by, approved_at, change_summary, is_demo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            "ladli_behna_mp",
            1,
            "VERIFIED",
            json.dumps({"name_en": "Mukhyamantri Ladli Behna Yojana", "income_limit": 250000, "age_min": 21, "age_max": 60}),
            "Senior Verification Officer (Govt of MP)",
            "2026-06-15 10:00:00",
            "Initial audited baseline rules verified."
        ))

    # 3. Add demo pending update awaiting human approval
    cursor.execute("""
    INSERT INTO pending_scheme_updates (
        update_id, scheme_id, scheme_name_en, scheme_name_hi, source_id, source_url,
        detected_at, change_type, old_version_id, old_content_snippet, new_content_snippet,
        proposed_changes_json, ai_analysis_summary, status, is_demo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(update_id) DO UPDATE SET
        ai_analysis_summary=excluded.ai_analysis_summary,
        status=excluded.status
    """, (
        "demo_upd_ladlibehna_01",
        "ladli_behna_mp",
        "Mukhyamantri Ladli Behna Yojana",
        "मुख्यमंत्री लाड़ली बहना योजना",
        "src_mp_ladlibehna",
        "https://cmladlibahna.mp.gov.in/",
        "2026-10-31 09:15:00",
        "CONTENT_MODIFIED",
        1,
        "पात्रता: परिवार की वार्षिक आय ₹2.5 लाख से अधिक न हो। आयु 21 से 60 वर्ष।",
        "नवीन निर्देश: परिवार की वार्षिक आय ₹2.5 लाख तक, तथा समग्र ई-केवाईसी एवं प्रत्यक्ष लाभ अंतरण (DBT) सक्रिय बैंक खाता अनिवार्य है।",
        json.dumps({
            "field": "annual_income",
            "proposed_threshold": 250000,
            "clarification": "Mandatory active NPCI-DBT linking required for monthly assistance transfer."
        }),
        "[DEMO / SYNTHETIC AI ANALYSIS]\n• Source: https://cmladlibahna.mp.gov.in/\n• Identified Change: Portal added strict explicit guidelines regarding mandatory Aadhaar DBT bank linking.\n• Eligibility Impact: Core age (21-60) and income criteria (<= ₹2.5 Lakh) remain unchanged.\n• Recommendation: Approve update to reflect enhanced DBT bank passbook documentation checklist.",
        "PENDING",
        1
    ))

    # 4. Insert demo activity logs
    cursor.execute("""
    INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "src_mp_ladlibehna",
        "ladli_behna_mp",
        "2026-10-31 09:15:00",
        "CHANGE_DETECTED",
        "CONTENT_MODIFIED",
        "[DEMO] Source change detected on cmladlibahna.mp.gov.in. Generated pending update demo_upd_ladlibehna_01.",
        1
    ))

    cursor.execute("""
    INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "src_central_pmkisan",
        "pm_kisan",
        "2026-10-31 08:00:00",
        "SUCCESS",
        "NO_CHANGE",
        "[DEMO] Portal checked. Content hash unchanged (SHA-256 matches verified baseline).",
        1
    ))

    cursor.execute("""
    INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "src_mp_farmer_dbt",
        "mp_kisan_kalyan",
        "2026-10-31 08:02:15",
        "FAILED",
        "SOURCE_UNAVAILABLE",
        "[DEMO] Server timeout after 2 retries (HTTP 504 Gateway Timeout).",
        1
    ))

    conn.commit()
    if should_close:
        conn.close()
    logger.info("Seeded monitoring sources and synthetic demonstration dataset.")

def seed_agent_sources(conn: Optional[sqlite3.Connection] = None):
    """Registers myScheme as the discovery root and retires the former portal roots."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    cursor = conn.cursor()
    # Retain historical records, but keep the old roots out of active discovery/monitoring.
    cursor.execute("""
        UPDATE sources SET status = 'disabled'
        WHERE lower(domain) LIKE '%data.gov.in' OR lower(domain) LIKE '%eseva.mp.gov.in'
    """)
    seeds = [
        ("src_seed_myscheme", "https://www.myscheme.gov.in/", "www.myscheme.gov.in", "PORTAL", "manual_catalog_source", "discovered")
    ]
    for s_id, s_url, s_dom, s_type, s_from, s_stat in seeds:
        cursor.execute("""
        INSERT INTO sources (id, url, domain, source_type, discovered_from, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """, (s_id, s_url, s_dom, s_type, s_from, s_stat))
    conn.commit()
    if should_close:
        conn.close()
    logger.info("Registered myScheme and retired the former discovery roots.")
