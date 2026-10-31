from typing import Optional, List, Any, Dict, Literal
from pydantic import BaseModel, Field

# ISO 3166-2:IN Two-letter codes for all 28 States and 8 Union Territories
STATE_NAME_TO_ISO = {
    "andhra pradesh": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CT",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OD",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN",
    "telangana": "TG",
    "tripura": "TR",
    "uttar pradesh": "UP",
    "uttarakhand": "UT",
    "west bengal": "WB",
    "andaman and nicobar islands": "AN",
    "chandigarh": "CH",
    "dadra and nagar haveli and daman and diu": "DH",
    "delhi": "DL",
    "jammu and kashmir": "JK",
    "ladakh": "LA",
    "lakshadweep": "LD",
    "puducherry": "PY",
    "unknown": "unknown",
    "other": "unknown"
}

class CitizenProfile(BaseModel):
    # Demographic
    age: Optional[int] = Field(None, description="Citizen age in years", ge=0, le=125)
    gender: Optional[str] = Field(None, description="male, female, transgender, other")
    marital_status: Optional[str] = Field(None, description="single, married, widow, divorced, deserted")
    
    # Location
    state: Optional[str] = Field(None, description="State of domicile / residence (2-letter ISO code or name)")
    residence_type: Optional[str] = Field(None, description="rural or urban")
    
    # Socio-economic
    category: Optional[str] = Field(None, description="General, OBC, SC, ST, EWS")
    occupation: Optional[str] = Field(None, description="farmer, student, agricultural_worker, self_employed, unemployed, homemaker, private_job")
    annual_income: Optional[float] = Field(None, description="Total annual family income in INR", ge=0)
    income_band: Optional[str] = Field(None, description="e.g. below_1_lakh, 1_to_2.5_lakh, 2.5_to_6_lakh, above_6_lakh")
    bpl_card_holder: Optional[bool] = Field(None, description="Whether family possesses BPL / Antyodaya ration card")
    
    # Agriculture / Assets
    landholding_hectares: Optional[float] = Field(None, description="Cultivable agricultural land in hectares", ge=0)
    is_institutional_landholder: Optional[bool] = Field(default=False, description="Whether land is held by institutional entity")
    holds_constitutional_post: Optional[bool] = Field(default=False, description="Whether applicant or family holds constitutional/govt post")
    has_pucca_house: Optional[bool] = Field(None, description="Whether family owns a pucca brick house")
    
    # Education
    student_class12_marks_percent: Optional[float] = Field(None, description="Class 12 board examination percentage", ge=0, le=100)
    enrolled_higher_education: Optional[bool] = Field(None, description="Whether enrolled in recognised college/university/professional degree")
    
    # Vulnerability
    disability_status: Optional[bool] = Field(None, description="Whether citizen has certified disability")
    disability_percent: Optional[float] = Field(None, description="Disability percentage if applicable", ge=0, le=100)
    
    # Meta tracking: which fields have been explicitly confirmed or skipped by user
    confirmed_fields: List[str] = Field(default_factory=list, description="Fields explicitly verified/confirmed by user")
    skipped_fields: List[str] = Field(default_factory=list, description="Fields explicitly skipped or declared unknown by user")

    def get_normalized_state_code(self) -> Optional[str]:
        if not self.state:
            return None
        st = self.state.strip()
        if len(st) == 2 and st.upper() in STATE_NAME_TO_ISO.values():
            return st.upper()
        return STATE_NAME_TO_ISO.get(st.lower(), "unknown")

    def is_field_confirmed(self, field_name: str) -> bool:
        if not self.confirmed_fields:
            return getattr(self, field_name, None) is not None
        return field_name in self.confirmed_fields
