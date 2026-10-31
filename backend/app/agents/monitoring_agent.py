import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .models import AgentStatus, SourceStatus, ChangeDetectionStatus, ChangeType
from .repository import AgentRepository
from .crawling_agent import CrawlingAgent
from .change_detection_agent import ChangeDetectionAgent
from .information_extraction_agent import InformationExtractionAgent
from .classification_agent import ClassificationAgent
from .evidence_validation_agent import EvidenceValidationAgent
from .policy_review_gate import PolicyReviewGate
from ..services.scheme_service import scheme_service

logger = logging.getLogger("monitoring_agent")

class MonitoringAgent:
    """
    Agent 9: Monitoring Agent
    Coordinates periodic re-crawling, change detection, extraction, classification,
    and policy review routing across tracked government scheme portals.
    """

    def __init__(self):
        self.crawler = CrawlingAgent()
        self.change_detector = ChangeDetectionAgent()
        self.extractor = InformationExtractionAgent()
        self.classifier = ClassificationAgent()
        self.validator = EvidenceValidationAgent()
        self.policy_gate = PolicyReviewGate()

    def run_monitoring_cycle(self, source_ids: Optional[List[str]] = None, max_sources: int = 10) -> Dict[str, Any]:
        """
        Executes a complete monitoring cycle over active sources.
        """
        run_id = f"run-mon-{uuid.uuid4().hex[:8]}"
        AgentRepository.record_run_start(
            run_id,
            "monitoring_agent",
            f"Running monitoring cycle (max_sources={max_sources})"
        )

        all_sources = AgentRepository.get_all_sources(limit=5000 if source_ids else max_sources)
        if source_ids:
            target_sources = [s for s in all_sources if s.id in source_ids]
        else:
            target_sources = all_sources[:max_sources]

        if not target_sources:
            summary = "No sources available to monitor."
            AgentRepository.record_run_completion(run_id, AgentStatus.COMPLETED, summary)
            return {"run_id": run_id, "summary": summary, "processed_sources": 0, "detected_changes": 0}

        processed_count = 0
        detected_changes = 0
        pending_updates_created = 0

        # Pre-fetch existing schemes for classification
        # Match only catalog entries that passed SchemeService validation.
        existing_schemes = [scheme.model_dump() for scheme in scheme_service.get_all_schemes()]
        scheme_map = {s["id"]: s for s in existing_schemes}
        scheme_name_map = {s["name_en"].lower(): s for s in existing_schemes}

        for source in target_sources:
            try:
                processed_count += 1
                logger.info(f"Monitoring source: {source.url}")

                # 1. Crawl
                crawl_res = self.crawler.crawl_source(source)
                if crawl_res["status"] != "success":
                    continue

                # 2. Change Detection
                det_res = self.change_detector.detect_changes(crawl_res)
                if not det_res["has_change"]:
                    continue

                detected_changes += 1

                # 3. Information Extraction
                extracted = self.extractor.extract_and_store(
                    source_id=source.id,
                    source_url=source.url,
                    text=crawl_res["raw_text"]
                )
                if not extracted:
                    continue

                # 4. Evidence Validation
                val_res = self.validator.validate_evidence(
                    extracted=extracted,
                    raw_text=crawl_res["raw_text"],
                    source_url=source.url
                )

                # 5. Classification
                # Check if scheme already exists
                matched_scheme = scheme_name_map.get(extracted.scheme_name.lower())
                change_types = self.classifier.classify(matched_scheme, extracted)

                # 6. Policy Review Gate
                target_scheme_id = matched_scheme["id"] if matched_scheme else f"scheme_{uuid.uuid4().hex[:8]}"
                for ct in change_types:
                    old_val = None
                    if matched_scheme:
                        if ct == ChangeType.BENEFIT_CHANGE:
                            old_val = matched_scheme.get("benefit_en")
                        elif ct == ChangeType.ELIGIBILITY_CHANGE:
                            old_val = str(matched_scheme.get("rules"))
                        elif ct == ChangeType.DOCUMENT_CHANGE:
                            old_val = json.dumps(matched_scheme.get("required_documents") or [], ensure_ascii=False)
                        elif ct == ChangeType.APPLICATION_PROCESS_CHANGE:
                            old_val = json.dumps(matched_scheme.get("application_procedure") or [], ensure_ascii=False)
                    if ct == ChangeType.BENEFIT_CHANGE:
                        new_val = extracted.benefits
                    elif ct == ChangeType.ELIGIBILITY_CHANGE:
                        new_val = json.dumps(extracted.eligibility_conditions, ensure_ascii=False)
                    elif ct == ChangeType.DOCUMENT_CHANGE:
                        new_val = json.dumps(extracted.required_documents, ensure_ascii=False)
                    elif ct == ChangeType.APPLICATION_PROCESS_CHANGE:
                        new_val = json.dumps(extracted.application_process, ensure_ascii=False)
                    elif ct == ChangeType.DEADLINE_CHANGE:
                        new_val = extracted.deadline
                    else:
                        new_val = json.dumps(extracted.model_dump(exclude_none=True), ensure_ascii=False)
                    if ct == ChangeType.NEW_SCHEME:
                        target_scheme_id = "disc-" + uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            f"{source.id}:{extracted.scheme_name.casefold()}"
                        ).hex[:24]
                        new_val = extracted.scheme_name

                    self.policy_gate.submit_for_review(
                        scheme_id=target_scheme_id,
                        change_type=ct,
                        old_value=old_val,
                        proposed_value=new_val,
                        evidence={
                            "verified_evidence": val_res["verified_evidence"],
                            "unverified_claims": val_res["unverified_claims"],
                            "validation_reason": val_res["reason"],
                            "source_url": crawl_res["url"],
                            "diff_summary": det_res["diff_summary"],
                        },
                        source_url=source.url,
                        confidence=val_res["confidence"]
                    )
                    pending_updates_created += 1

            except Exception as src_err:
                logger.warning(f"Error during monitoring of source {source.id}: {src_err}")

        summary = (
            f"Monitoring cycle completed: {processed_count} sources checked, "
            f"{detected_changes} changes detected, {pending_updates_created} proposed updates logged."
        )
        AgentRepository.record_run_completion(run_id, AgentStatus.COMPLETED, summary)

        return {
            "run_id": run_id,
            "summary": summary,
            "processed_sources": processed_count,
            "detected_changes": detected_changes,
            "pending_updates": pending_updates_created
        }
