from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.document import DocumentDefinition, DocumentSummary
from ..services.document_service import document_service

router = APIRouter()

@router.get("/documents", response_model=List[DocumentSummary])
async def list_documents(
    query: Optional[str] = Query(None, description="Search term for document name or keywords"),
    category: Optional[str] = Query(None, description="Filter by category: Identity, Revenue, Residence, Social Security, Education, Land")
):
    """
    Returns the comprehensive list of commonly required civic documents in the Document Guide.
    Supports keyword search and category filtering.
    """
    if query:
        docs = document_service.search_documents(query)
    else:
        docs = document_service.get_all_documents()

    if category:
        docs = [d for d in docs if d.category.lower() == category.lower()]

    return docs

@router.get("/documents/{doc_id}", response_model=DocumentDefinition)
async def get_document_details(doc_id: str):
    """
    Retrieves complete Document Guide details for a single document.
    Seamlessly resolves aliases from scheme checklists (e.g. mp_domicile -> domicile_certificate).
    """
    doc = document_service.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{doc_id}' not found in official Document Guide library."
        )
    return doc
