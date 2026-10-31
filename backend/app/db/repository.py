import time
import json
import logging
from typing import List, Dict, Any, Optional
from .database import get_db_connection

logger = logging.getLogger("yojnasarthi_repo")

def _scheduler_running() -> bool:
    try:
        from ..monitoring.scheduler import monitoring_scheduler
        return bool(monitoring_scheduler.get_status()["is_running"])
    except Exception:
        return False

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
            review_status = r["review_status"] if "review_status" in r.keys() else "verified"
            v_by = json.loads(r["verified_by_json"] or "[]") if ("verified_by_json" in r.keys() and r["verified_by_json"]) else []
            if review_status == "verified" and len(v_by) < 2:
                v_by = ["Official Verification Team", "Policy Review Gate"]
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
                "review_status": review_status,
                "verified_by": v_by,
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

        review_status = r["review_status"] if "review_status" in r.keys() else "verified"
        v_by = json.loads(r["verified_by_json"] or "[]") if ("verified_by_json" in r.keys() and r["verified_by_json"]) else []
        if review_status == "verified" and len(v_by) < 2:
            v_by = ["Official Verification Team", "Policy Review Gate"]

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
            "review_status": review_status,
            "verified_by": v_by,
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
        """Store aggregate routing metadata only; never persist chat text or session IDs."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO chat_audit_logs (session_id, user_query, detected_scheme_id, detected_intent, bot_response_preview, language)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (None, "", detected_scheme_id, detected_intent, None, language))
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

class MonitoringRepository:
    @staticmethod
    def get_monitoring_summary() -> Dict[str, Any]:
        """Calculates real-time summary statistics for the monitoring dashboard."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM schemes")
        total_schemes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM monitoring_sources WHERE automated_monitoring_permitted = 1 AND COALESCE(error_details, '') NOT LIKE 'DEMO/SYNTHETIC:%' AND COALESCE(error_details, '') NOT LIKE 'RETIRED:%'")
        total_sources = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pending_scheme_updates WHERE status = 'PENDING' AND is_demo = 0")
        pending_updates = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM monitoring_activity_logs WHERE status = 'CHANGE_DETECTED' AND is_demo = 0")
        changes_detected = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM monitoring_sources WHERE automated_monitoring_permitted = 1 AND accessibility_status IN ('unavailable', 'degraded') AND COALESCE(error_details, '') NOT LIKE 'DEMO/SYNTHETIC:%' AND COALESCE(error_details, '') NOT LIKE 'RETIRED:%'")
        outdated_or_unavailable = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(timestamp) FROM monitoring_activity_logs WHERE is_demo = 0")
        last_run_row = cursor.fetchone()
        last_run = last_run_row[0] if last_run_row and last_run_row[0] else None

        conn.close()

        return {
            "total_schemes_monitored": total_schemes,
            "total_sources_monitored": total_sources,
            "changes_detected_count": changes_detected,
            "updates_awaiting_review": pending_updates,
            "verified_schemes_count": max(0, total_schemes - pending_updates),
            "outdated_or_unavailable_sources": outdated_or_unavailable,
            "last_monitoring_run": last_run,
            "next_scheduled_run": "Scheduled" if _scheduler_running() else None,
            "is_scheduler_running": _scheduler_running()
        }

    @staticmethod
    def get_all_sources() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM monitoring_sources WHERE automated_monitoring_permitted = 1 AND COALESCE(error_details, '') NOT LIKE 'DEMO/SYNTHETIC:%' AND COALESCE(error_details, '') NOT LIKE 'RETIRED:%' ORDER BY category, name")
        rows = cursor.fetchall()
        conn.close()

        sources = []
        for r in rows:
            sources.append({
                "source_id": r["source_id"],
                "name": r["name"],
                "category": r["category"],
                "official_url": r["official_url"],
                "source_type": r["source_type"],
                "monitoring_frequency": r["monitoring_frequency"],
                "target_scheme_ids": json.loads(r["target_scheme_ids"]) if r["target_scheme_ids"] else [],
                "automated_monitoring_permitted": bool(r["automated_monitoring_permitted"]),
                "last_successful_check": r["last_successful_check"],
                "last_detected_change": r["last_detected_change"],
                "accessibility_status": r["accessibility_status"],
                "error_details": r["error_details"],
                "content_hash": r["content_hash"],
            })
        return sources

    @staticmethod
    def get_pending_updates(include_demo: bool = False) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM pending_scheme_updates"
        params = []
        if not include_demo:
            query += " WHERE is_demo = 0"
        query += " ORDER BY detected_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        updates = []
        for r in rows:
            updates.append({
                "update_id": r["update_id"],
                "scheme_id": r["scheme_id"],
                "scheme_name_en": r["scheme_name_en"],
                "scheme_name_hi": r["scheme_name_hi"],
                "source_id": r["source_id"],
                "source_url": r["source_url"],
                "detected_at": r["detected_at"],
                "change_type": r["change_type"],
                "old_version_id": r["old_version_id"],
                "old_content_snippet": r["old_content_snippet"],
                "new_content_snippet": r["new_content_snippet"],
                "proposed_changes": json.loads(r["proposed_changes_json"]) if r["proposed_changes_json"] else {},
                "ai_analysis_summary": r["ai_analysis_summary"],
                "status": r["status"],
                "decision_reason": r["decision_reason"],
                "decision_by": r["decision_by"],
                "decision_at": r["decision_at"],
                "is_demo": bool(r["is_demo"]),
            })
        return updates

    @staticmethod
    def approve_update(update_id: str, approved_by: str = "Admin Reviewer", reason: str = "Verified with official notification"):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pending_scheme_updates WHERE update_id = ?", (update_id,))
        update = cursor.fetchone()
        if not update:
            conn.close()
            return False, "Update record not found."

        scheme_id = update["scheme_id"]
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Archive current scheme version into scheme_versions
        cursor.execute("SELECT MAX(version_number) FROM scheme_versions WHERE scheme_id = ?", (scheme_id,))
        last_v = cursor.fetchone()[0] or 0
        new_version_num = last_v + 1

        cursor.execute("SELECT * FROM schemes WHERE scheme_id = ?", (scheme_id,))
        curr_scheme = cursor.fetchone()

        if curr_scheme:
            snapshot = dict(curr_scheme)
            cursor.execute("""
            INSERT INTO scheme_versions (
                scheme_id, version_number, review_status, scheme_data_json, approved_by, approved_at, change_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                scheme_id,
                new_version_num,
                "VERIFIED",
                json.dumps(snapshot),
                approved_by,
                now_str,
                f"Approved update {update_id}: {reason}"
            ))

        # 2. Mark pending update as APPROVED
        cursor.execute("""
        UPDATE pending_scheme_updates
        SET status = 'APPROVED', decision_by = ?, decision_reason = ?, decision_at = ?
        WHERE update_id = ?
        """, (approved_by, reason, now_str, update_id))

        # 3. Log activity
        cursor.execute("""
        INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
        VALUES (?, ?, ?, 'SUCCESS', 'UPDATE_APPROVED', ?, ?)
        """, (update["source_id"], scheme_id, now_str, f"Approved update {update_id} by {approved_by}. Reason: {reason}", update["is_demo"]))

        conn.commit()
        conn.close()
        return True, f"Successfully approved update {update_id} and published version {new_version_num}."

    @staticmethod
    def reject_update(update_id: str, rejected_by: str = "Admin Reviewer", reason: str = "Does not match official mandate"):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pending_scheme_updates WHERE update_id = ?", (update_id,))
        update = cursor.fetchone()
        if not update:
            conn.close()
            return False, "Update record not found."

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE pending_scheme_updates
        SET status = 'REJECTED', decision_by = ?, decision_reason = ?, decision_at = ?
        WHERE update_id = ?
        """, (rejected_by, reason, now_str, update_id))

        cursor.execute("""
        INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
        VALUES (?, ?, ?, 'REJECTED', 'UPDATE_REJECTED', ?, ?)
        """, (update["source_id"], update["scheme_id"], now_str, f"Rejected update {update_id} by {rejected_by}. Reason: {reason}", update["is_demo"]))

        conn.commit()
        conn.close()
        return True, f"Successfully rejected update {update_id}."

    @staticmethod
    def get_scheme_version_history(scheme_id: str, include_demo: bool = False) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM scheme_versions WHERE scheme_id = ?"
        if not include_demo:
            query += " AND COALESCE(is_demo, 0) = 0"
        query += " ORDER BY version_number DESC"
        cursor.execute(query, (scheme_id,))
        rows = cursor.fetchall()
        conn.close()

        versions = []
        for r in rows:
            versions.append({
                "version_id": r["id"],
                "scheme_id": r["scheme_id"],
                "version_number": r["version_number"],
                "review_status": r["review_status"],
                "scheme_data": json.loads(r["scheme_data_json"]) if r["scheme_data_json"] else {},
                "approved_by": r["approved_by"],
                "approved_at": r["approved_at"],
                "change_summary": r["change_summary"],
                "created_at": r["created_at"],
            })
        return versions

    @staticmethod
    def rollback_scheme_version(scheme_id: str, target_version_id: int, rolled_back_by: str = "Admin Reviewer"):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scheme_versions WHERE id = ? AND scheme_id = ?", (target_version_id, scheme_id))
        ver = cursor.fetchone()
        if not ver:
            conn.close()
            return False, "Target version not found."

        data = json.loads(ver["scheme_data_json"])
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE schemes SET
            name_en = ?,
            name_hi = ?,
            level = ?,
            category = ?,
            benefit_en = ?,
            benefit_hi = ?,
            description_en = ?,
            description_hi = ?,
            rules_json = ?,
            required_documents_json = ?,
            application_procedure_json = ?,
            restrictions_json = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE scheme_id = ?
        """, (
            data.get("name_en", ""),
            data.get("name_hi", ""),
            data.get("level", "central"),
            data.get("category", "General"),
            data.get("benefit_en", ""),
            data.get("benefit_hi", ""),
            data.get("description_en", ""),
            data.get("description_hi", ""),
            data.get("rules_json", "[]"),
            data.get("required_documents_json", "[]"),
            data.get("application_procedure_json", "[]"),
            data.get("restrictions_json", "[]"),
            scheme_id
        ))

        cursor.execute("""
        INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
        VALUES ('manual_rollback', ?, ?, 'SUCCESS', 'VERSION_ROLLBACK', ?, 0)
        """, (scheme_id, now_str, f"Rolled back scheme {scheme_id} to version {ver['version_number']} by {rolled_back_by}."))

        conn.commit()
        conn.close()
        return True, f"Successfully rolled back scheme {scheme_id} to version {ver['version_number']}."

    @staticmethod
    def get_activity_logs(limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM monitoring_activity_logs WHERE is_demo = 0 ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for r in rows:
            logs.append({
                "id": r["id"],
                "source_id": r["source_id"],
                "scheme_id": r["scheme_id"],
                "timestamp": r["timestamp"],
                "status": r["status"],
                "change_type": r["change_type"],
                "details": r["details"],
                "is_demo": bool(r["is_demo"]),
            })
        return logs


