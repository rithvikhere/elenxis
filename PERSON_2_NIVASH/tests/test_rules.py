"""
Unit Tests: Rule Engine + Validators.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

import sys
from datetime import date
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr import extract_transaction_fields
from src.rules import validate_transaction
from src.rules.validators import (
    check_amount_present, check_amount_positive, check_amount_range,
    check_date_not_future, check_utr_numeric, check_utr_length,
    check_status_present, check_recipient_present,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
REF_DATE = date(2026, 9, 17)  # Fixed reference date for deterministic tests


# ---------------------------------------------------------------------------
# Validator unit tests
# ---------------------------------------------------------------------------

class TestAmountValidators:
    def test_present_passes(self):
        ok, _ = check_amount_present("₹450.00")
        assert ok is True

    def test_none_fails(self):
        ok, _ = check_amount_present(None)
        assert ok is False

    def test_positive_passes(self):
        ok, _ = check_amount_positive(450.0)
        assert ok is True

    def test_zero_fails(self):
        ok, _ = check_amount_positive(0.0)
        assert ok is False

    def test_negative_fails(self):
        ok, _ = check_amount_positive(-100.0)
        assert ok is False

    def test_range_within_bounds(self):
        ok, _ = check_amount_range(450.0)
        assert ok is True

    def test_range_above_limit(self):
        ok, msg = check_amount_range(200_000.0)
        assert ok is False
        assert "plausible" in msg.lower()


class TestDateValidators:
    def test_past_date_passes(self):
        ok, _ = check_date_not_future("2026-03-12", reference=REF_DATE)
        assert ok is True

    def test_today_passes(self):
        ok, _ = check_date_not_future(REF_DATE.strftime("%Y-%m-%d"), reference=REF_DATE)
        assert ok is True

    def test_future_date_fails(self):
        ok, msg = check_date_not_future("2029-12-28", reference=REF_DATE)
        assert ok is False
        assert "FUTURE" in msg

    def test_none_date_fails(self):
        ok, _ = check_date_not_future(None, reference=REF_DATE)
        assert ok is False


class TestUtrValidators:
    def test_numeric_utr_passes(self):
        ok, _ = check_utr_numeric("425631219101")
        assert ok is True

    def test_alpha_prefix_fails(self):
        ok, msg = check_utr_numeric("UTR2719583")
        assert ok is False
        assert "non-numeric" in msg.lower()

    def test_correct_length_passes(self):
        ok, _ = check_utr_length("425631219101")
        assert ok is True

    def test_short_utr_fails(self):
        ok, msg = check_utr_length("UTR2719583")
        assert ok is False
        assert "digit" in msg.lower()

    def test_none_utr_fails(self):
        ok, _ = check_utr_numeric(None)
        assert ok is False


# ---------------------------------------------------------------------------
# Full rule engine integration tests (on actual images)
# ---------------------------------------------------------------------------

class TestRuleEngineOnImages:
    def _ocr_and_validate(self, img_num: int) -> dict:
        ocr = extract_transaction_fields(str(DATA_DIR / f"img_{img_num:03d}.png"))
        return validate_transaction(ocr, reference_date=REF_DATE)

    def test_original_apex_is_legitimate(self):
        r = self._ocr_and_validate(1)
        assert r["verdict"] == "LIKELY_LEGITIMATE"
        assert r["suspicion_score"] < 0.25

    def test_original_zenith_is_legitimate(self):
        r = self._ocr_and_validate(5)
        assert r["verdict"] == "LIKELY_LEGITIMATE"

    def test_original_nova_is_legitimate(self):
        r = self._ocr_and_validate(9)
        assert r["verdict"] == "LIKELY_LEGITIMATE"

    def test_date_tamper_apex_is_suspicious(self):
        r = self._ocr_and_validate(3)
        assert r["verdict"] == "SUSPICIOUS"
        assert any("FUTURE" in v or "future" in v for v in r["violations"])

    def test_utr_tamper_apex_is_suspicious(self):
        r = self._ocr_and_validate(4)
        assert r["verdict"] == "SUSPICIOUS"

    def test_utr_tamper_zenith_is_suspicious(self):
        r = self._ocr_and_validate(8)
        assert r["verdict"] == "SUSPICIOUS"

    def test_result_has_all_keys(self):
        r = self._ocr_and_validate(1)
        for key in ("verdict", "suspicion_score", "violations",
                    "warnings", "passed_checks", "explanation", "fields_used"):
            assert key in r

    def test_unreadable_input(self):
        r = validate_transaction(
            {"fields": {}, "success": False, "raw_text": "", "mean_confidence": 0, "error": "bad file"}
        )
        assert r["verdict"] == "UNREADABLE"
        assert r["suspicion_score"] == 1.0
