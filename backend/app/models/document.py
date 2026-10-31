from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentSamplePreview(BaseModel):
    sample_type: str = Field("certificate", description="'id_card', 'certificate', 'passbook', 'land_record', 'marksheet'")
    holder_name: str = "JOHN DOE"
    document_number: str = "XX/SAMPLE/2026/0000"
    issuing_authority: str = "Government Authority"
    watermark_text: str = "ILLUSTRATIVE SAMPLE — NOT AN OFFICIAL DOCUMENT"
    key_fields: Dict[str, str] = Field(default_factory=dict)
    disclaimer_en: str = "This is a synthetic illustrative representation for informational purposes only. Actual certificates vary by issuing state and authority."
    disclaimer_hi: str = "यह केवल जानकारी हेतु एक काल्पनिक प्रारूप है। वास्तविक प्रमाण पत्र राज्य एवं जारीकर्ता प्राधिकरण के अनुसार भिन्न हो सकते हैं।"

class DocumentDefinition(BaseModel):
    id: str = Field(..., description="Unique canonical document ID (e.g. income_certificate)")
    aliases: List[str] = Field(default_factory=list, description="Alternative IDs used in existing scheme files")
    name_en: str
    name_hi: str
    category: str = Field("General", description="Identity, Revenue, Residence, Social Security, Education, Land")
    short_explanation_en: str
    short_explanation_hi: str
    why_schemes_ask_en: str
    why_schemes_ask_hi: str
    issuer_en: str
    issuer_hi: str
    contents_en: List[str]
    contents_hi: List[str]
    required_for_application_en: List[str]
    required_for_application_hi: List[str]
    application_steps_en: List[str]
    application_steps_hi: List[str]
    sample_preview: DocumentSamplePreview
    apply_url: Optional[str] = None
    is_online_available: bool = True
    application_mode_note_en: str
    application_mode_note_hi: str
    issuing_authority_note_en: str
    issuing_authority_note_hi: str

class DocumentSummary(BaseModel):
    id: str
    name_en: str
    name_hi: str
    category: str
    short_explanation_en: str
    short_explanation_hi: str
    issuer_en: str
    issuer_hi: str
    is_online_available: bool
    apply_url: Optional[str] = None
