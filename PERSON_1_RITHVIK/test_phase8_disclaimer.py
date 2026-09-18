import pathlib
from streamlit.testing.v1 import AppTest

DISCLAIMER_EXACT = (
    "This tool analyzes screenshot authenticity signals. It does not verify whether "
    "a bank transaction occurred. Confirm payment through the official payment app or bank account."
)

WATERMARK_TEXT = "DEMO / SYNTHETIC UPI RECEIPT"
SYNTHETIC_TEXT = "synthetic and used for academic purposes only"
METRIC_OCR = "**OCR:** 100% extraction/field accuracy on test split"
METRIC_RULES = "**Rule engine:** 93.9% precision / 68.9% recall overall"
METRIC_CNN = "**CNN:** 0.75 accuracy / 1.00 recall on a 12-image held-out set"

def assert_phase8_elements(at: AppTest):
    """Verify that standing disclaimer and footer elements are present and unparaphrased."""
    # 1. Standing disclaimer must be present in warnings
    all_warnings = " ".join(w.value for w in at.warning)
    assert DISCLAIMER_EXACT in all_warnings, "Exact standing disclaimer not found in st.warning"

    # 2. About & Academic Integrity subheader must be present
    all_subheaders = [sh.value for sh in at.subheader]
    assert "About & Academic Integrity" in all_subheaders, "'About & Academic Integrity' section missing"

    # 3. Footer text elements must be present in markdown
    all_markdown = " ".join(m.value for m in at.markdown)
    assert SYNTHETIC_TEXT in all_markdown, "Synthetic data statement missing"
    assert WATERMARK_TEXT in all_markdown, "Watermark reference missing"
    assert METRIC_OCR in all_markdown, "OCR benchmark metric missing"
    assert METRIC_RULES in all_markdown, "Rule engine benchmark metric missing"
    assert METRIC_CNN in all_markdown, "CNN benchmark metric missing"

def test_state_1_no_file_uploaded():
    """State 1: No file uploaded at all."""
    at = AppTest.from_file("../app.py", default_timeout=25).run()
    assert_phase8_elements(at)
    assert len(at.button) == 0
    assert any("upload a UPI payment screenshot" in info.value for info in at.info)
    print("[PASS] State 1 (No file uploaded): Disclaimer and Integrity Footer verified.")

def test_state_2_file_uploaded_not_analyzed():
    """State 2: File uploaded, preview displayed, not analyzed yet."""
    at = AppTest.from_file("../app.py", default_timeout=25).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()

    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    assert len(at.button) == 1
    assert_phase8_elements(at)
    print("[PASS] State 2 (File uploaded, not analyzed): Disclaimer and Integrity Footer verified.")

def test_state_3_after_full_analysis():
    """State 3: After full analysis run."""
    at = AppTest.from_file("../app.py", default_timeout=40).run()
    sample_png = pathlib.Path("PERSON_2_NIVASH/docs/samples/sample_family1_paylite.png")
    with open(sample_png, "rb") as f:
        png_bytes = f.read()

    at.file_uploader[0].upload(filename="sample_family1_paylite.png", content=png_bytes).run()
    at.button[0].click().run()

    assert_phase8_elements(at)
    
    # Also verify existing analysis sections remain intact
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "- **Status:** Suspicious signals detected" in all_markdown
    assert "OCR Extracted Fields" in [sh.value for sh in at.subheader]
    assert "CNN Visual Classification" in [sh.value for sh in at.subheader]
    print("[PASS] State 3 (After full analysis): Disclaimer and Integrity Footer verified alongside all results.")

if __name__ == "__main__":
    test_state_1_no_file_uploaded()
    test_state_2_file_uploaded_not_analyzed()
    test_state_3_after_full_analysis()
    print("\nALL 3 PHASE 8 STATES VERIFIED SUCCESSFULLY!")
