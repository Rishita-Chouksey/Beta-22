import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import SourceDefinition, ChangeType, AccessibilityStatus
from .source_registry import SourceRegistry, OFFICIAL_SOURCE_CATALOG
from .crawler import OfficialSchemeCrawler
from .fingerprint import detect_meaningful_difference
from .change_analyzer import change_analyzer
from ..db.repository import MonitoringRepository
from ..db.database import get_db_connection

logger = logging.getLogger("monitor_service")

class SchemeMonitoringService:
    """
    Central Scheme Intelligence & Monitoring Orchestrator.
    Coordinates polite crawling, fingerprint comparison, Gemini diff analysis,
    and update lifecycle management while strictly preserving eligibility engine isolation.
    """

    def __init__(self):
        self.is_running = False
        self._last_run_time: Optional[str] = None

    async def run_monitoring_cycle(self, target_source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a scheduled or on-demand monitoring cycle across all official sources.
        Guarantees that a network failure or timeout on one portal does not stop others.
        """
        self.is_running = True
        start_ts = time.time()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._last_run_time = now_str

        sources_to_check = []
        # A manual catalogue is the data source now; never crawl sources that
        # are not explicitly authorized for automated monitoring.
        all_sources = [s for s in SourceRegistry.get_all_sources() if s.automated_monitoring_permitted]

        if target_source_id:
            sources_to_check = [s for s in all_sources if s.source_id == target_source_id]
        else:
            sources_to_check = all_sources

        total_checked = 0
        success_count = 0
        failed_count = 0
        changes_detected = 0
        results = []

        conn = get_db_connection()
        cursor = conn.cursor()

        for source in sources_to_check:
            total_checked += 1
            src_id = source.source_id
            official_url = source.official_url

            # Fetch existing stored hash and preview
            cursor.execute("SELECT content_hash, last_content_preview FROM monitoring_sources WHERE source_id = ?", (src_id,))
            row = cursor.fetchone()
            old_hash = row["content_hash"] if row and row["content_hash"] else None
            old_text = row["last_content_preview"] if row and row["last_content_preview"] else ""

            try:
                # 1. Fetch content respectfully
                new_text, new_hash, status, error_msg = await OfficialSchemeCrawler.fetch_source_content(source)

                if status == AccessibilityStatus.HEALTHY and new_text and new_hash:
                    success_count += 1

                    # 2. Check for content change
                    if old_hash and old_hash != new_hash:
                        # Detect if change is meaningful
                        is_meaningful, diff_summary = detect_meaningful_difference(old_text, new_text)

                        if is_meaningful:
                            changes_detected += 1
                            change_type = ChangeType.CONTENT_MODIFIED

                            # Run AI-assisted diff analysis
                            ai_analysis = await change_analyzer.analyze_diff(
                                scheme_id=source.target_scheme_ids[0] if source.target_scheme_ids else "scheme_update",
                                scheme_name=source.name,
                                source_url=official_url,
                                old_text=old_text,
                                new_text=new_text,
                                detected_summary=diff_summary
                            )

                            # Create pending update for target schemes
                            for target_scheme in source.target_scheme_ids:
                                update_id = f"upd_{target_scheme}_{int(time.time())}"
                                cursor.execute("""
                                INSERT INTO pending_scheme_updates (
                                    update_id, scheme_id, scheme_name_en, scheme_name_hi, source_id, source_url,
                                    detected_at, change_type, old_content_snippet, new_content_snippet,
                                    proposed_changes_json, ai_analysis_summary, status, is_demo
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0)
                                """, (
                                    update_id,
                                    target_scheme,
                                    source.name,
                                    source.name,
                                    src_id,
                                    official_url,
                                    now_str,
                                    change_type.value,
                                    old_text[:600],
                                    new_text[:600],
                                    "{}",
                                    ai_analysis.get("ai_summary", diff_summary)
                                ))

                            # Log change detection activity
                            cursor.execute("""
                            INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
                            VALUES (?, ?, ?, 'CHANGE_DETECTED', ?, ?, 0)
                            """, (src_id, source.target_scheme_ids[0] if source.target_scheme_ids else None, now_str, change_type.value, diff_summary[:400]))

                            # Update source record
                            cursor.execute("""
                            UPDATE monitoring_sources SET
                                content_hash = ?,
                                last_content_preview = ?,
                                last_successful_check = ?,
                                last_detected_change = ?,
                                accessibility_status = 'healthy',
                                error_details = NULL
                            WHERE source_id = ?
                            """, (new_hash, new_text[:2000], now_str, now_str, src_id))

                            results.append({"source_id": src_id, "status": "change_detected", "summary": diff_summary})
                        else:
                            # Insignificant whitespace/timestamp change -> record success with NO_CHANGE
                            cursor.execute("""
                            UPDATE monitoring_sources SET
                                last_successful_check = ?,
                                accessibility_status = 'healthy',
                                error_details = NULL
                            WHERE source_id = ?
                            """, (now_str, src_id))
                            results.append({"source_id": src_id, "status": "no_change", "summary": "Formatting/whitespace only"})
                    else:
                        # Initial baseline capture or identical hash
                        cursor.execute("""
                        UPDATE monitoring_sources SET
                            content_hash = ?,
                            last_content_preview = ?,
                            last_successful_check = ?,
                            accessibility_status = 'healthy',
                            error_details = NULL
                        WHERE source_id = ?
                        """, (new_hash, new_text[:2000], now_str, src_id))
                        results.append({"source_id": src_id, "status": "verified_unchanged", "summary": "Baseline matched"})

                else:
                    # Source failed or was unavailable
                    failed_count += 1
                    err_clean = error_msg or "Failed to connect to official server."
                    cursor.execute("""
                    UPDATE monitoring_sources SET
                        accessibility_status = ?,
                        error_details = ?
                    WHERE source_id = ?
                    """, (status.value, err_clean, src_id))

                    cursor.execute("""
                    INSERT INTO monitoring_activity_logs (source_id, scheme_id, timestamp, status, change_type, details, is_demo)
                    VALUES (?, NULL, ?, 'FAILED', 'SOURCE_UNAVAILABLE', ?, 0)
                    """, (src_id, now_str, err_clean))

                    results.append({"source_id": src_id, "status": status.value, "error": err_clean})

            except Exception as e:
                failed_count += 1
                logger.error(f"Error checking source {src_id}: {e}")
                results.append({"source_id": src_id, "status": "error", "error": str(e)})

        conn.commit()
        conn.close()

        self.is_running = False
        duration_ms = int((time.time() - start_ts) * 1000)

        return {
            "cycle_completed_at": now_str,
            "duration_ms": duration_ms,
            "total_sources_checked": total_checked,
            "success_count": success_count,
            "failed_count": failed_count,
            "changes_detected": changes_detected,
            "results": results
        }

monitor_service = SchemeMonitoringService()

