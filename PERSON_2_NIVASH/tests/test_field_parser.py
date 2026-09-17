"""
Unit Tests: Field Parser Module.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr.field_parser import (
    parse_amount, parse_date, parse_time,
    parse_utr, parse_template_type, parse_recipient,
    parse_transaction_status, parse_all_fields,
)


class TestParseAmount:
    def test_rupee_symbol(self):
        assert parse_amount("₹450.00")[0] == "₹450.00"

    def test_percent_ocr_misread(self):
        assert parse_amount("%450.00")[0] == "₹450.00"

    def test_comma_thousands(self):
        result, val = parse_amount("1,200.00")
        assert result == "₹1,200.00"
        assert val == 1200.0

    def test_rs_prefix(self):
        result, val = parse_amount("Rs. 899.00")
        assert val == 899.0

    def test_large_tampered_amount(self):
        result, val = parse_amount("%23278.99")
        assert val == pytest.approx(23278.99)

    def test_no_amount_returns_none(self):
        result, val = parse_amount("Hello World\nNo money here")
        assert result is None
        assert val is None

    def test_empty_string(self):
        assert parse_amount("") == (None, None)

    def test_amount_below_range_excluded(self):
        # 0.10 is below 0.5 minimum — should not be extracted
        result, _ = parse_amount("₹0.10")
        assert result is None


class TestParseDate:
    def test_named_month_format(self):
        d, iso = parse_date("Payment Date 12 Mar 2026")
        assert d == "12 Mar 2026"
        assert iso == "2026-03-12"

    def test_future_date(self):
        d, iso = parse_date("Date 28 Dec 2029")
        assert d == "28 Dec 2029"
        assert iso == "2029-12-28"

    def test_no_date(self):
        assert parse_date("No date in this text")[0] is None

    def test_case_insensitive_month(self):
        d, iso = parse_date("14 mar 2026")
        assert iso == "2026-03-14"


class TestParseTime:
    def test_12h_am(self):
        assert parse_time("Time 10:15 AM") == "10:15 AM"

    def test_12h_pm(self):
        assert parse_time("Time 02:45 PM") == "02:45 PM"

    def test_24h(self):
        t = parse_time("Time 14:30")
        assert t is not None

    def test_no_time(self):
        assert parse_time("No temporal info here") is None


class TestParseUtr:
    def test_standard_12_digit(self):
        assert parse_utr("UPI Ref (UTR) 425631219101") == "425631219101"

    def test_tampered_alpha_prefix(self):
        val = parse_utr("UPI Transaction ID UTR2719583")
        assert val == "UTR2719583"

    def test_standalone_12_digit(self):
        assert parse_utr("486846326096") == "486846326096"

    def test_no_utr(self):
        assert parse_utr("No transaction info") is None

    def test_utr_number_label(self):
        val = parse_utr("UTR Number UTR8078673")
        assert val == "UTR8078673"


class TestParseTemplateType:
    def test_apex(self):
        assert parse_template_type("ApexPay UPI") == "ApexPay"

    def test_zenith(self):
        assert parse_template_type("ZenithUPI Instant Transfer") == "ZenithUPI"

    def test_nova(self):
        assert parse_template_type("NovaPay Transfer") == "NovaPay"

    def test_generic_fallback(self):
        assert parse_template_type("Unknown App") == "GenericUPI"


class TestParseAllFields:
    def test_returns_all_keys(self):
        fields = parse_all_fields("ApexPay UPI\n%450.00\n12 Mar 2026\n10:15 AM\n425631219101\nMetro Book Store")
        for key in ("amount", "amount_value", "date", "date_iso", "time",
                    "transaction_id", "template_type", "recipient", "status", "raw_text"):
            assert key in fields

    def test_empty_string_does_not_crash(self):
        fields = parse_all_fields("")
        assert fields["amount"] is None
        assert fields["date"] is None
