"""
Unit Tests: OCR Extractor (End-to-End Pipeline — Phase 5).
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

from pathlib import Path
import pytest
from PIL import Image

from src.ocr import extract_transaction_fields
from src.utils.paths import RAW_DIR


class TestExtractorOnRealImages:
    def test_paylite_family1_original(self):
        r = extract_transaction_fields(RAW_DIR / "tpl1_src001_none_01.png")
        assert r["success"] is True
        assert r["fields"]["amount_value"] is not None
        assert r["fields"]["date"] is not None
        assert r["fields"]["transaction_id"] == "321819600133"
        assert r["fields"]["template_type"] == "PayLite"
        assert r["mean_confidence"] > 50

    def test_quickpe_family2_original(self):
        r = extract_transaction_fields(RAW_DIR / "tpl2_src021_none_01.png")
        assert r["success"] is True
        assert r["fields"]["amount_value"] == 12967.28
        assert r["fields"]["transaction_id"] == "874016400524"
        assert r["fields"]["template_type"] == "QuickPe"

    def test_unipay_family3_original(self):
        r = extract_transaction_fields(RAW_DIR / "tpl3_src041_none_01.png")
        assert r["success"] is True
        assert r["fields"]["amount_value"] == 2982.48
        assert r["fields"]["transaction_id"] == "737996507527"
        assert r["fields"]["template_type"] == "UniPay"
        assert r["fields"]["status"] == "SUCCESS"


class TestExtractorEdgeCases:
    def test_missing_file_returns_error(self):
        r = extract_transaction_fields("/does/not/exist.png")
        assert r["success"] is False
        assert r["error"] is not None

    def test_blank_white_image(self):
        blank = Image.new("RGB", (400, 800), "white")
        r = extract_transaction_fields(blank)
        assert isinstance(r["success"], bool)
        assert r["error"] is None

    def test_result_keys_always_present(self):
        r = extract_transaction_fields(RAW_DIR / "tpl1_src001_none_01.png")
        for key in ("fields", "raw_text", "mean_confidence",
                    "preprocess_mode", "image_path", "success", "error"):
            assert key in r

    def test_preprocess_modes_do_not_crash(self):
        img_path = RAW_DIR / "tpl1_src001_none_01.png"
        for mode in ("raw", "grayscale", "contrast", "otsu", "threshold", "denoise"):
            r = extract_transaction_fields(img_path, preprocess_mode=mode)
            assert isinstance(r["success"], bool), f"mode={mode} crashed"
