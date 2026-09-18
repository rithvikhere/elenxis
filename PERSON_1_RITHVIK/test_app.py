import pathlib
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

def test_initial_state():
    """Test 1: No file uploaded, page just loaded."""
    at = AppTest.from_file("../app.py", default_timeout=15).run()
    assert at.title[0].value == "UPI Fraud Forensics"
    assert at.caption[0].value == "Screenshot-based forensic analysis for detecting potential manipulation indicators."
    assert len(at.file_uploader) == 1
    # Check neutral info message is displayed
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    # Check no analyze button is shown
    assert len(at.button) == 0
    # No error
    assert len(at.error) == 0
    print("[PASS] Test 1: Initial empty state verified.")

def test_valid_png_upload_and_analysis():
    """Test 2: Valid PNG upload and execution of Person 2 OCR + Rule Engine."""
    at = AppTest.from_file("../app.py", default_timeout=25).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.error) == 0
    assert len(at.image) == 1
    assert "sample_family1_paylite.png" in at.image[0].captions[0]
    
    # Check button appears
    assert len(at.button) == 1
    assert at.button[0].label == "Analyze Screenshot"
    
    # Click Analyze Screenshot button
    at.button[0].click().run()
    
    # Verify subheaders are rendered
    subheader_values = [sh.value for sh in at.subheader]
    assert "OCR Extracted Fields" in subheader_values
    assert "Rule Validation" in subheader_values
    
    # Verify markdown contents for OCR fields
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "**Amount:**" in all_markdown
    assert "**Date:**" in all_markdown
    assert "**Time:**" in all_markdown
    assert "**UTR:**" in all_markdown
    assert "**Template:**" in all_markdown
    assert "**Recipient:**" in all_markdown
    
    # Verify markdown contents for Rule Validation
    assert "**Verdict:**" in all_markdown
    assert "**Anomaly Score:**" in all_markdown
    assert "**Rule Explanations:**" in all_markdown
    
    # In sample_family1_paylite.png, recipient is null in ground truth/sample, so check "Not detected"
    assert "Not detected" in all_markdown
    
    print("[PASS] Test 2: Valid PNG upload and Person 2 analysis verified.")

def test_valid_jpg_upload():
    """Test 3: Valid JPG upload."""
    at = AppTest.from_file("../app.py", default_timeout=15).run()
    sample_jpg = pathlib.Path("PERSON_3_SANJAY/results/ela/recompressed_original.jpg")
    with open(sample_jpg, "rb") as f:
        jpg_bytes = f.read()
    
    at.file_uploader[0].upload(filename="recompressed_original.jpg", content=jpg_bytes).run()
    assert len(at.error) == 0
    assert len(at.image) == 1
    assert "recompressed_original.jpg" in at.image[0].captions[0]
    assert len(at.button) == 1
    print("[PASS] Test 3: Valid JPG upload verified.")

def test_corrupted_file_upload():
    """Test 4: Non-image file renamed to .png."""
    at = AppTest.from_file("../app.py", default_timeout=15).run()
    corrupted_bytes = b"This is plain text pretending to be a PNG file."
    
    at.file_uploader[0].upload(filename="scratch_invalid.png", content=corrupted_bytes).run()
    assert len(at.error) == 1
    assert "not a valid or readable image" in at.error[0].value
    # No preview image
    assert len(at.image) == 0
    # No button
    assert len(at.button) == 0
    print("[PASS] Test 4: Corrupted file error handling verified.")

def test_file_removal():
    """Test 5: Uploading, then removing the file."""
    at = AppTest.from_file("../app.py", default_timeout=15).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    # Upload
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.image) == 1
    assert len(at.button) == 1
    
    # Remove file (simulates clicking remove button in Streamlit)
    at.file_uploader[0].clear().run()
    
    assert len(at.image) == 0
    assert len(at.button) == 0
    assert len(at.error) == 0
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    print("[PASS] Test 5: File upload and removal reset verified.")

def test_exception_fallback():
    """Test 6: Simulated exception in module execution displays 'Not available yet'."""
    at = AppTest.from_file("../app.py", default_timeout=15).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    
    # Simulate an error during extract_transaction_fields by patching it to raise an exception
    with patch("src.ocr.extract_transaction_fields", side_effect=RuntimeError("Simulated OCR failure")):
        at.button[0].click().run()
        
    # App must not crash, and should display "Not available yet" for failed sections
    assert len(at.exception) == 0
    assert any("Not available yet" in info.value for info in at.info)
    print("[PASS] Test 6: Exception graceful fallback verified.")

if __name__ == "__main__":
    test_initial_state()
    test_valid_png_upload_and_analysis()
    test_valid_jpg_upload()
    test_corrupted_file_upload()
    test_file_removal()
    test_exception_fallback()
    print("\nALL 6 PHASE 4 TEST SCENARIOS PASSED!")
