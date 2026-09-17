"""
Unit Tests: OCR Extractor (end-to-end pipeline).
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

import sys
from pathlib import Path
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr import extract_transaction_fields

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


class TestExtractorOnRealImages:
    def test_apex_original(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_001.png"))
        assert r["success"] is True
        assert r["fields"]["amount"] == "₹450.00"
        assert r["fields"]["date"] == "12 Mar 2026"
        assert r["fields"]["transaction_id"] == "425631219101"
        assert r["fields"]["recipient"] == "Metro Book Store"
        assert r["mean_confidence"] > 70

    def test_zenith_original(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_005.png"))
        assert r["success"] is True
        assert r["fields"]["amount"] == "₹1,200.00"
        assert r["fields"]["date"] == "14 Mar 2026"

    def test_nova_original(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_009.png"))
        assert r["success"] is True
        assert r["fields"]["date"] == "15 Mar 2026"
        assert r["fields"]["transaction_id"] == "486846326096"

    def test_date_tamper_detected(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_003.png"))
        assert r["fields"]["date"] == "28 Dec 2029"

    def test_utr_tamper_detected(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_004.png"))
        utr = r["fields"]["transaction_id"]
        assert utr is not None
        import re
        assert not re.match(r'^\d{12}$', utr), "Tampered UTR should not be a clean 12-digit number"

    def test_amount_tamper(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_002.png"))
        assert r["success"] is True
        val = r["fields"]["amount_value"]
        assert val is not None and val > 10000  # Tampered to a large value


class TestExtractorEdgeCases:
    def test_missing_file_returns_error(self):
        r = extract_transaction_fields("/does/not/exist.png")
        assert r["success"] is False
        assert r["error"] is not None

    def test_blank_white_image(self):
        blank = Image.new("RGB", (540, 800), "white")
        r = extract_transaction_fields(blank)
        # Should not crash; might succeed=False since no fields
        assert isinstance(r["success"], bool)
        assert r["error"] is None  # No exception

    def test_result_keys_always_present(self):
        r = extract_transaction_fields(str(DATA_DIR / "img_001.png"))
        for key in ("fields", "raw_text", "mean_confidence",
                    "preprocess_mode", "image_path", "success", "error"):
            assert key in r

    def test_preprocess_modes_do_not_crash(self):
        img_path = str(DATA_DIR / "img_001.png")
        for mode in ("raw", "grayscale", "contrast", "otsu", "threshold", "denoise"):
            r = extract_transaction_fields(img_path, preprocess_mode=mode)
            assert isinstance(r["success"], bool), f"mode={mode} crashed"
