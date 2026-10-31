import logging
from typing import List, Dict, Any, Optional

from .models import ChangeType, ExtractedSchemeData

logger = logging.getLogger("classification_agent")

class ClassificationAgent:
    """
    Agent 5: Classification Agent
    Classifies discovered information and changes into policy-relevant categories:
    NEW_SCHEME, ELIGIBILITY_CHANGE, BENEFIT_CHANGE, DOCUMENT_CHANGE, DEADLINE_CHANGE, etc.
    """

    def classify(self, existing_scheme: Optional[Dict[str, Any]], extracted: ExtractedSchemeData) -> List[ChangeType]:
        """
        Compares existing scheme definition with freshly extracted data to determine all change types.
        """
        changes: List[ChangeType] = []

        if not existing_scheme:
            changes.append(ChangeType.NEW_SCHEME)
            return changes

        # 1. Eligibility criteria changes
        old_rules = existing_scheme.get("rules") or {}
        if isinstance(old_rules, list):
            normalized_rules = {}
            for rule in old_rules:
                field = rule.get("field")
                operator = rule.get("operator")
                if field == "age" and operator == "gte":
                    normalized_rules["min_age"] = rule.get("value")
                elif field == "age" and operator == "lte":
                    normalized_rules["max_age"] = rule.get("value")
                elif field == "annual_income" and operator == "lte":
                    normalized_rules["income_limit"] = rule.get("value")
                elif field and operator == "eq":
                    normalized_rules[field] = rule.get("value")
            old_rules = normalized_rules
        new_elig = extracted.eligibility_conditions or {}

        # Age check
        if "min_age" in new_elig and new_elig["min_age"] is not None:
            if old_rules.get("min_age") != new_elig["min_age"]:
                changes.append(ChangeType.ELIGIBILITY_CHANGE)
        elif "max_age" in new_elig and new_elig["max_age"] is not None:
            if old_rules.get("max_age") != new_elig["max_age"]:
                if ChangeType.ELIGIBILITY_CHANGE not in changes:
                    changes.append(ChangeType.ELIGIBILITY_CHANGE)

        # Income check
        if "income_limit" in new_elig and new_elig["income_limit"] is not None:
            if old_rules.get("max_income") != new_elig["income_limit"]:
                if ChangeType.ELIGIBILITY_CHANGE not in changes:
                    changes.append(ChangeType.ELIGIBILITY_CHANGE)

        # 2. Benefit changes
        old_benefit = existing_scheme.get("benefit_en") or ""
        new_benefit = extracted.benefits or ""
        if new_benefit and old_benefit and new_benefit.lower() != old_benefit.lower():
            changes.append(ChangeType.BENEFIT_CHANGE)

        # 3. Document changes
        old_docs = set(existing_scheme.get("required_documents") or [])
        new_docs = set(extracted.required_documents or [])
        if new_docs and old_docs != new_docs:
            changes.append(ChangeType.DOCUMENT_CHANGE)

        # 4. Deadline changes
        old_deadline = existing_scheme.get("deadline")
        new_deadline = extracted.deadline
        if new_deadline and old_deadline != new_deadline:
            changes.append(ChangeType.DEADLINE_CHANGE)

        # 5. Application process changes
        old_proc = existing_scheme.get("application_procedure") or []
        new_proc = extracted.application_process or []
        if new_proc and old_proc != new_proc:
            changes.append(ChangeType.APPLICATION_PROCESS_CHANGE)

        # If nothing specific changed, check for minor content or guideline update
        if not changes:
            if extracted.official_guideline_url:
                changes.append(ChangeType.GUIDELINE_UPDATE)
            else:
                changes.append(ChangeType.MINOR_CONTENT_CHANGE)

        return changes
