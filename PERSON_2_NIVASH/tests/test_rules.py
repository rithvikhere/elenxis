"""
Unit Tests: Rule-Based Validation Engine & Consistency Validators (Phase 7).
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

from datetime import date
from pathlib import Path
import pytest

from src.ocr import extract_transaction_fields
from src.rules import validate_transaction
from src.rules.validators import (
    check_amount_present, check_amount_positive, check_amount_range,
    check_date_not_future, check_utr_numeric, check_utr_length,
    check_status_present, check_recipient_present,
)
from src.utils.paths import DATA_DIR, RAW_DIR, PROCESSED_DIR

REF_DATE = date(2026, 9, 17)  # Fixed reference date for deterministic testing


# ---------------------------------------------------------------------------
# Validator Unit Tests
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
# Integration Tests on Dataset Images
# ---------------------------------------------------------------------------

class TestRuleEngineOnImages:
    def test_original_paylite_is_legitimate(self):
        ocr = extract_transaction_fields(RAW_DIR / "tpl1_src001_none_01.png")
        r = validate_transaction(ocr, reference_date=REF_DATE)
        assert r["verdict"] == "LIKELY_LEGITIMATE"
        assert r["suspicion_score"] < 0.25

    def test_original_quickpe_is_legitimate(self):
        ocr = extract_transaction_fields(RAW_DIR / "tpl2_src021_none_01.png")
        r = validate_transaction(ocr, reference_date=REF_DATE)
        assert r["verdict"] == "LIKELY_LEGITIMATE"

    def test_original_unipay_is_legitimate(self):
        ocr = extract_transaction_fields(RAW_DIR / "tpl3_src041_none_01.png")
        r = validate_transaction(ocr, reference_date=REF_DATE)
        assert r["verdict"] == "LIKELY_LEGITIMATE"

    def test_date_tamper_is_suspicious(self):
        ocr = extract_transaction_fields(PROCESSED_DIR / "tpl1_src001_date_change_01.png")
        r = validate_transaction(ocr, reference_date=REF_DATE)
        assert r["verdict"] == "SUSPICIOUS"
        assert any("FUTURE" in v or "future" in v for v in r["violations"])

    def test_result_has_all_keys(self):
        ocr = extract_transaction_fields(RAW_DIR / "tpl1_src001_none_01.png")
        r = validate_transaction(ocr, reference_date=REF_DATE)
        for key in ("verdict", "suspicion_score", "violations",
                    "warnings", "passed_checks", "explanation", "fields_used"):
            assert key in r

    def test_unreadable_input(self):
        r = validate_transaction(
            {"fields": {}, "success": False, "raw_text": "", "mean_confidence": 0, "error": "bad file"}
        )
        assert r["verdict"] == "UNREADABLE"
        assert r["suspicion_score"] == 1.0
