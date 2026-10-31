import time
import json
import logging
from typing import List, Dict, Any, Optional
from .database import get_db_connection

logger = logging.getLogger("yojnasarthi_repo")

class SchemeRepository:
    @staticmethod
    def get_all_schemes() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes ORDER BY level, name_en")
        rows = cursor.fetchall()
        conn.close()

        schemes = []
        for r in rows:
            schemes.append({
                "id": r["scheme_id"],
                "name_en": r["name_en"],
                "name_hi": r["name_hi"],
                "level": r["level"],
                "category": r["category"],
                "applicable_states": json.loads(r["applicable_states"]),
                "benefit_en": r["benefit_en"],
                "benefit_hi": r["benefit_hi"],
                "description_en": r["description_en"],
                "description_hi": r["description_hi"],
                "rules": json.loads(r["rules_json"]),
                "required_documents": json.loads(r["required_documents_json"]),
                "application_procedure": json.loads(r["application_procedure_json"]),
                "restrictions": json.loads(r["restrictions_json"]),
                "official_source_url": r["official_source_url"],
                "helpline": r["helpline"],
                "last_verified_date": r["last_verified_date"],
            })
        return schemes

    @staticmethod
    def get_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes WHERE scheme_id = ?", (scheme_id,))
        r = cursor.fetchone()
        conn.close()

        if not r:
            return None

        return {
            "id": r["scheme_id"],
            "name_en": r["name_en"],
            "name_hi": r["name_hi"],
            "level": r["level"],
            "category": r["category"],
            "applicable_states": json.loads(r["applicable_states"]),
            "benefit_en": r["benefit_en"],
            "benefit_hi": r["benefit_hi"],
            "description_en": r["description_en"],
            "description_hi": r["description_hi"],
            "rules": json.loads(r["rules_json"]),
            "required_documents": json.loads(r["required_documents_json"]),
            "application_procedure": json.loads(r["application_procedure_json"]),
            "restrictions": json.loads(r["restrictions_json"]),
            "official_source_url": r["official_source_url"],
            "helpline": r["helpline"],
            "last_verified_date": r["last_verified_date"],
        }

class AuditRepository:
    @staticmethod
    def log_chat_interaction(
        user_query: str,
        detected_scheme_id: Optional[str] = None,
        detected_intent: Optional[str] = None,
        bot_response_preview: Optional[str] = None,
        language: str = "hi",
        session_id: Optional[str] = None
    ):
        """Logs chat query without any personal identity (Zero Citizen PII)."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            preview = bot_response_preview[:300] if bot_response_preview else ""
            cursor.execute("""
            INSERT INTO chat_audit_logs (session_id, user_query, detected_scheme_id, detected_intent, bot_response_preview, language)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_query[:500], detected_scheme_id, detected_intent, preview, language))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not log chat audit: {e}")

class FeedbackRepository:
    @staticmethod
    def save_feedback(scheme_id: Optional[str], rating: int, is_helpful: bool, comment: Optional[str], language: str = "hi"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO citizen_feedback (scheme_id, rating, is_helpful, comment, language)
            VALUES (?, ?, ?, ?, ?)
            """, (scheme_id, rating, is_helpful, comment[:500] if comment else None, language))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"Could not save feedback: {e}")
            return False

class RateLimiterRepository:
    @staticmethod
    def is_rate_limited(client_ip: str, endpoint: str, max_requests: int = 20, window_seconds: int = 60) -> bool:
        """Sliding-window rate limiter per client IP and endpoint."""
        now = time.time()
        cutoff = now - window_seconds
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Clean up old records
            cursor.execute("DELETE FROM rate_limit_records WHERE timestamp < ?", (cutoff,))
            # Count recent requests
            cursor.execute("SELECT COUNT(*) FROM rate_limit_records WHERE client_ip = ? AND endpoint = ? AND timestamp >= ?", (client_ip, endpoint, cutoff))
            count = cursor.fetchone()[0]

            if count >= max_requests:
                conn.commit()
                conn.close()
                return True

            cursor.execute("INSERT INTO rate_limit_records (client_ip, endpoint, timestamp) VALUES (?, ?, ?)", (client_ip, endpoint, now))
            conn.commit()
            conn.close()
            return False
        except Exception as e:
            logger.warning(f"Rate limiter error: {e}")
            return False

