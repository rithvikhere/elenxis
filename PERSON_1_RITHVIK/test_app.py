import pathlib
import logging
import warnings
from unittest.mock import patch
from streamlit import logger as st_logger
import streamlit.runtime.scriptrunner_utils.script_run_context as st_context
from streamlit.testing.v1 import AppTest

# Suppress Streamlit runtime warnings and ResourceWarnings during test runs
st_logger.set_log_level("ERROR")
st_context._LOGGER.disabled = True
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def test_initial_state():
    """Test 1: No file uploaded, page just loaded."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
    assert at.title[0].value == "UPI Fraud Forensics"
    assert at.caption[0].value == "Screenshot-based forensic analysis for detecting potential manipulation indicators."
    assert len(at.file_uploader) == 1
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    assert len(at.button) == 0
    assert len(at.error) == 0
    print("[PASS] Test 1: Initial empty state verified.")

def test_combined_assessment_suspicious_state():
    """Test 2: At least one suspicious signal -> 'Suspicious signals detected'."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    at.button[0].click().run()
    
    all_markdown = " ".join(m.value for m in at.markdown)
    all_captions = " ".join(c.value for c in at.caption)
    
    # Check Section header exists
    subheader_values = [sh.value for sh in at.subheader]
    assert "Combined Assessment" in subheader_values
    
    # Verify status is exactly "Suspicious signals detected"
    assert "- **Status:** Suspicious signals detected" in all_markdown
    assert "*Based on: rule engine, CNN*" in all_markdown
    assert "Provisional combined signal — not a calibrated ensemble. Full ensemble scoring is planned for a later milestone." in all_captions
    
    # Contract check: strictly never output forbidden words
    assert "FAKE" not in all_markdown
    assert "FRAUD" not in all_markdown
    print("[PASS] Test 2: Combined Assessment 'Suspicious signals detected' verified.")

def test_combined_assessment_clean_state():
    """Test 3: Both signals clean -> 'No suspicious signals detected'."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    
    # Mock rule verdict as LIKELY_LEGITIMATE and CNN as original
    clean_rule_mock = {
        "verdict": "LIKELY_LEGITIMATE",
        "suspicion_score": 0.05,
        "violations": [],
        "warnings": [],
        "passed_checks": ["RULE-01 PASS: All rules passed"],
    }
    clean_cnn_mock = {
        "status": "success",
        "class": "original",
        "label": "original",
        "probability": 0.95,
        "available": True,
    }
    
    with patch("src.rules.validate_transaction", return_value=clean_rule_mock), \
         patch("PERSON_3_SANJAY.src.api.predict", return_value=clean_cnn_mock):
        at.button[0].click().run()
        
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "- **Status:** No suspicious signals detected" in all_markdown
    assert "*Based on: rule engine, CNN*" in all_markdown
    print("[PASS] Test 3: Combined Assessment 'No suspicious signals detected' verified.")

def test_combined_assessment_unavailable_state():
    """Test 4: One or both modules fail/unavailable -> 'Insufficient evidence / unable to analyze reliably'."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    
    # Simulate CNN failure while rule engine succeeds
    with patch("PERSON_3_SANJAY.src.api.predict", side_effect=RuntimeError("CNN service down")):
        at.button[0].click().run()
        
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "- **Status:** Insufficient evidence / unable to analyze reliably" in all_markdown
    assert "*Based on: rule engine only — CNN unavailable*" in all_markdown
    print("[PASS] Test 4: Combined Assessment partial failure handled reliably.")

def test_combined_assessment_both_unavailable_state():
    """Test 5: Both modules fail -> 'Insufficient evidence / unable to analyze reliably' and 'Based on: none available.'"""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    
    with patch("src.ocr.extract_transaction_fields", side_effect=RuntimeError("OCR down")), \
         patch("PERSON_3_SANJAY.src.api.predict", side_effect=RuntimeError("CNN down")):
        at.button[0].click().run()
        
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "- **Status:** Insufficient evidence / unable to analyze reliably" in all_markdown
    assert "*Based on: none available.*" in all_markdown
    print("[PASS] Test 5: Combined Assessment both modules unavailable handled without crash.")

def test_corrupted_file_upload():
    """Test 6: Non-image file renamed to .png."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
    corrupted_bytes = b"This is plain text pretending to be a PNG file."
    
    at.file_uploader[0].upload(filename="scratch_invalid.png", content=corrupted_bytes).run()
    assert len(at.error) == 1
    assert "not a valid or readable image" in at.error[0].value
    assert len(at.button) == 0
    print("[PASS] Test 6: Corrupted file error handling verified.")

def test_file_removal():
    """Test 7: Uploading, then removing the file."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.button) == 1
    
    # Clear file
    at.file_uploader[0].clear().run()
    assert len(at.button) == 0
    assert len(at.error) == 0
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    print("[PASS] Test 7: File removal reset verified.")

if __name__ == "__main__":
    test_initial_state()
    test_combined_assessment_suspicious_state()
    test_combined_assessment_clean_state()
    test_combined_assessment_unavailable_state()
    test_combined_assessment_both_unavailable_state()
    test_corrupted_file_upload()
    test_file_removal()
    print("\nALL 7 PHASE 6 TESTS PASSED!")
