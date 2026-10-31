from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..config import settings
from ..db.repository import MonitoringRepository
from ..monitoring.monitor_service import monitor_service
from ..monitoring.models import MonitoringSummary
from ..services.scheme_service import scheme_service

router = APIRouter(prefix="/admin/monitoring", tags=["Admin Scheme Monitoring"])

def verify_admin_access(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """
    Enforces secure, backend-protected administrative authorization.
    Rejects unauthorized requests with 401/403.
    """
    expected_key = getattr(settings, "ADMIN_API_KEY", "")
    if not expected_key:
        raise HTTPException(
            status_code=403,
            detail="Admin access unconfigured. Set ADMIN_API_KEY in backend environment (.env)."
        )
    if not x_admin_key or x_admin_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Missing or invalid X-Admin-Key header."
        )
    return True

class ApproveUpdateRequest(BaseModel):
    reviewer_name: str = Field(default="Verification Officer", description="Name/Role of reviewer approving update")
    reason: str = Field(..., description="Audit rationale for approving the scheme update")

class RejectUpdateRequest(BaseModel):
    reviewer_name: str = Field(default="Verification Officer", description="Name/Role of reviewer rejecting update")
    reason: str = Field(..., description="Audit rationale for rejecting the scheme update")

class RollbackRequest(BaseModel):
    target_version_id: int = Field(..., description="ID of historical version to restore")
    reviewer_name: str = Field(default="Verification Officer", description="Name of officer authorizing rollback")

class RunMonitoringRequest(BaseModel):
    source_id: Optional[str] = Field(None, description="Optional single source ID to check, or None for all")

@router.get("/summary", response_model=MonitoringSummary)
async def get_monitoring_summary(_authorized: bool = Depends(verify_admin_access)):
    """Provides high-level system monitoring health and pending update counts."""
    summary = MonitoringRepository.get_monitoring_summary()
    return MonitoringSummary(**summary)

@router.get("/sources")
async def list_monitoring_sources(_authorized: bool = Depends(verify_admin_access)):
    """Lists all monitored official government portals, their category, and live health status."""
    return MonitoringRepository.get_all_sources()

@router.get("/changes")
async def list_activity_changes(
    limit: int = Query(50, ge=1, le=200),
    _authorized: bool = Depends(verify_admin_access)
):
    """Returns the monitoring audit trail of detected changes and accessibility checks."""
    return MonitoringRepository.get_activity_logs(limit=limit)

@router.get("/pending-updates")
async def list_pending_updates(
    include_demo: bool = Query(False),
    _authorized: bool = Depends(verify_admin_access)
):
    """Lists scheme updates awaiting human verification and authorization."""
    return MonitoringRepository.get_pending_updates(include_demo=include_demo)

@router.get("/schemes/{scheme_id}/history")
async def get_scheme_version_history(
    scheme_id: str,
    _authorized: bool = Depends(verify_admin_access)
):
    """Retrieves full immutable version history and approval logs for a specific scheme."""
    history = MonitoringRepository.get_scheme_version_history(scheme_id)
    return {"scheme_id": scheme_id, "versions": history}

@router.post("/run")
async def trigger_monitoring_run(
    req: RunMonitoringRequest,
    _authorized: bool = Depends(verify_admin_access)
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
    _authorized: bool = Depends(verify_admin_access)
):
    """
    Approves a detected scheme update.
    Archives the previous version, updates executable rules in the verified catalogue,
    and refreshes the active scheme cache.
    """
    success, message = MonitoringRepository.approve_update(
        update_id=update_id,
        approved_by=req.reviewer_name,
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
    _authorized: bool = Depends(verify_admin_access)
):
    """
    Rejects a proposed scheme update with an audit rationale.
    The previous verified scheme rules remain in effect.
    """
    success, message = MonitoringRepository.reject_update(
        update_id=update_id,
        rejected_by=req.reviewer_name,
        reason=req.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}

@router.post("/schemes/{scheme_id}/rollback")
async def rollback_scheme_version(
    scheme_id: str,
    req: RollbackRequest,
    _authorized: bool = Depends(verify_admin_access)
):
    """Restores a scheme to a previous approved version from version history."""
    success, message = MonitoringRepository.rollback_scheme_version(
        scheme_id=scheme_id,
        target_version_id=req.target_version_id,
        rolled_back_by=req.reviewer_name
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Reload scheme service cache
    scheme_service.load_schemes()
    return {"success": True, "message": message}

