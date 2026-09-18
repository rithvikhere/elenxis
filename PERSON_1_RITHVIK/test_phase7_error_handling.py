import io
import os
import pathlib
import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

def test_case_1_non_image_file():
    """Case 1: Non-image file renamed to .png (text bytes)."""
    at = AppTest.from_file("../app.py", default_timeout=25).run()
    corrupted_bytes = b"This is a text file pretending to be a PNG screenshot."
    at.file_uploader[0].upload(filename="fake_screenshot.png", content=corrupted_bytes).run()
    
    # Verify st.error is displayed
    assert len(at.error) == 1
    assert "not a valid or readable image" in at.error[0].value
    # Verify button cannot be rendered/clicked
    assert len(at.button) == 0
    # Zero unhandled exceptions
    assert len(at.exception) == 0
    print("[PASS] Case 1: Non-image file handled with clear st.error.")

def test_case_2_truncated_image():
    """Case 2: Corrupted image file (truncated PNG byte stream)."""
    at = AppTest.from_file("../app.py", default_timeout=25).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()
    
    # Truncate to just the first 50 bytes (broken header/stream)
    truncated_bytes = png_bytes[:50]
    at.file_uploader[0].upload(filename="truncated_screenshot.png", content=truncated_bytes).run()
    
    assert len(at.error) == 1
    assert "not a valid or readable image" in at.error[0].value
    assert len(at.button) == 0
    assert len(at.exception) == 0
    print("[PASS] Case 2: Truncated/corrupted image handled with clear st.error.")

def test_case_3_very_small_image():
    """Case 3: Very low-resolution image (10x10 px)."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    # Create 10x10 image in memory
    img = Image.new("RGB", (10, 10), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    small_bytes = buf.getvalue()
    
    at.file_uploader[0].upload(filename="small_10x10.png", content=small_bytes).run()
    assert len(at.error) == 0
    assert len(at.button) == 1
    
    at.button[0].click().run()
    
    all_markdown = " ".join(m.value for m in at.markdown)
    # OCR fields should all be "Not detected"
    assert "**Amount:** Not detected" in all_markdown
    assert "**Date:** Not detected" in all_markdown
    assert "**Time:** Not detected" in all_markdown
    assert "**UTR:** Not detected" in all_markdown
    
    # Rule verdict handles unreadable/suspicious gracefully
    assert any(v in all_markdown for v in ("**Verdict:** UNREADABLE", "**Verdict:** SUSPICIOUS"))
    
    # Combined assessment produces a valid status without crash
    assert any(s in all_markdown for s in ("- **Status:** Suspicious signals detected", "- **Status:** Insufficient evidence / unable to analyze reliably"))
    assert len(at.exception) == 0
    print("[PASS] Case 3: 10x10 px image handled without crash; fields show 'Not detected'.")

def test_case_4_no_text_image():
    """Case 4: Image with no extractable text (200x200 blank image)."""
    at = AppTest.from_file("../app.py", default_timeout=35).run()
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    blank_bytes = buf.getvalue()
    
    at.file_uploader[0].upload(filename="blank_white.png", content=blank_bytes).run()
    at.button[0].click().run()
    
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "**Amount:** Not detected" in all_markdown
    assert "**Date:** Not detected" in all_markdown
    assert "**Time:** Not detected" in all_markdown
    assert "**UTR:** Not detected" in all_markdown
    assert "**Recipient:** Not detected" in all_markdown
    assert len(at.exception) == 0
    print("[PASS] Case 4: Blank image produces 'Not detected' per field without crash.")

def test_case_5_missing_checkpoint():
    """Case 5: Missing CNN model checkpoint file."""
    ckpt_path = pathlib.Path("PERSON_3_SANJAY/models/resnet18_baseline_best.pt")
    bak_path = pathlib.Path("PERSON_3_SANJAY/models/resnet18_baseline_best.pt.simulated_missing")
    
    assert ckpt_path.exists(), "Original checkpoint must exist before running test."
    
    try:
        # Temporarily rename to simulate missing checkpoint
        ckpt_path.rename(bak_path)
        
        at = AppTest.from_file("../app.py", default_timeout=35).run()
        sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
        with open(sample_png, "rb") as f:
            png_bytes = f.read()
        
        at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
        at.button[0].click().run()
        
        all_markdown = " ".join(m.value for m in at.markdown)
        all_info = " ".join(i.value for i in at.info)
        
        # Sections that require checkpoint should show "Not available yet"
        assert "Not available yet" in all_info
        # Combined assessment falls back to insufficient evidence
        assert "- **Status:** Insufficient evidence / unable to analyze reliably" in all_markdown
        assert "*Based on: rule engine only — CNN unavailable*" in all_markdown
        assert len(at.exception) == 0
        print("[PASS] Case 5: Missing checkpoint handled with 'Not available yet' fallback.")
    finally:
        # Guarantee restoration of original checkpoint
        if bak_path.exists():
            bak_path.rename(ckpt_path)
        assert ckpt_path.exists(), "Checkpoint must be restored after test."
        print("[RESTORED] Checkpoint restored to original path.")

def test_case_6_no_file_uploaded():
    """Case 6: No file uploaded at all — confirm button cannot be reached and neutral info is shown."""
    at = AppTest.from_file("../app.py", default_timeout=20).run()
    
    # Button is not visible or clickable
    assert len(at.button) == 0
    # Neutral info prompt is shown
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    # No error or crash
    assert len(at.error) == 0
    assert len(at.exception) == 0
    print("[PASS] Case 6: No file state shows neutral prompt; Analyze button unreachable.")

if __name__ == "__main__":
    test_case_1_non_image_file()
    test_case_2_truncated_image()
    test_case_3_very_small_image()
    test_case_4_no_text_image()
    test_case_5_missing_checkpoint()
    test_case_6_no_file_uploaded()
    print("\nALL 6 ERROR HANDLING CASES PASSED!")
