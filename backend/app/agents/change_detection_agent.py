import uuid
import hashlib
import difflib
import logging
from typing import Dict, Any, Optional

from .models import SourceSnapshot, ChangeDetectionStatus, AgentStatus
from .repository import AgentRepository

logger = logging.getLogger("change_detection_agent")

class ChangeDetectionAgent:
    """
    Agent 3: Change Detection Agent
    Computes cryptographic SHA-256 content hashes, compares against historical snapshots,
    and isolates changed sections with textual diffing.
    """

    @staticmethod
    def normalize_content(text: str) -> str:
        """
        Normalizes text to eliminate spurious diffs from non-semantic whitespace.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    @staticmethod
    def compute_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_diff_summary(self, old_text: str, new_text: str, max_lines: int = 15) -> str:
        """
        Generates a readable diff summary showing modified lines.
        """
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="previous_snapshot",
            tofile="current_snapshot",
            lineterm=""
        ))
        if not diff:
            return "No textual differences detected."
        return "\n".join(diff[:max_lines])

    def detect_changes(self, crawl_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares crawl result against latest snapshot and records a new snapshot.
        """
        source_id = crawl_result["source_id"]
        raw_text = crawl_result.get("raw_text", "")
        doc_type = crawl_result.get("document_type", "HTML")
        status_in = crawl_result.get("status", "failed")

        if status_in != "success" or not raw_text:
            return {
                "source_id": source_id,
                "status": ChangeDetectionStatus.FETCH_FAILED,
                "has_change": False,
                "current_hash": "",
                "previous_hash": "",
                "snapshot_id": None,
                "diff_summary": "Fetch failed or empty content."
            }

        normalized = self.normalize_content(raw_text)
        current_hash = self.compute_sha256(normalized)

        prev_snapshot = AgentRepository.get_latest_snapshot(source_id)

        if not prev_snapshot:
            detection_status = ChangeDetectionStatus.NEW_SOURCE
            has_change = True
            diff_summary = "Initial snapshot captured. New source discovered."
            prev_id = None
            prev_hash = ""
        elif prev_snapshot.content_hash == current_hash:
            detection_status = ChangeDetectionStatus.NO_CHANGE
            has_change = False
            diff_summary = "Content identical to previous snapshot."
            prev_id = prev_snapshot.id
            prev_hash = prev_snapshot.content_hash
        else:
            detection_status = ChangeDetectionStatus.CONTENT_CHANGED
            has_change = True
            diff_summary = self.generate_diff_summary(prev_snapshot.extracted_content, normalized)
            prev_id = prev_snapshot.id
            prev_hash = prev_snapshot.content_hash

        # Create new snapshot in database
        snapshot_id = f"snp-{uuid.uuid4().hex[:10]}"
        new_snapshot = SourceSnapshot(
            id=snapshot_id,
            source_id=source_id,
            content_hash=current_hash,
            extracted_content=normalized,
            retrieved_at=AgentRepository.now_iso(),
            document_type=doc_type,
            previous_snapshot_id=prev_id
        )
        AgentRepository.create_snapshot(new_snapshot)

        return {
            "source_id": source_id,
            "status": detection_status,
            "has_change": has_change,
            "current_hash": current_hash,
            "previous_hash": prev_hash,
            "snapshot_id": snapshot_id,
            "diff_summary": diff_summary
        }
