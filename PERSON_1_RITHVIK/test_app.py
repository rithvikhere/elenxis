import pathlib
from streamlit.testing.v1 import AppTest

def test_initial_state():
    """Test 1: No file uploaded, page just loaded."""
    at = AppTest.from_file("../app.py", default_timeout=10).run()
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

def test_valid_png_upload():
    """Test 2: Valid PNG upload."""
    at = AppTest.from_file("../app.py", default_timeout=10).run()
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
    
    # Click button
    at.button[0].click().run()
    assert any("Analysis modules will be wired in during Phase 4/5" in info.value for info in at.info)
    print("[PASS] Test 2: Valid PNG upload and analyze click verified.")

def test_valid_jpg_upload():
    """Test 3: Valid JPG upload."""
    at = AppTest.from_file("../app.py", default_timeout=10).run()
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
    at = AppTest.from_file("../app.py", default_timeout=10).run()
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
    at = AppTest.from_file("../app.py", default_timeout=10).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    # Upload
    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.image) == 1
    assert len(at.button) == 1
    
    # Remove file (simulates clicking the remove button in Streamlit file_uploader)
    at.file_uploader[0].clear().run()
    
    assert len(at.image) == 0
    assert len(at.button) == 0
    assert len(at.error) == 0
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    print("[PASS] Test 5: File upload and removal reset verified.")

if __name__ == "__main__":
    test_initial_state()
    test_valid_png_upload()
    test_valid_jpg_upload()
    test_corrupted_file_upload()
    test_file_removal()
    print("\nALL 5 TEST SCENARIOS PASSED!")
