"""
Rule-Based Validation Engine.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Consumes the output of extract_transaction_fields() and returns a structured
verdict dict for direct consumption by Person 1's ensemble/UI module.

Academic premise: flags *potential inconsistencies* based on format, logic,
and metadata rules — not a live bank ledger lookup.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from .validators import (
    check_amount_present,
    check_amount_positive,
    check_amount_range,
    check_date_not_future,
    check_date_not_too_old,
    check_date_present,
    check_recipient_present,
    check_status_present,
    check_utr_length,
    check_utr_numeric,
    check_utr_present,
)

# ---------------------------------------------------------------------------
# Weights — higher = more suspicion contribution when failed
# ---------------------------------------------------------------------------
_RULE_WEIGHTS: Dict[str, float] = {
    "amount_present":  0.15,
    "amount_positive": 0.10,
    "amount_range":    0.05,
    "date_present":    0.15,
    "date_not_future": 0.25,   # Strongest tamper signal
    "date_not_old":    0.05,
    "utr_present":     0.10,
    "utr_numeric":     0.15,   # Alpha prefix = tamper
    "utr_length":      0.10,   # Wrong digit count = tamper
    "status_present":  0.05,
    "recipient_present": 0.05,
}


def _run_all(fields: Dict[str, Any]) -> List[Tuple[str, bool, str, float]]:
    """
    Executes all validators.
    Returns list of (rule_key, passed, message, weight).
    """
    amt    = fields.get("amount")
    amtv   = fields.get("amount_value")
    dt_str = fields.get("date")
    dt_iso = fields.get("date_iso")
    utr    = fields.get("transaction_id")
    status = fields.get("status")
    recip  = fields.get("recipient")

    checks = [
        ("amount_present",   *check_amount_present(amt),   _RULE_WEIGHTS["amount_present"]),
        ("amount_positive",  *check_amount_positive(amtv), _RULE_WEIGHTS["amount_positive"]),
        ("amount_range",     *check_amount_range(amtv),    _RULE_WEIGHTS["amount_range"]),
        ("date_present",     *check_date_present(dt_str),  _RULE_WEIGHTS["date_present"]),
        ("date_not_future",  *check_date_not_future(dt_iso), _RULE_WEIGHTS["date_not_future"]),
        ("date_not_old",     *check_date_not_too_old(dt_iso), _RULE_WEIGHTS["date_not_old"]),
        ("utr_present",      *check_utr_present(utr),      _RULE_WEIGHTS["utr_present"]),
        ("utr_numeric",      *check_utr_numeric(utr),      _RULE_WEIGHTS["utr_numeric"]),
        ("utr_length",       *check_utr_length(utr),       _RULE_WEIGHTS["utr_length"]),
        ("status_present",   *check_status_present(status), _RULE_WEIGHTS["status_present"]),
        ("recipient_present", *check_recipient_present(recip), _RULE_WEIGHTS["recipient_present"]),
    ]
    return checks


def validate_transaction(
    ocr_result: Dict[str, Any],
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Runs all rule-based checks on an OCR extraction result.

    Args:
        ocr_result     : dict returned by extract_transaction_fields().
        reference_date : Optional date to use as 'today' (useful for testing).

    Returns dict with:
        'verdict'        — 'SUSPICIOUS' | 'LIKELY_LEGITIMATE' | 'UNREADABLE'
        'suspicion_score'— float 0.0 (clean) → 1.0 (highly suspicious)
        'violations'     — list of failed rule messages
        'warnings'       — list of soft-fail rule messages
        'passed_checks'  — list of passed rule messages
        'explanation'    — human-readable summary paragraph
        'fields_used'    — the fields dict that was analysed
    """
    fields = ocr_result.get("fields", {})
    success = ocr_result.get("success", False)

    # If OCR completely failed, return early
    if not success and not fields:
        return {
            "verdict": "UNREADABLE",
            "suspicion_score": 1.0,
            "violations": ["Image could not be read or no fields extracted."],
            "warnings": [],
            "passed_checks": [],
            "explanation": "The receipt image could not be processed by the OCR engine.",
            "fields_used": fields,
        }

    # Override reference date if supplied (primarily for testing)
    if reference_date is not None:
        import src.rules.validators as _v
        _original = _v.date
        # Monkey-patch for this call only
        class _FixedDate:
            @staticmethod
            def today():
                return reference_date
        _v.date = _FixedDate  # type: ignore[assignment]

    checks = _run_all(fields)

    if reference_date is not None:
        import src.rules.validators as _v
        _v.date = _original  # type: ignore[assignment]

    violations: List[str] = []
    warnings: List[str]   = []
    passed:   List[str]   = []
    weighted_fail = 0.0

    for rule_key, passed_flag, message, weight in checks:
        if passed_flag:
            passed.append(message)
        else:
            # Distinguish hard fails vs soft warnings
            if "FAIL" in message:
                violations.append(message)
                weighted_fail += weight
            else:  # WARN / SKIP
                warnings.append(message)
                weighted_fail += weight * 0.4  # Warnings count less

    suspicion_score = min(round(weighted_fail, 3), 1.0)

    if suspicion_score >= 0.25:
        verdict = "SUSPICIOUS"
    else:
        verdict = "LIKELY_LEGITIMATE"

    # Build human-readable explanation
    if verdict == "SUSPICIOUS":
        top_violation = violations[0] if violations else (warnings[0] if warnings else "")
        explanation = (
            f"Receipt flagged as SUSPICIOUS (score={suspicion_score:.2f}/1.00). "
            f"{len(violations)} violation(s) detected. "
            f"Primary concern: {top_violation}"
        )
    else:
        explanation = (
            f"Receipt appears LIKELY LEGITIMATE (score={suspicion_score:.2f}/1.00). "
            f"All critical checks passed with {len(passed)} rules satisfied."
        )

    return {
        "verdict": verdict,
        "suspicion_score": suspicion_score,
        "violations": violations,
        "warnings": warnings,
        "passed_checks": passed,
        "explanation": explanation,
        "fields_used": fields,
    }
