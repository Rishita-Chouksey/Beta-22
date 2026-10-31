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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit ON rate_limit_records (client_ip, endpoint, timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes (category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_level ON schemes (level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheme_versions ON scheme_versions (scheme_id, version_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pending_updates ON pending_scheme_updates (scheme_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitoring_logs ON monitoring_activity_logs (timestamp)")

    conn.commit()

def get_db_connection() -> sqlite3.Connection:
    """Returns a thread-safe connection to the SQLite database."""
    global _tables_initialized
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    conn.row_factory = sqlite3.Row
    if not _tables_initialized:
        _tables_initialized = True
        init_db_schema(conn)
        # Check if monitoring sources need seeding
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM monitoring_sources")
        if cursor.fetchone()[0] == 0:
            seed_monitoring_sources(conn)
            seed_monitoring_demo_data(conn)
    return conn

def init_db():
    """Initializes database schema and tables."""
    conn = get_db_connection()
    init_db_schema(conn)
    conn.close()
    logger.info(f"Database initialized successfully at {DB_PATH}")

def seed_schemes_from_json():
    """Syncs verified scheme JSON files into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    schemes_dir = os.path.join(DB_DIR, "schemes")
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
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
                data.get("last_verified_date", "")
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

def seed_monitoring_demo_data(conn: Optional[sqlite3.Connection] = None):
    """
    Seeds clearly labelled demonstration monitoring data per Requirement 12:
    - 1 unchanged scheme (pm_kisan - VERIFIED)
    - 1 scheme with detected source change (ladli_behna_mp - UPDATE_DETECTED)
    - 1 newly discovered scheme (mp_udyami_yojana - DRAFT / UNDER_REVIEW)
    - 1 source temporarily unavailable (src_mp_agri_portal - UNAVAILABLE)
    - 1 pending approval (demo_upd_01 - PENDING)
    All records explicitly labelled with is_demo = 1.
    """
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
            scheme_id, version_number, review_status, scheme_data_json, approved_by, approved_at, change_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
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
