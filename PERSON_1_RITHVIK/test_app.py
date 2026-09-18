import pathlib
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

def test_initial_state():
    """Test 1: No file uploaded, page just loaded."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
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

def test_valid_png_upload_and_full_pipeline():
    """Test 2: Valid PNG upload and execution of Person 2 & Person 3 pipelines."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.error) == 0
    assert len(at.image) >= 1
    
    # Click Analyze Screenshot button
    at.button[0].click().run()
    
    # Verify subheaders are rendered
    subheader_values = [sh.value for sh in at.subheader]
    assert "OCR Extracted Fields" in subheader_values
    assert "Rule Validation" in subheader_values
    assert "CNN Visual Classification" in subheader_values
    assert "Image Forensics" in subheader_values
    assert "Model Explainability (Grad-CAM)" in subheader_values
    
    all_markdown = " ".join(m.value for m in at.markdown)
    all_captions = " ".join(c.value for c in at.caption)
    
    # 1. OCR verification
    assert "**Amount:**" in all_markdown
    assert "**Date:**" in all_markdown
    assert "**Time:**" in all_markdown
    assert "**UTR:**" in all_markdown
    assert "**Template:**" in all_markdown
    assert "**Recipient:**" in all_markdown
    
    # 2. Rules verification
    assert "**Verdict:**" in all_markdown
    assert "**Anomaly Score:**" in all_markdown
    assert "**Rule Explanations:**" in all_markdown
    
    # 3. CNN verification
    assert "**Predicted Class:**" in all_markdown
    assert "**Probability:**" in all_markdown
    assert "Prediction from a small baseline model — accuracy 0.75, recall 1.00 on a 12-image held-out test set." in all_captions
    
    # 4. Forensics verification
    assert "#### Error Level Analysis (ELA)" in all_markdown
    assert "#### Metadata & EXIF Analysis" in all_markdown
    assert "ELA and metadata are evidence for inspection, not proof of manipulation." in all_captions
    assert "Missing EXIF is normal for screenshots and shared images and is not itself suspicious." in all_captions
    
    # 5. Grad-CAM verification
    assert "Highlights regions that influenced the model's prediction — not proof that a region was edited." in all_captions
    
    print("[PASS] Test 2: Full pipeline (Person 2 + Person 3) verified.")

def test_corrupted_file_upload():
    """Test 3: Non-image file renamed to .png."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
    corrupted_bytes = b"This is plain text pretending to be a PNG file."
    
    at.file_uploader[0].upload(filename="scratch_invalid.png", content=corrupted_bytes).run()
    assert len(at.error) == 1
    assert "not a valid or readable image" in at.error[0].value
    assert len(at.button) == 0
    print("[PASS] Test 3: Corrupted file error handling verified.")

def test_file_removal():
    """Test 4: Uploading, then removing the file."""
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
    print("[PASS] Test 4: File removal reset verified.")

def test_independent_graceful_degradation():
    """Test 5: Independent graceful degradation when one Person 3 call fails."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    
    # Simulate Grad-CAM failure while CNN and OCR succeed
    with patch("PERSON_3_SANJAY.src.explainability.gradcam.generate_gradcam", side_effect=RuntimeError("Grad-CAM failure")):
        at.button[0].click().run()
    
    # App must not crash
    assert len(at.exception) == 0
    subheader_values = [sh.value for sh in at.subheader]
    assert "OCR Extracted Fields" in subheader_values
    assert "CNN Visual Classification" in subheader_values
    assert "Model Explainability (Grad-CAM)" in subheader_values
    
    # Grad-CAM displays "Not available yet", but other components succeeded
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "**Predicted Class:**" in all_markdown
    assert any("Not available yet" in info.value for info in at.info)
    print("[PASS] Test 5: Independent graceful degradation verified.")

if __name__ == "__main__":
    test_initial_state()
    test_valid_png_upload_and_full_pipeline()
    test_corrupted_file_upload()
    test_file_removal()
    test_independent_graceful_degradation()
    print("\nALL 5 PHASE 5 TESTS PASSED!")
