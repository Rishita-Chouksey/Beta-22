from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..models.scheme import SchemeDefinition
from ..models.api import RulesStatusResponse
from ..services.scheme_service import scheme_service
from ..services.local_translator_service import local_translator

router = APIRouter()


def _localized(scheme: SchemeDefinition, lang: Optional[str]) -> SchemeDefinition:
    """Fill any missing <field>_<lang> text from the English source, offline, on the fly."""
    if not lang or lang == "en":
        return scheme
    data = local_translator.localize(scheme.model_dump(), lang)
    return SchemeDefinition.model_validate(data)


@router.get("/schemes", response_model=List[SchemeDefinition])
async def list_schemes(lang: Optional[str] = Query(None, description="en | hi | bn")):
    """Lists all available official schemes (optionally completed in the requested language)."""
    return [_localized(s, lang) for s in scheme_service.get_all_schemes()]


@router.get("/schemes/{scheme_id}", response_model=SchemeDefinition)
async def get_scheme(scheme_id: str, lang: Optional[str] = Query(None, description="en | hi | bn")):
    """Retrieves full details, rules, documents, and procedures for a single scheme."""
    scheme = scheme_service.get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found.")
    return _localized(scheme, lang)


@router.get("/rules-status", response_model=RulesStatusResponse)
async def get_rules_status():
    """Provides verification audit status of all scheme rule definitions in the library."""
    data = scheme_service.get_rules_status()
    return RulesStatusResponse(**data)
