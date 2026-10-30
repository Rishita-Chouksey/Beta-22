from fastapi import APIRouter, HTTPException
from ..models.api import NextQuestionRequest, NextQuestionResponse, EvaluateRequest
from ..models.evaluation import OverallEvaluationResponse
from ..engine.question_selector import select_next_question
from ..engine.evaluator import evaluate_all_schemes
from ..services.scheme_service import scheme_service

router = APIRouter()

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(req: NextQuestionRequest):
    """
    Intelligently determines the next question based on current citizen profile answers.
    Evaluates remaining schemes and selects the field having maximum impact.
    """
    schemes = scheme_service.get_all_schemes()
    # Count how many fields are already populated to track step progress
    answered_count = sum(1 for k, v in req.profile.model_dump().items() if v is not None and k != "confirmed_fields")
    return select_next_question(schemes, req.profile, current_step=answered_count + 1)

@router.post("/evaluate", response_model=OverallEvaluationResponse)
async def evaluate_profile(req: EvaluateRequest):
    """
    Evaluates citizen profile against all official government schemes.
    Sorts results into:
    - ELIGIBLE: Every rule passed with confirmed answers.
    - NOT SURE: Missing answers, borderline values, or external verification needed.
    - NOT ELIGIBLE: At least one rule clearly failed.
    - NO CURRENT RULES: Unverified or outdated scheme rules.
    """
    schemes = scheme_service.get_all_schemes()
    return evaluate_all_schemes(schemes, req.profile)
