import json
import logging
from typing import Dict, Any, Optional

from ..db.database import get_db_connection
from .models import SchemeVersion, ReviewStatus, ChangeType
from .repository import AgentRepository
from ..services.scheme_service import scheme_service

logger = logging.getLogger("publishing_service")

def merge_eligibility_rules(existing_rules, proposed_value):
    """Map only supported extracted criteria to deterministic engine rules."""
    try:
        proposed = json.loads(proposed_value) if isinstance(proposed_value, str) else proposed_value
    except (TypeError, json.JSONDecodeError):
        return existing_rules
    if not isinstance(proposed, dict):
        return existing_rules

    rules = existing_rules if isinstance(existing_rules, list) else []
    field_ops = {
        "min_age": ("age", "gte", "Applicant must meet the minimum age requirement."),
        "max_age": ("age", "lte", "Applicant must meet the maximum age requirement."),
        "income_limit": ("annual_income", "lte", "Annual family income must be within the stated limit."),
        "gender": ("gender", "eq", "Applicant gender must match the stated requirement."),
        "domicile_state": ("state", "eq", "Applicant must reside in the stated state."),
    }
    for key, value in proposed.items():
        if key not in field_ops or value is None:
            continue
        field, operator, description = field_ops[key]
        rules = [rule for rule in rules if not (rule.get("field") == field and rule.get("operator") == operator)]
        rules.append({
            "field": field,
            "operator": operator,
            "value": value,
            "description_en": description,
            "description_hi": "यह शर्त आधिकारिक स्रोत में दी गई पात्रता से ली गई है।",
            "is_external_unverifiable": False,
        })
    return rules

def format_document_requirements(documents):
    """Keep catalog document entries valid while retaining only extracted names."""
    formatted = []
    for item in documents or []:
        if isinstance(item, dict):
            formatted.append(item)
            continue
        name = str(item).strip()
        if not name:
            continue
        slug = "_".join(name.lower().split())
        formatted.append({
            "id": slug,
            "name_en": name,
            "name_hi": name,
            "purpose_en": "Required document stated by the official source.",
            "purpose_hi": "आधिकारिक स्रोत में उल्लिखित आवश्यक दस्तावेज़।",
            "how_to_get_en": "Follow the instructions on the official application portal.",
            "how_to_get_hi": "आधिकारिक आवेदन पोर्टल पर दिए गए निर्देशों का पालन करें।",
        })
    return formatted

