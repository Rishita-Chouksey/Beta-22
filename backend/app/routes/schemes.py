from fastapi import APIRouter, HTTPException
from typing import List
from ..models.scheme import SchemeDefinition
from ..models.api import RulesStatusResponse
from ..services.scheme_service import scheme_service

router = APIRouter()

@router.get("/schemes", response_model=List[SchemeDefinition])
async def list_schemes():
    """Lists all available official schemes."""
    return scheme_service.get_all_schemes()

@router.get("/schemes/{scheme_id}", response_model=SchemeDefinition)
async def get_scheme(scheme_id: str):
    """Retrieves full details, rules, documents, and procedures for a single scheme."""
    scheme = scheme_service.get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found.")
    return scheme

@router.get("/rules-status", response_model=RulesStatusResponse)
async def get_rules_status():
    """Provides verification audit status of all scheme rule definitions in the library."""
    data = scheme_service.get_rules_status()
    return RulesStatusResponse(**data)
