from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..admin_auth import require_admin, require_admin_csrf
from ..db.repository import MonitoringRepository
from ..monitoring.monitor_service import monitor_service
from ..monitoring.models import MonitoringSummary
from ..services.scheme_service import scheme_service

router = APIRouter(prefix="/admin/monitoring", tags=["Admin Scheme Monitoring"])

class ApproveUpdateRequest(BaseModel):
    reason: str = Field(..., description="Audit rationale for approving the scheme update")

class RejectUpdateRequest(BaseModel):
    reason: str = Field(..., description="Audit rationale for rejecting the scheme update")

class RollbackRequest(BaseModel):
    target_version_id: int = Field(..., description="ID of historical version to restore")

class RunMonitoringRequest(BaseModel):
    source_id: Optional[str] = Field(None, description="Optional single source ID to check, or None for all")

@router.get("/summary", response_model=MonitoringSummary)
async def get_monitoring_summary(_authorized=Depends(require_admin)):
    """Provides high-level system monitoring health and pending update counts."""
    summary = MonitoringRepository.get_monitoring_summary()
    return MonitoringSummary(**summary)

@router.get("/sources")
async def list_monitoring_sources(_authorized=Depends(require_admin)):
    """Lists all monitored official government portals, their category, and live health status."""
    return MonitoringRepository.get_all_sources()

@router.get("/changes")
async def list_activity_changes(
    limit: int = Query(50, ge=1, le=200),
    _authorized=Depends(require_admin)
):
    """Returns the monitoring audit trail of detected changes and accessibility checks."""
    return MonitoringRepository.get_activity_logs(limit=limit)

@router.get("/pending-updates")
async def list_pending_updates(
    include_demo: bool = Query(False),
    _authorized=Depends(require_admin)
):
    """Lists scheme updates awaiting human verification and authorization."""
    return MonitoringRepository.get_pending_updates(include_demo=include_demo)

@router.get("/schemes/{scheme_id}/history")
async def get_scheme_version_history(
    scheme_id: str,
    include_demo: bool = Query(False),
    _authorized=Depends(require_admin)
):
    """Retrieves full immutable version history and approval logs for a specific scheme."""
    history = MonitoringRepository.get_scheme_version_history(scheme_id, include_demo=include_demo)
    return {"scheme_id": scheme_id, "versions": history}

@router.post("/run")
async def trigger_monitoring_run(
    req: RunMonitoringRequest,
    _authorized=Depends(require_admin_csrf)
):
    """Triggers an on-demand polite monitoring check across official government sources."""
    report = await monitor_service.run_monitoring_cycle(target_source_id=req.source_id)
    return {
        "success": True,
        "message": f"Completed monitoring check. {report.get('success_count')} sources active, {report.get('changes_detected')} changes detected.",
        "report": report
    }

@router.post("/updates/{update_id}/approve")
async def approve_scheme_update(
    update_id: str,
    req: ApproveUpdateRequest,
    _authorized=Depends(require_admin_csrf)
):
    """
    Approves a detected scheme update.
    Archives the previous version, updates executable rules in the verified catalogue,
    and refreshes the active scheme cache.
    """
    success, message = MonitoringRepository.approve_update(
        update_id=update_id,
        approved_by=_authorized["sub"],
        reason=req.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Reload scheme service cache so approved rules are immediately available
    scheme_service.load_schemes()
    return {"success": True, "message": message}

@router.post("/updates/{update_id}/reject")
async def reject_scheme_update(
    update_id: str,
    req: RejectUpdateRequest,
    _authorized=Depends(require_admin_csrf)
):
    """
    Rejects a proposed scheme update with an audit rationale.
    The previous verified scheme rules remain in effect.
    """
    success, message = MonitoringRepository.reject_update(
        update_id=update_id,
        rejected_by=_authorized["sub"],
        reason=req.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}

@router.post("/schemes/{scheme_id}/rollback")
async def rollback_scheme_version(
    scheme_id: str,
    req: RollbackRequest,
    _authorized=Depends(require_admin_csrf)
):
    """Restores a scheme to a previous approved version from version history."""
    success, message = MonitoringRepository.rollback_scheme_version(
        scheme_id=scheme_id,
        target_version_id=req.target_version_id,
        rolled_back_by=_authorized["sub"]
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Reload scheme service cache
    scheme_service.load_schemes()
    return {"success": True, "message": message}