class PublishingService:
    """
    Agent 8: Publishing Service
    Safely publishes approved updates into the active scheme catalog,
    increments scheme versions, stores immutable version snapshots,
    and refreshes the SchemeService cache.
    """

    def publish_approved_update(self, update_id: str) -> Dict[str, Any]:
        """
        Takes an approved proposed_update ID and publishes the changes to the active scheme catalog.
        """
        update = AgentRepository.get_proposed_update_by_id(update_id)
        if not update:
            return {"success": False, "error": f"Update {update_id} not found."}

        if update.review_status != ReviewStatus.APPROVED:
            return {"success": False, "error": f"Update {update_id} is not APPROVED (status: {update.review_status.value})."}

        scheme_id = update.scheme_id
        now_date = AgentRepository.now_iso()[:10]  # YYYY-MM-DD
        now_iso = AgentRepository.now_iso()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if scheme exists in main schemes table
        cursor.execute("SELECT * FROM schemes WHERE scheme_id = ?", (scheme_id,))
        existing_row = cursor.fetchone()

        if existing_row:
            # Updating an existing scheme
            # Read existing fields
            rules = json.loads(existing_row["rules_json"]) if existing_row["rules_json"] else {}
            docs = json.loads(existing_row["required_documents_json"]) if existing_row["required_documents_json"] else []
            proc = json.loads(existing_row["application_procedure_json"]) if existing_row["application_procedure_json"] else []
            benefit_en = existing_row["benefit_en"]
            official_url = existing_row["official_source_url"]

            # Apply specific change based on change_type
            if update.change_type == ChangeType.ELIGIBILITY_CHANGE:
                rules = merge_eligibility_rules(rules, update.proposed_value)
            elif update.change_type == ChangeType.BENEFIT_CHANGE:
                benefit_en = update.proposed_value
            elif update.change_type == ChangeType.DOCUMENT_CHANGE:
                try:
                    docs = format_document_requirements(json.loads(update.proposed_value))
                except Exception:
                    docs = format_document_requirements(update.proposed_value.split(","))
            elif update.change_type == ChangeType.APPLICATION_PROCESS_CHANGE:
                try:
                    proc = json.loads(update.proposed_value)
                except Exception:
                    proc = [update.proposed_value]

            if update.source_url:
                official_url = update.source_url

            cursor.execute("""
            UPDATE schemes SET
                rules_json = ?,
                required_documents_json = ?,
                application_procedure_json = ?,
                benefit_en = ?,
                official_source_url = ?,
                last_verified_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE scheme_id = ?
            """, (
                json.dumps(rules, ensure_ascii=False),
                json.dumps(docs, ensure_ascii=False),
                json.dumps(proc, ensure_ascii=False),
                benefit_en,
                official_url,
                now_date,
                scheme_id
            ))
            conn.commit()

            # Build full scheme data snapshot for version history
            scheme_data = {
                "id": scheme_id,
                "name_en": existing_row["name_en"],
                "name_hi": existing_row["name_hi"],
                "level": existing_row["level"],
                "category": existing_row["category"],
                "applicable_states": json.loads(existing_row["applicable_states"]),
                "benefit_en": benefit_en,
                "benefit_hi": existing_row["benefit_hi"],
                "description_en": existing_row["description_en"],
                "description_hi": existing_row["description_hi"],
                "rules": rules,
                "required_documents": docs,
                "application_procedure": proc,
                "restrictions": json.loads(existing_row["restrictions_json"]) if existing_row["restrictions_json"] else {},
                "official_source_url": official_url,
                "helpline": existing_row["helpline"],
                "last_verified_date": now_date
            }

        else:
            # Publishing a brand new discovered scheme
            # Retrieve discovered scheme record if available
            disc_scheme = AgentRepository.get_discovered_scheme_by_id(scheme_id)
            extracted = disc_scheme.extracted_data if disc_scheme else {}

            name_en = extracted.get("scheme_name") or update.proposed_value or scheme_id.replace("_", " ").title()
            level = extracted.get("classification") or "central"
            state = extracted.get("state")
            applicable_states = [state] if state and state.lower() != "all" else ["All"]

            rules = merge_eligibility_rules([], extracted.get("eligibility_conditions") or {})
            docs = format_document_requirements(extracted.get("required_documents") or [])
            proc = extracted.get("application_process") or []
            benefit_en = extracted.get("benefits") or "Welfare assistance"
            desc_en = extracted.get("description") or f"Government initiative: {name_en}"
            official_url = update.source_url or extracted.get("official_application_url") or "https://data.gov.in/"

            cursor.execute("""
            INSERT INTO schemes (
                scheme_id, name_en, name_hi, level, category, applicable_states,
                benefit_en, benefit_hi, description_en, description_hi,
                rules_json, required_documents_json, application_procedure_json,
                restrictions_json, official_source_url, helpline, last_verified_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scheme_id,
                name_en,
                name_en,  # Hindi fallback to English title until translated
                level,
                "welfare",
                json.dumps(applicable_states, ensure_ascii=False),
                benefit_en,
                benefit_en,
                desc_en,
                desc_en,
                json.dumps(rules, ensure_ascii=False),
                json.dumps(docs, ensure_ascii=False),
                json.dumps(proc, ensure_ascii=False),
                json.dumps([], ensure_ascii=False),
                official_url,
                "181",
                now_date
            ))
            conn.commit()

            scheme_data = {
                "id": scheme_id,
                "name_en": name_en,
                "name_hi": name_en,
                "level": level,
                "category": "welfare",
                "applicable_states": applicable_states,
                "benefit_en": benefit_en,
                "benefit_hi": benefit_en,
                "description_en": desc_en,
                "description_hi": desc_en,
                "rules": rules,
                "required_documents": docs,
                "application_procedure": proc,
                "restrictions": {},
                "official_source_url": official_url,
                "helpline": "181",
                "last_verified_date": now_date
            }

        conn.close()

        # Increment version and save to scheme_versions
        current_version_num = AgentRepository.get_latest_version_number(scheme_id)
        new_version_num = current_version_num + 1

        version_record = SchemeVersion(
            scheme_id=scheme_id,
            version_number=new_version_num,
            scheme_data=scheme_data,
            source_url=update.source_url,
            approval_status=ReviewStatus.APPROVED.value,
            created_at=now_iso
        )
        AgentRepository.save_scheme_version(version_record)

        # Reload schemes in SchemeService cache so the Python rule engine immediately sees the new scheme
        scheme_service.load_schemes()
        logger.info(f"Published scheme {scheme_id} version {new_version_num}. SchemeService reloaded.")

        return {
            "success": True,
            "scheme_id": scheme_id,
            "version_number": new_version_num,
            "published_at": now_iso
        }
