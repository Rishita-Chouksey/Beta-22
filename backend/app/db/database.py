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

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit ON rate_limit_records (client_ip, endpoint, timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes (category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemes_level ON schemes (level)")

    conn.commit()

def get_db_connection() -> sqlite3.Connection:
    """Returns a thread-safe connection to the SQLite database."""
    global _tables_initialized
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    if not _tables_initialized:
        init_db_schema(conn)
        _tables_initialized = True
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
