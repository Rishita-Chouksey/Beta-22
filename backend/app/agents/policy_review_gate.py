import uuid
import logging
from typing import Dict, Any, List, Optional

from .models import ProposedUpdate, ChangeType, ReviewStatus, ExtractedSchemeData
from .repository import AgentRepository

logger = logging.getLogger("policy_review_gate")

CRITICAL_CHANGE_TYPES = {
    ChangeType.NEW_SCHEME,
    ChangeType.ELIGIBILITY_CHANGE,
    ChangeType.BENEFIT_CHANGE,
    ChangeType.DOCUMENT_CHANGE,
    ChangeType.DEADLINE_CHANGE,
    ChangeType.APPLICATION_PROCESS_CHANGE
}

class PolicyReviewGate:
    """
    Agent 7: Policy Review Gate
    Human-in-the-loop governance mechanism ensuring that changes affecting citizen
    eligibility, benefits, documents, or new schemes require explicit administrative approval.
    """

    def submit_for_review(
        self,
        scheme_id: str,
        change_type: ChangeType,
        old_value: Optional[str],
        proposed_value: str,
        evidence: Dict[str, Any],
        source_url: str,
        confidence: float
    ) -> ProposedUpdate:
        """
        Creates a pending update record requiring human review.
        """
        update_id = f"upd-{uuid.uuid4().hex[:10]}"
        now = AgentRepository.now_iso()

        update = ProposedUpdate(
            id=update_id,
            scheme_id=scheme_id,
            change_type=change_type,
            old_value=old_value,
            proposed_value=proposed_value,
            evidence=evidence,
            source_url=source_url,
            confidence=confidence,
            review_status=ReviewStatus.PENDING,
            created_at=now
        )
        AgentRepository.create_proposed_update(update)
        logger.info(f"ProposedUpdate {update_id} submitted for scheme {scheme_id} ({change_type.value})")
        return update

    def approve_update(self, update_id: str) -> Dict[str, Any]:
        """
        Marks update as APPROVED in the database.
        """
        existing = AgentRepository.get_proposed_update_by_id(update_id)
        if not existing:
            return {"success": False, "error": f"Update ID {update_id} not found."}

        now = AgentRepository.now_iso()
        AgentRepository.update_proposed_update_status(update_id, ReviewStatus.APPROVED, reviewed_at=now)
        logger.info(f"Update {update_id} approved.")
        return {"success": True, "update_id": update_id, "status": ReviewStatus.APPROVED.value}

    def reject_update(self, update_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Marks update as REJECTED in the database.
        """
        existing = AgentRepository.get_proposed_update_by_id(update_id)
        if not existing:
            return {"success": False, "error": f"Update ID {update_id} not found."}

        now = AgentRepository.now_iso()
        AgentRepository.update_proposed_update_status(update_id, ReviewStatus.REJECTED, reviewed_at=now)
        logger.info(f"Update {update_id} rejected. Reason: {reason}")
        return {"success": True, "update_id": update_id, "status": ReviewStatus.REJECTED.value, "reason": reason}
