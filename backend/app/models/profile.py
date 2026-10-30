from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class CitizenProfile(BaseModel):
    # Demographic
    age: Optional[int] = Field(None, description="Citizen age in years", ge=0, le=125)
    gender: Optional[str] = Field(None, description="male, female, transgender, other")
    marital_status: Optional[str] = Field(None, description="single, married, widow, divorced, deserted")
    
    # Location
    state: Optional[str] = Field(None, description="State of domicile / residence")
    residence_type: Optional[str] = Field(None, description="rural or urban")
    
    # Socio-economic
    category: Optional[str] = Field(None, description="General, OBC, SC, ST, EWS")
    occupation: Optional[str] = Field(None, description="farmer, student, agricultural_worker, self_employed, unemployed, homemaker, private_job")
    annual_income: Optional[float] = Field(None, description="Total annual family income in INR", ge=0)
    income_band: Optional[str] = Field(None, description="e.g. below_1_lakh, 1_to_2.5_lakh, 2.5_to_6_lakh, above_6_lakh")
    bpl_card_holder: Optional[bool] = Field(None, description="Whether family possesses BPL / Antyodaya ration card")
    
    # Agriculture / Assets
    landholding_hectares: Optional[float] = Field(None, description="Cultivable agricultural land in hectares", ge=0)
    is_institutional_landholder: Optional[bool] = Field(None, description="Whether land is held by institutional entity")
    holds_constitutional_post: Optional[bool] = Field(None, description="Whether applicant or family holds constitutional/govt post")
    has_pucca_house: Optional[bool] = Field(None, description="Whether family owns a pucca brick house")
    
    # Education
    student_class12_marks_percent: Optional[float] = Field(None, description="Class 12 board examination percentage", ge=0, le=100)
    enrolled_higher_education: Optional[bool] = Field(None, description="Whether enrolled in recognised college/university/professional degree")
    
    # Vulnerability
    disability_status: Optional[bool] = Field(None, description="Whether citizen has certified disability")
    disability_percent: Optional[float] = Field(None, description="Disability percentage if applicable", ge=0, le=100)
    
    # Meta tracking: which fields have been explicitly confirmed by user
    confirmed_fields: List[str] = Field(default_factory=list, description="Fields explicitly verified/confirmed by user")

    def is_field_confirmed(self, field_name: str) -> bool:
        # If confirmed_fields is empty, we consider fields populated via direct questionnaire as confirmed
        if not self.confirmed_fields:
            return getattr(self, field_name, None) is not None
        return field_name in self.confirmed_fields
