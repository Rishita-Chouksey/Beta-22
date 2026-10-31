import logging
from typing import Dict, Any, List, Optional

from .source_discovery_agent import SourceDiscoveryAgent, DEFAULT_SEEDS
from .crawling_agent import CrawlingAgent
from .change_detection_agent import ChangeDetectionAgent
from .information_extraction_agent import InformationExtractionAgent
from .classification_agent import ClassificationAgent
from .evidence_validation_agent import EvidenceValidationAgent
from .policy_review_gate import PolicyReviewGate
from .publishing_service import PublishingService
from .monitoring_agent import MonitoringAgent
from .repository import AgentRepository
from .models import SourceItem, SourceStatus, ReviewStatus

logger = logging.getLogger("agent_orchestrator")

class AgentOrchestrator:
    """
    Central Orchestrator coordinating all 9 specialized agents:
    1. SourceDiscoveryAgent
    2. CrawlingAgent
    3. ChangeDetectionAgent
    4. InformationExtractionAgent
    5. ClassificationAgent
    6. EvidenceValidationAgent
    7. PolicyReviewGate
    8. PublishingService
    9. MonitoringAgent
    """

    def __init__(self):
        self.source_discovery = SourceDiscoveryAgent()
        self.crawling = CrawlingAgent()
        self.change_detection = ChangeDetectionAgent()
        self.information_extraction = InformationExtractionAgent()
        self.classification = ClassificationAgent()
        self.evidence_validation = EvidenceValidationAgent()
        self.policy_review_gate = PolicyReviewGate()
        self.publishing_service = PublishingService()
        self.monitoring = MonitoringAgent()

    def discover_sources(self, seeds: Optional[List[str]] = None, max_links_per_seed: int = 15) -> Dict[str, Any]:
        """
        Executes Agent 1: Discovers official government portal links.
        """
        results = self.source_discovery.discover_sources(
            seed_urls=seeds or DEFAULT_SEEDS,
            max_links_per_seed=max_links_per_seed
        )
        return {
            "success": not self.source_discovery.last_errors or len(self.source_discovery.last_errors) < len(seeds or DEFAULT_SEEDS),
            "count": len(results),
            "sources": [s.model_dump() for s in results],
            "source_errors": self.source_discovery.last_errors
        }

    def crawl_sources(self, source_ids: Optional[List[str]] = None, max_sources: int = 10) -> Dict[str, Any]:
        """
        Executes Agent 2: Crawls government portals and documents.
        """
        all_sources = AgentRepository.get_all_sources(limit=5000 if source_ids else max_sources)
        if source_ids:
            target_sources = [s for s in all_sources if s.id in source_ids]
        else:
            target_sources = all_sources[:max_sources]

        crawl_results = self.crawling.crawl_sources(target_sources)
        return {
            "success": True,
            "count": len(crawl_results),
            "results": [
                {
                    "source_id": r["source_id"],
                    "url": r["url"],
                    "document_type": r["document_type"],
                    "status": r["status"],
                    "text_length": len(r.get("raw_text", "")),
                    "error": r.get("error")
                }
                for r in crawl_results
            ]
        }

    def run_monitoring_cycle(self, source_ids: Optional[List[str]] = None, max_sources: int = 10) -> Dict[str, Any]:
        """
        Executes Agent 9: Runs full end-to-end monitoring pipeline.
        """
        return self.monitoring.run_monitoring_cycle(source_ids=source_ids, max_sources=max_sources)

    def approve_update(self, update_id: str, reviewer_name: str = "Admin Officer", reason: str = "") -> Dict[str, Any]:
        """
        Policy Review Gate -> Publishing Service:
        Human approval causes the update to be published to the live catalog and versioned.
        """
        update = AgentRepository.get_proposed_update_by_id(update_id)
        if not update:
            return {"success": False, "error": f"Update ID {update_id} not found."}
        if update.review_status != ReviewStatus.PENDING:
            return {"success": False, "error": f"Update is already {update.review_status.value}."}
        review_result = self.policy_review_gate.approve_update(update_id, reviewer_name=reviewer_name, reason=reason)
        if not review_result.get("success"):
            return review_result

        # Auto-publish approved update
        publish_result = self.publishing_service.publish_approved_update(update_id)
        return {
            "success": bool(publish_result.get("success")),
            "review": review_result,
            "publishing": publish_result
        }

    def reject_update(self, update_id: str, reason: str = "", reviewer_name: str = "Admin Officer") -> Dict[str, Any]:
        """
        Policy Review Gate: Human rejects the proposed update.
        """
        return self.policy_review_gate.reject_update(update_id, reason=reason, reviewer_name=reviewer_name)

    def get_agent_statuses(self) -> Dict[str, Any]:
        """
        Returns live status of all 9 specialized agents.
        """
        return AgentRepository.get_agent_status_map()

    def get_agent_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns history of agent execution runs.
        """
        records = AgentRepository.get_agent_runs(limit=limit)
        return [r.model_dump() for r in records]

    def get_monitoring_overview(self) -> Dict[str, Any]:
        """
        Returns summary metrics for Admin Monitoring overview dashboard.
        """
        return AgentRepository.get_monitoring_overview()

# Global orchestrator singleton
orchestrator = AgentOrchestrator()
