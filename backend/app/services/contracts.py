"""Contract template definitions and term validation.

IMPORTANT: These templates are NOT legal advice. They are convenience
scaffolding for generating draft agreements and require review by a
qualified lawyer (employment/immigration/tax as applicable) before any
contract generated from them is used in production.

Design: every template has exactly one compensation field — either
``salary`` (for full-time/salaried arrangements) or ``hourly_rate`` (for
contractor/gig arrangements) — plus ``currency`` and ``start_date``, which
every template requires. Cross-border templates add fields that pin down
where work is performed and how/when payment happens.
"""

from typing import Any, Dict, List

from app.models.contract import ContractTemplateType

TEMPLATES: Dict[str, Dict[str, Any]] = {
    ContractTemplateType.KOREA_ENGINEER_CANADA_CO.value: {
        "label": "Korea-Based Engineer, Canadian Company",
        "description": (
            "For an engineer working from Korea and employed or contracted by a "
            "Canadian company. Covers cross-border pay currency and schedule."
        ),
        "required_terms": [
            "salary",
            "currency",
            "start_date",
            "work_location_country",
            "payment_schedule",
        ],
    },
    ContractTemplateType.CANADA_ENGINEER_KOREA_CO.value: {
        "label": "Canada-Based Engineer, Korean Company",
        "description": (
            "For an engineer working from Canada and employed or contracted by a "
            "Korean company. Covers cross-border pay currency and schedule."
        ),
        "required_terms": [
            "salary",
            "currency",
            "start_date",
            "work_location_country",
            "payment_schedule",
        ],
    },
    ContractTemplateType.REMOTE_CONTRACTOR.value: {
        "label": "Remote Contractor Agreement",
        "description": (
            "General-purpose agreement for an independent contractor paid hourly, "
            "regardless of location."
        ),
        "required_terms": [
            "hourly_rate",
            "currency",
            "start_date",
            "payment_schedule",
        ],
    },
    ContractTemplateType.FULL_TIME_DOMESTIC.value: {
        "label": "Full-Time (Same Country)",
        "description": (
            "Standard full-time employment agreement where the employer and "
            "employee are in the same country."
        ),
        "required_terms": [
            "salary",
            "currency",
            "start_date",
        ],
    },
    ContractTemplateType.PART_TIME_GIG.value: {
        "label": "Part-Time / Gig Agreement",
        "description": (
            "Lightweight agreement for part-time or gig work paid hourly with a "
            "defined weekly time commitment."
        ),
        "required_terms": [
            "hourly_rate",
            "currency",
            "start_date",
            "hours_per_week",
        ],
    },
}


def validate_terms(
    template_type: ContractTemplateType, terms: Dict[str, Any]
) -> List[str]:
    """Return the list of required term keys missing (or null) in `terms`."""
    required = TEMPLATES[template_type.value]["required_terms"]
    return [key for key in required if terms.get(key) is None]


# Money terms are integer cents (see CLAUDE.md: no floats for money).
MONEY_TERMS = ("salary", "hourly_rate")
# Plain numeric terms (not money).
NUMERIC_TERMS = ("hours_per_week",)


def validate_term_types(terms: Dict[str, Any]) -> List[str]:
    """Return human-readable errors for present terms that have the wrong type.

    Missing terms are reported by `validate_terms`; this only checks values
    that were supplied. `bool` is excluded explicitly because it is an `int`
    subclass in Python.
    """
    errors: List[str] = []
    for key in MONEY_TERMS:
        value = terms.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            errors.append(f"{key} must be a positive integer number of cents")
    for key in NUMERIC_TERMS:
        value = terms.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{key} must be a positive number")
    return errors
