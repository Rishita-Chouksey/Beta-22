import json
import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from ..db.database import get_db_connection
from .models import (
    SourceItem,
    SourceSnapshot,
    DiscoveredScheme,
    ProposedUpdate,
    SchemeVersion,
    AgentRunRecord,
    SourceStatus,
    SourceType,
    ChangeType,
    ReviewStatus,
    AgentStatus
)

logger = logging.getLogger("agent_repository")

class AgentRepository:
    """
    Database repository implementing Section 5 schema requirements for the
    lightweight multi-agent scheme discovery and monitoring system.
    """

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- Sources ---
    @staticmethod
    def add_or_update_source(source: SourceItem) -> SourceItem:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        created_at = source.created_at or now

        # URLs are the source identity. Reuse an existing row if discovery found
        # the same URL under a different generated ID.
        cursor.execute("SELECT id FROM sources WHERE url = ?", (source.url,))
        existing = cursor.fetchone()
        if existing and existing["id"] != source.id:
            source.id = existing["id"]

        cursor.execute("""
        INSERT INTO sources (id, url, domain, source_type, discovered_from, status, last_checked_at, last_successful_fetch_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            url = excluded.url,
            domain = excluded.domain,
            source_type = excluded.source_type,
            discovered_from = COALESCE(sources.discovered_from, excluded.discovered_from),
            status = excluded.status,
            last_checked_at = excluded.last_checked_at,
            last_successful_fetch_at = COALESCE(excluded.last_successful_fetch_at, sources.last_successful_fetch_at)
        """, (
            source.id,
            source.url,
            source.domain,
            source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
            source.discovered_from,
            source.status.value if hasattr(source.status, 'value') else str(source.status),
            source.last_checked_at,
            source.last_successful_fetch_at,
            created_at
        ))
        conn.commit()
        conn.close()
        return source

    @staticmethod
    def get_source_by_id(source_id: str) -> Optional[SourceItem]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return SourceItem(
            id=row["id"],
            url=row["url"],
            domain=row["domain"],
            source_type=SourceType(row["source_type"]),
            discovered_from=row["discovered_from"],
            status=SourceStatus(row["status"]),
            last_checked_at=row["last_checked_at"],
            last_successful_fetch_at=row["last_successful_fetch_at"],
            created_at=row["created_at"]
        )

    @staticmethod
    def get_source_by_url(url: str) -> Optional[SourceItem]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sources WHERE url = ?", (url,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return SourceItem(
            id=row["id"],
            url=row["url"],
            domain=row["domain"],
            source_type=SourceType(row["source_type"]),
            discovered_from=row["discovered_from"],
            status=SourceStatus(row["status"]),
            last_checked_at=row["last_checked_at"],
            last_successful_fetch_at=row["last_successful_fetch_at"],
            created_at=row["created_at"]
        )

    @staticmethod
    def get_all_sources(status: Optional[str] = None, limit: int = 100) -> List[SourceItem]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM sources WHERE status = ? ORDER BY created_at DESC LIMIT ?", (status, limit))
        else:
            cursor.execute("SELECT * FROM sources WHERE status != 'disabled' ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            try:
                st = SourceType(r["source_type"])
            except Exception:
                st = SourceType.HTML
            try:
                ss = SourceStatus(r["status"])
            except Exception:
                ss = SourceStatus.DISCOVERED
            results.append(SourceItem(
                id=r["id"],
                url=r["url"],
                domain=r["domain"],
                source_type=st,
                discovered_from=r["discovered_from"],
                status=ss,
                last_checked_at=r["last_checked_at"],
                last_successful_fetch_at=r["last_successful_fetch_at"],
                created_at=r["created_at"]
            ))
        return results

    @staticmethod
    def update_source_status(source_id: str, status: SourceStatus, last_checked_at: str, last_successful_fetch_at: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        if last_successful_fetch_at:
            cursor.execute("""
            UPDATE sources SET status = ?, last_checked_at = ?, last_successful_fetch_at = ? WHERE id = ?
            """, (status.value, last_checked_at, last_successful_fetch_at, source_id))
        else:
            cursor.execute("""
            UPDATE sources SET status = ?, last_checked_at = ? WHERE id = ?
            """, (status.value, last_checked_at, source_id))
        conn.commit()
        conn.close()

    # --- Snapshots ---
    @staticmethod
    def create_snapshot(snapshot: SourceSnapshot) -> SourceSnapshot:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        retrieved_at = snapshot.retrieved_at or now

        cursor.execute("""
        INSERT INTO source_snapshots (id, source_id, content_hash, extracted_content, retrieved_at, document_type, previous_snapshot_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.id,
            snapshot.source_id,
            snapshot.content_hash,
            snapshot.extracted_content,
            retrieved_at,
            snapshot.document_type,
            snapshot.previous_snapshot_id
        ))
        conn.commit()
        conn.close()
        return snapshot

    @staticmethod
    def get_latest_snapshot(source_id: str) -> Optional[SourceSnapshot]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM source_snapshots WHERE source_id = ? ORDER BY retrieved_at DESC LIMIT 1
        """, (source_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return SourceSnapshot(
            id=row["id"],
            source_id=row["source_id"],
            content_hash=row["content_hash"],
            extracted_content=row["extracted_content"],
            retrieved_at=row["retrieved_at"],
            document_type=row["document_type"],
            previous_snapshot_id=row["previous_snapshot_id"]
        )

    # --- Discovered Schemes ---
    @staticmethod
    def add_or_update_discovered_scheme(scheme: DiscoveredScheme) -> DiscoveredScheme:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        first_disc = scheme.first_discovered_at or now
        last_upd = scheme.last_updated_at or now

        cursor.execute("""
        INSERT INTO discovered_schemes (id, scheme_name, department, state, source_id, source_url, extracted_data, verification_status, first_discovered_at, last_updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            scheme_name = excluded.scheme_name,
            department = excluded.department,
            state = excluded.state,
            extracted_data = excluded.extracted_data,
            verification_status = excluded.verification_status,
            last_updated_at = excluded.last_updated_at
        """, (
            scheme.id,
            scheme.scheme_name,
            scheme.department,
            scheme.state,
            scheme.source_id,
            scheme.source_url,
            json.dumps(scheme.extracted_data, ensure_ascii=False),
            scheme.verification_status,
            first_disc,
            last_upd
        ))
        conn.commit()
        conn.close()
        return scheme

    @staticmethod
    def get_discovered_scheme_by_id(scheme_id: str) -> Optional[DiscoveredScheme]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM discovered_schemes WHERE id = ?", (scheme_id,))
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        return DiscoveredScheme(
            id=r["id"],
            scheme_name=r["scheme_name"],
            department=r["department"],
            state=r["state"],
            source_id=r["source_id"],
            source_url=r["source_url"],
            extracted_data=json.loads(r["extracted_data"]) if r["extracted_data"] else {},
            verification_status=r["verification_status"],
            first_discovered_at=r["first_discovered_at"],
            last_updated_at=r["last_updated_at"]
        )

    @staticmethod
    def get_all_discovered_schemes(status: Optional[str] = None) -> List[DiscoveredScheme]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM discovered_schemes WHERE verification_status = ? ORDER BY last_updated_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM discovered_schemes ORDER BY last_updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        res = []
        for r in rows:
            res.append(DiscoveredScheme(
                id=r["id"],
                scheme_name=r["scheme_name"],
                department=r["department"],
                state=r["state"],
                source_id=r["source_id"],
                source_url=r["source_url"],
                extracted_data=json.loads(r["extracted_data"]) if r["extracted_data"] else {},
                verification_status=r["verification_status"],
                first_discovered_at=r["first_discovered_at"],
                last_updated_at=r["last_updated_at"]
            ))
        return res

    # --- Proposed Updates ---
    @staticmethod
    def create_proposed_update(update: ProposedUpdate) -> ProposedUpdate:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        created_at = update.created_at or now

        cursor.execute("""
        INSERT INTO proposed_updates (id, scheme_id, change_type, old_value, proposed_value, evidence, source_url, confidence, review_status, created_at, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            proposed_value = excluded.proposed_value,
            evidence = excluded.evidence,
            confidence = excluded.confidence,
            review_status = excluded.review_status,
            reviewed_at = excluded.reviewed_at
        """, (
            update.id,
            update.scheme_id,
            update.change_type.value if hasattr(update.change_type, 'value') else str(update.change_type),
            update.old_value,
            update.proposed_value,
            json.dumps(update.evidence, ensure_ascii=False) if update.evidence else None,
            update.source_url,
            update.confidence,
            update.review_status.value if hasattr(update.review_status, 'value') else str(update.review_status),
            created_at,
            update.reviewed_at
        ))
        conn.commit()
        conn.close()
        return update

    @staticmethod
    def get_proposed_update_by_id(update_id: str) -> Optional[ProposedUpdate]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proposed_updates WHERE id = ?", (update_id,))
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        try:
            ev = json.loads(r["evidence"]) if r["evidence"] else None
        except Exception:
            ev = {"raw": r["evidence"]}
        return ProposedUpdate(
            id=r["id"],
            scheme_id=r["scheme_id"],
            change_type=ChangeType(r["change_type"]),
            old_value=r["old_value"],
            proposed_value=r["proposed_value"],
            evidence=ev,
            source_url=r["source_url"],
            confidence=float(r["confidence"]) if r["confidence"] is not None else 0.85,
            review_status=ReviewStatus(r["review_status"]),
            created_at=r["created_at"],
            reviewed_at=r["reviewed_at"],
            reviewed_by=r["reviewed_by"],
            review_reason=r["review_reason"]
        )

    @staticmethod
    def get_all_proposed_updates(review_status: Optional[str] = None) -> List[ProposedUpdate]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if review_status:
            cursor.execute("SELECT * FROM proposed_updates WHERE review_status = ? ORDER BY created_at DESC", (review_status,))
        else:
            cursor.execute("SELECT * FROM proposed_updates ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        updates = []
        for r in rows:
            try:
                ev = json.loads(r["evidence"]) if r["evidence"] else None
            except Exception:
                ev = {"raw": r["evidence"]}
            try:
                ct = ChangeType(r["change_type"])
            except Exception:
                ct = ChangeType.GUIDELINE_UPDATE
            try:
                rs = ReviewStatus(r["review_status"])
            except Exception:
                rs = ReviewStatus.PENDING

            updates.append(ProposedUpdate(
                id=r["id"],
                scheme_id=r["scheme_id"],
                change_type=ct,
                old_value=r["old_value"],
                proposed_value=r["proposed_value"],
                evidence=ev,
                source_url=r["source_url"],
                confidence=float(r["confidence"]) if r["confidence"] is not None else 0.85,
                review_status=rs,
                created_at=r["created_at"],
                reviewed_at=r["reviewed_at"],
                reviewed_by=r["reviewed_by"],
                review_reason=r["review_reason"]
            ))
        return updates

    @staticmethod
    def update_proposed_update_status(update_id: str, status: ReviewStatus, reviewed_at: Optional[str] = None,
                                      reviewed_by: Optional[str] = None, review_reason: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        ts = reviewed_at or AgentRepository.now_iso()
        cursor.execute("""
        UPDATE proposed_updates SET review_status = ?, reviewed_at = ?, reviewed_by = ?, review_reason = ? WHERE id = ?
        """, (status.value, ts, reviewed_by, review_reason, update_id))
        conn.commit()
        conn.close()

    # --- Scheme Versions ---
    @staticmethod
    def save_scheme_version(version: SchemeVersion) -> SchemeVersion:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        created_at = version.created_at or now

        # Also populate scheme_data_json if table was created with older schema
        data_json = json.dumps(version.scheme_data, ensure_ascii=False)

        cursor.execute("""
        INSERT INTO scheme_versions (scheme_id, version_number, scheme_data, scheme_data_json, source_url, approval_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            version.scheme_id,
            version.version_number,
            data_json,
            data_json,
            version.source_url,
            version.approval_status,
            created_at
        ))
        v_id = cursor.lastrowid
        conn.commit()
        conn.close()
        version.id = v_id
        return version

    @staticmethod
    def get_scheme_versions(scheme_id: str) -> List[SchemeVersion]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM scheme_versions WHERE scheme_id = ? ORDER BY version_number DESC
        """, (scheme_id,))
        rows = cursor.fetchall()
        conn.close()

        versions = []
        for r in rows:
            raw_data = r["scheme_data"] if "scheme_data" in r.keys() and r["scheme_data"] else r["scheme_data_json"]
            try:
                sdata = json.loads(raw_data) if raw_data else {}
            except Exception:
                sdata = {}
            source_url = r["source_url"] if "source_url" in r.keys() else None
            appr_status = r["approval_status"] if "approval_status" in r.keys() else "APPROVED"

            versions.append(SchemeVersion(
                id=r["id"],
                scheme_id=r["scheme_id"],
                version_number=r["version_number"],
                scheme_data=sdata,
                source_url=source_url,
                approval_status=appr_status,
                created_at=r["created_at"]
            ))
        return versions

    @staticmethod
    def get_latest_version_number(scheme_id: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version_number) FROM scheme_versions WHERE scheme_id = ?", (scheme_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if (row and row[0] is not None) else 0

    # --- Agent Runs ---
    @staticmethod
    def record_run_start(run_id: str, agent_name: str, input_summary: str) -> AgentRunRecord:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        cursor.execute("""
        INSERT INTO agent_runs (id, agent_name, status, input_summary, started_at)
        VALUES (?, ?, ?, ?, ?)
        """, (run_id, agent_name, AgentStatus.RUNNING.value, input_summary, now))
        conn.commit()
        conn.close()
        return AgentRunRecord(
            id=run_id,
            agent_name=agent_name,
            status=AgentStatus.RUNNING,
            input_summary=input_summary,
            started_at=now
        )

    @staticmethod
    def record_run_completion(run_id: str, status: AgentStatus, output_summary: str, error_message: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = AgentRepository.now_iso()
        cursor.execute("""
        UPDATE agent_runs SET status = ?, output_summary = ?, error_message = ?, completed_at = ? WHERE id = ?
        """, (status.value, output_summary, error_message, now, run_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_agent_runs(limit: int = 50) -> List[AgentRunRecord]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        records = []
        for r in rows:
            try:
                st = AgentStatus(r["status"])
            except Exception:
                st = AgentStatus.COMPLETED
            records.append(AgentRunRecord(
                id=r["id"],
                agent_name=r["agent_name"],
                status=st,
                input_summary=r["input_summary"],
                output_summary=r["output_summary"],
                error_message=r["error_message"],
                started_at=r["started_at"],
                completed_at=r["completed_at"]
            ))
        return records

    @staticmethod
    def get_agent_status_map() -> Dict[str, Dict[str, Any]]:
        """Returns the live status of all 9 specialized agents."""
        conn = get_db_connection()
        cursor = conn.cursor()
        all_agents = [
            "source_discovery",
            "crawling",
            "change_detection",
            "information_extraction",
            "classification",
            "evidence_validation",
            "policy_review_gate",
            "publishing_service",
            "monitoring_agent"
        ]

        result = {}
        for ag in all_agents:
            cursor.execute("""
            SELECT status, started_at, completed_at, output_summary, error_message
            FROM agent_runs WHERE agent_name = ? ORDER BY started_at DESC LIMIT 1
            """, (ag,))
            row = cursor.fetchone()
            if row:
                result[ag] = {
                    "status": row["status"],
                    "last_run": row["completed_at"] or row["started_at"],
                    "output_summary": row["output_summary"],
                    "error_message": row["error_message"]
                }
            else:
                result[ag] = {
                    "status": AgentStatus.IDLE.value,
                    "last_run": None,
                    "output_summary": "Ready to execute",
                    "error_message": None
                }
        conn.close()
        return result

    @staticmethod
    def get_monitoring_overview() -> Dict[str, Any]:
        """Provides high-level numbers for Section 7.A Overview."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sources")
        total_sources = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sources WHERE status = 'crawled'")
        monitored_sources = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM discovered_schemes")
        discovered_schemes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM proposed_updates WHERE review_status = 'PENDING'")
        pending_updates = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM proposed_updates WHERE review_status = 'APPROVED'")
        approved_updates = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM agent_runs WHERE status = 'FAILED'")
        failed_runs = cursor.fetchone()[0]

        conn.close()
        return {
            "total_discovered_sources": total_sources,
            "successfully_monitored_sources": monitored_sources,
            "schemes_discovered": discovered_schemes,
            "pending_updates": pending_updates,
            "approved_updates": approved_updates,
            "failed_agent_runs": failed_runs
        }
