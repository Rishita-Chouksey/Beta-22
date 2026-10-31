from fastapi import APIRouter
from ..models.api import ChecklistRequest, ChecklistResponse
from ..services.checklist_service import generate_consolidated_checklist

router = APIRouter()

@router.post("/checklist", response_model=ChecklistResponse)
async def get_document_checklist(req: ChecklistRequest):
    """
    Generates a personalized consolidated and de-duplicated document checklist
    for the selected scheme IDs.
    """
    return generate_consolidated_checklist(req.scheme_ids)
