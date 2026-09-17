"""
Atomic Rule Validators.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Each validator returns a (passed: bool, message: str) tuple.
- passed=True  → rule satisfied, transaction looks legitimate on this criterion
- passed=False → inconsistency / potential tamper detected
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple

# Standard UPI UTR is 12 digits (NPCI mandate)
_STANDARD_UTR_LENGTH = 12
_NUMERIC_RE = re.compile(r'^\d+$')


# ---------------------------------------------------------------------------
# 1. Amount validators
# ---------------------------------------------------------------------------

def check_amount_present(amount: Optional[str]) -> Tuple[bool, str]:
    """RULE-01: Transaction amount must be present and non-empty."""
    if not amount:
        return False, "RULE-01 FAIL: Amount field is missing or could not be extracted."
    return True, "RULE-01 PASS: Amount field present."


def check_amount_positive(amount_value: Optional[float]) -> Tuple[bool, str]:
    """RULE-02: Amount must be a positive numeric value > 0."""
    if amount_value is None:
        return False, "RULE-02 FAIL: Amount numeric value is missing."
    if amount_value <= 0:
        return False, f"RULE-02 FAIL: Amount ₹{amount_value:.2f} is non-positive."
    return True, f"RULE-02 PASS: Amount ₹{amount_value:,.2f} is positive."


def check_amount_range(amount_value: Optional[float]) -> Tuple[bool, str]:
    """RULE-03: Amount must be within plausible UPI range (₹1 – ₹1,00,000)."""
    if amount_value is None:
        return False, "RULE-03 SKIP: Amount not available for range check."
    if not (1.0 <= amount_value <= 100_000.0):
        return False, (
            f"RULE-03 WARN: Amount ₹{amount_value:,.2f} is outside plausible "
            f"everyday UPI range ₹1 – ₹1,00,000. Possible tamper or test artefact."
        )
    return True, f"RULE-03 PASS: Amount ₹{amount_value:,.2f} is within plausible UPI range."


# ---------------------------------------------------------------------------
# 2. Date validators
# ---------------------------------------------------------------------------

def check_date_present(date_str: Optional[str]) -> Tuple[bool, str]:
    """RULE-04: Transaction date must be extractable."""
    if not date_str:
        return False, "RULE-04 FAIL: Date field is missing or could not be extracted."
    return True, "RULE-04 PASS: Date field present."


def check_date_not_future(date_iso: Optional[str], reference: Optional[date] = None) -> Tuple[bool, str]:
    """
    RULE-05: Transaction date must NOT be in the future.
    UPI receipts for completed payments cannot have a future date — this is a
    strong tamper indicator (e.g., date_change tamper variant sets '28 Dec 2029').
    """
    if not date_iso:
        return False, "RULE-05 SKIP: ISO date not available for future-date check."

    try:
        txn_date = datetime.strptime(date_iso, "%Y-%m-%d").date()
    except ValueError:
        return False, f"RULE-05 FAIL: Cannot parse date '{date_iso}' as YYYY-MM-DD."

    ref = reference or date.today()
    if txn_date > ref:
        return False, (
            f"RULE-05 FAIL: Transaction date {date_iso} is in the FUTURE "
            f"(reference: {ref}). Strong tamper indicator."
        )
    return True, f"RULE-05 PASS: Transaction date {date_iso} is not in the future."


def check_date_not_too_old(date_iso: Optional[str], max_years: int = 5) -> Tuple[bool, str]:
    """RULE-06: Date must not be more than max_years in the past (sanity check)."""
    if not date_iso:
        return True, "RULE-06 SKIP: No date for staleness check."
    try:
        txn_date = datetime.strptime(date_iso, "%Y-%m-%d").date()
        age_years = (date.today() - txn_date).days / 365.25
        if age_years > max_years:
            return False, (
                f"RULE-06 WARN: Transaction date {date_iso} is over "
                f"{max_years} years ago ({age_years:.1f} yrs)."
            )
        return True, f"RULE-06 PASS: Date age {age_years:.1f} years is within {max_years}-year window."
    except ValueError:
        return True, "RULE-06 SKIP: Date parse failed."


# ---------------------------------------------------------------------------
# 3. UTR / Transaction ID validators
# ---------------------------------------------------------------------------

def check_utr_present(utr: Optional[str]) -> Tuple[bool, str]:
    """RULE-07: UTR/Transaction ID must be present."""
    if not utr:
        return False, "RULE-07 FAIL: UTR / Transaction ID is missing."
    return True, "RULE-07 PASS: UTR field present."


def check_utr_numeric(utr: Optional[str]) -> Tuple[bool, str]:
    """
    RULE-08: Standard UPI UTR must be purely numeric.
    Alphanumeric prefixes (e.g. 'UTR2719583', 'UTRS614226') indicate
    a tampered or non-standard transaction reference.
    """
    if not utr:
        return False, "RULE-08 SKIP: UTR not available."
    if not _NUMERIC_RE.match(utr):
        return False, (
            f"RULE-08 FAIL: UTR '{utr}' contains non-numeric characters. "
            f"Standard UPI UTRs are 12-digit numeric strings."
        )
    return True, f"RULE-08 PASS: UTR '{utr}' is purely numeric."


def check_utr_length(utr: Optional[str], expected: int = _STANDARD_UTR_LENGTH) -> Tuple[bool, str]:
    """
    RULE-09: Numeric UTR must be exactly 12 digits (NPCI standard).
    Tampered receipts typically show truncated 7-10 digit UTRs prefixed with 'UTR'.
    """
    if not utr:
        return False, "RULE-09 SKIP: UTR not available for length check."
    digits_only = re.sub(r'\D', '', utr)
    if len(digits_only) != expected:
        return False, (
            f"RULE-09 FAIL: UTR has {len(digits_only)} digits; "
            f"expected {expected}. Possible truncation or tamper."
        )
    return True, f"RULE-09 PASS: UTR has correct {expected}-digit length."


# ---------------------------------------------------------------------------
# 4. Status / Completeness validators
# ---------------------------------------------------------------------------

def check_status_present(status: Optional[str]) -> Tuple[bool, str]:
    """RULE-10: Receipt must carry a recognisable payment success status."""
    valid = {"Paid Successfully", "Transaction Successful", "Payment Confirmed",
             "COMPLETED", "SUCCESS"}
    if not status or status == "Unknown":
        return False, "RULE-10 FAIL: Payment status is missing or unrecognised."
    if status not in valid:
        return False, f"RULE-10 WARN: Status '{status}' is not a standard success indicator."
    return True, f"RULE-10 PASS: Status '{status}' is a valid success indicator."


def check_recipient_present(recipient: Optional[str]) -> Tuple[bool, str]:
    """RULE-11: Recipient name must be present."""
    if not recipient:
        return False, "RULE-11 WARN: Recipient name could not be extracted."
    return True, f"RULE-11 PASS: Recipient '{recipient}' extracted."
