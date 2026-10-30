from typing import List, Dict
from ..models.api import ChecklistDocumentItem, ChecklistResponse
from .scheme_service import scheme_service

def generate_consolidated_checklist(scheme_ids: List[str]) -> ChecklistResponse:
    """
    Consolidates required documents across all given scheme IDs.
    De-duplicates identical documents and tracks which schemes require each document.
    """
    doc_map: Dict[str, ChecklistDocumentItem] = {}
    schemes_covered: List[str] = []

    for sid in scheme_ids:
        scheme = scheme_service.get_scheme_by_id(sid)
        if not scheme:
            continue
            
        schemes_covered.append(scheme.name_en)
        for doc in scheme.required_documents:
            if doc.id in doc_map:
                # Add scheme name if not already listed
                if scheme.name_en not in doc_map[doc.id].schemes_required_for:
                    doc_map[doc.id].schemes_required_for.append(scheme.name_en)
            else:
                doc_map[doc.id] = ChecklistDocumentItem(
                    document_id=doc.id,
                    name_en=doc.name_en,
                    name_hi=doc.name_hi,
                    schemes_required_for=[scheme.name_en],
                    purpose_en=doc.purpose_en,
                    purpose_hi=doc.purpose_hi,
                    how_to_get_en=doc.how_to_get_en,
                    how_to_get_hi=doc.how_to_get_hi,
                    online_url=doc.online_url,
                    offline_office=doc.offline_office
                )

    doc_list = list(doc_map.values())
    return ChecklistResponse(
        documents=doc_list,
        total_documents=len(doc_list),
        schemes_covered=schemes_covered
    )
