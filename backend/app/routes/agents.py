import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field

from ..agents.orchestrator import orchestrator
from ..agents.repository import AgentRepository
from ..agents.models import ReviewStatus, SourceStatus, SourceItem, ProposedUpdate
from ..admin_auth import require_admin, require_admin_csrf

logger = logging.getLogger("routes_agents")

router = APIRouter(dependencies=[Depends(require_admin)])

# Request Models
class DiscoverRequest(BaseModel):
    seeds: Optional[List[str]] = Field(None, description="Optional custom seed URLs. Defaults to myScheme public pages.")
    max_links_per_seed: int = Field(15, ge=1, le=50, description="Max government links to discover per seed")

class CrawlRequest(BaseModel):
    source_ids: Optional[List[str]] = Field(None, description="Optional list of specific source IDs to crawl")
    max_sources: int = Field(10, ge=1, le=50, description="Max sources to crawl")

class MonitorRequest(BaseModel):
    source_ids: Optional[List[str]] = Field(None, description="Optional list of specific source IDs to monitor")
    max_sources: int = Field(10, ge=1, le=50, description="Max sources to check")

class ApproveRequest(BaseModel):
    reason: Optional[str] = Field("Approved after verifying against official notification.", description="Audit rationale")

class RejectRequest(BaseModel):
    reason: str = Field(..., description="Audit rationale for rejection")

# 1. Agents Live Status & Runs
@router.get("/agents/status")
async def get_agents_status():
    """
    Returns live status of all 9 specialized agents:
    SourceDiscovery, Crawling, ChangeDetection, InformationExtraction,
    Classification, EvidenceValidation, PolicyReviewGate, PublishingService, Monitoring.
    """
    statuses = orchestrator.get_agent_statuses()
    return {
        "success": True,
        "agents": statuses
    }

@router.get("/agents/runs")
async def get_agent_runs(limit: int = Query(50, ge=1, le=200)):
    """
    Returns chronological audit history of agent runs.
    """
    runs = orchestrator.get_agent_runs(limit=limit)
    return {
        "success": True,
        "count": len(runs),
        "runs": runs
    }

# 2. Trigger Actions
@router.post("/agents/discover", dependencies=[Depends(require_admin_csrf)])
async def trigger_source_discovery(req: Optional[DiscoverRequest] = Body(None)):
    """
    Triggers Agent 1 (Source Discovery) on myScheme public pages when an administrator requests it.
    """
    seeds = req.seeds if req else None
    max_links = req.max_links_per_seed if req else 15
    res = orchestrator.discover_sources(seeds=seeds, max_links_per_seed=max_links)
    return res

@router.post("/agents/crawl", dependencies=[Depends(require_admin_csrf)])
async def trigger_source_crawling(req: Optional[CrawlRequest] = Body(None)):
    """
    Triggers Agent 2 (Crawling) across discovered government pages and PDF circulars.
    """
    src_ids = req.source_ids if req else None
    max_src = req.max_sources if req else 10
    res = orchestrator.crawl_sources(source_ids=src_ids, max_sources=max_src)
    return res

@router.post("/agents/monitor", dependencies=[Depends(require_admin_csrf)])
async def trigger_monitoring_cycle(req: Optional[MonitorRequest] = Body(None)):
    """
    Triggers Agent 9 (Monitoring Pipeline): Crawl -> Change Detection -> Extraction -> Classification -> Validation -> Policy Review Gate.
    """
    src_ids = req.source_ids if req else None
    max_src = req.max_sources if req else 10
    res = orchestrator.run_monitoring_cycle(source_ids=src_ids, max_sources=max_src)
    return res

# 3. Sources Endpoints
@router.get("/sources")
async def list_sources(
    status: Optional[str] = Query(None, description="Filter by status: discovered, crawled, failed, degraded"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Lists all tracked public government sources, their domains, types, and crawl health.
    """
    sources = AgentRepository.get_all_sources(status=status, limit=limit)
    return {
        "success": True,
        "count": len(sources),
        "sources": [s.model_dump() for s in sources]
    }

@router.get("/sources/{source_id}")
async def get_source_detail(source_id: str):
    """
    Detailed source view including latest snapshot and raw extracted content.
    """
    source = AgentRepository.get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found.")

    latest_snapshot = AgentRepository.get_latest_snapshot(source_id)

    return {
        "success": True,
        "source": source.model_dump(),
        "latest_snapshot": latest_snapshot.model_dump() if latest_snapshot else None
    }

# 4. Proposed Updates & Policy Review Gate
@router.get("/updates")
async def list_proposed_updates(
    status: Optional[str] = Query(None, description="Filter by review status: PENDING, APPROVED, REJECTED")
):
    """
    Lists proposed scheme updates requiring human review or previously reviewed.
    """
    updates = AgentRepository.get_all_proposed_updates(review_status=status)
    return {
        "success": True,
        "count": len(updates),
        "updates": [u.model_dump() for u in updates]
    }

@router.get("/updates/{update_id}")
async def get_proposed_update_detail(update_id: str):
    """
    Detailed view of a proposed update with change classification, old vs new values, and evidence excerpts.
    """
    update = AgentRepository.get_proposed_update_by_id(update_id)
    if not update:
        raise HTTPException(status_code=404, detail=f"Proposed update {update_id} not found.")
    return {
        "success": True,
        "update": update.model_dump()
    }

@router.post("/updates/{update_id}/approve")
async def approve_proposed_update(update_id: str, req: Optional[ApproveRequest] = Body(None),
                                 _authorized=Depends(require_admin_csrf)):
    """
    Approves proposed update, commits change to active catalog, and stores immutable scheme version.
    """
    res = orchestrator.approve_update(
        update_id,
        reviewer_name=_authorized["sub"],
        reason=req.reason if req else "Approved after verifying against official notification."
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error") or "Failed to approve and publish update.")
    return {
        "success": True,
        "message": f"Update {update_id} successfully approved and published.",
        "result": res
    }

@router.post("/updates/{update_id}/reject")
async def reject_proposed_update(update_id: str, req: RejectRequest,
                                 _authorized=Depends(require_admin_csrf)):
    """
    Rejects proposed update with mandatory audit rationale.
    """
    res = orchestrator.reject_update(update_id, reason=req.reason,
                                     reviewer_name=_authorized["sub"])
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error") or "Failed to reject update.")
    return {
        "success": True,
        "message": f"Update {update_id} rejected.",
        "result": res
    }

# 5. Version History & Monitoring Overview
@router.get("/schemes/{scheme_id}/versions")
async def get_scheme_versions(scheme_id: str):
    """
    Retrieves full version history and audit snapshots for a scheme.
    """
    versions = AgentRepository.get_scheme_versions(scheme_id)
    return {
        "success": True,
        "scheme_id": scheme_id,
        "count": len(versions),
        "versions": [v.model_dump() for v in versions]
    }

@router.get("/monitoring/status")
async def get_monitoring_overview():
    """
    High-level overview metrics: total sources, active monitors, schemes discovered, pending updates.
    """
    overview = orchestrator.get_monitoring_overview()
    return {
        "success": True,
        "overview": overview
    }
