import os
import sys
import shutil
import pathlib
import traceback
import streamlit as st
from PIL import Image

# Ensure Tesseract OCR binary path is configured on Windows
try:
    import pytesseract
    if not shutil.which("tesseract"):
        tesseract_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_default):
            pytesseract.pytesseract.tesseract_cmd = tesseract_default
except Exception as t_err:
    print(f"[Warning] Tesseract init: {t_err}", file=sys.stderr)

# Ensure PERSON_2_NIVASH is on sys.path for importing OCR & Rule modules
REPO_ROOT = pathlib.Path(__file__).resolve().parent
PERSON_2_DIR = str(REPO_ROOT / "PERSON_2_NIVASH")
if PERSON_2_DIR not in sys.path:
    sys.path.insert(0, PERSON_2_DIR)

# 1. Page Configuration
st.set_page_config(
    page_title="UPI Fraud Forensics",
    layout="wide"
)

# 2. Header & Subtitle
st.title("UPI Fraud Forensics")
st.caption("Screenshot-based forensic analysis for detecting potential manipulation indicators.")

# Directory for saving uploaded images temporarily for downstream forensic modules
TEMP_DIR = pathlib.Path("PERSON_1_RITHVIK/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# 3. File Uploader
uploaded_file = st.file_uploader(
    "Upload UPI Screenshot",
    type=["png", "jpg", "jpeg"],
    help="Select a transaction screenshot in PNG, JPG, or JPEG format."
)

temp_image_path = None
valid_image = None

if uploaded_file is not None:
    # 4. Image Validation
    try:
        # Verify file structure and integrity
        raw_image = Image.open(uploaded_file)
        raw_image.verify()

        # Re-open and fully decode pixel data to catch truncated or corrupted image content
        uploaded_file.seek(0)
        decoded_image = Image.open(uploaded_file)
        decoded_image.load()

        valid_image = decoded_image

        # 6. Save uploaded file to local temp path for Person 2 & Person 3 modules
        file_suffix = pathlib.Path(uploaded_file.name).suffix
        temp_file_path = TEMP_DIR / f"uploaded_screenshot{file_suffix}"
        uploaded_file.seek(0)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        temp_image_path = str(temp_file_path)

        # 5. Image Preview
        st.subheader("Screenshot Preview")
        st.image(valid_image, caption=f"Uploaded: {uploaded_file.name}", width=450)

    except Exception:
        st.error("The uploaded file is not a valid or readable image. Please upload an uncorrupted PNG or JPG screenshot.")
else:
    # Reset analysis state when file is cleared
    st.session_state.pop("ocr_output", None)
    st.session_state.pop("rule_verdict", None)
    st.session_state.pop("analyzed_file", None)

# Helper function to format values as "Not detected" if missing or empty
def format_field_value(val):
    if val is None or str(val).strip() == "":
        return "Not detected"
    return str(val)

# 7. Action Button & Integration (Phase 4: Wire In Person 2)
if valid_image is not None and temp_image_path is not None:
    if st.button("Analyze Screenshot", type="primary"):
        # Run OCR extraction
        ocr_res = None
        try:
            from src.ocr import extract_transaction_fields
            ocr_res = extract_transaction_fields(temp_image_path)
        except Exception as exc:
            print(f"[Error] OCR extraction failed: {exc}", file=sys.stderr)
            traceback.print_exc()

        # Run Rule Validation
        rule_res = None
        if ocr_res is not None:
            try:
                from src.rules import validate_transaction
                rule_res = validate_transaction(ocr_res)
            except Exception as exc:
                print(f"[Error] Rule validation failed: {exc}", file=sys.stderr)
                traceback.print_exc()

        st.session_state["ocr_output"] = ocr_res
        st.session_state["rule_verdict"] = rule_res
        st.session_state["analyzed_file"] = uploaded_file.name

    # Display analysis sections if current file has been analyzed
    if st.session_state.get("analyzed_file") == uploaded_file.name:
        st.divider()

        # Section 1: OCR Extracted Fields
        st.subheader("OCR Extracted Fields")
        ocr_data = st.session_state.get("ocr_output")
        if ocr_data is not None and isinstance(ocr_data, dict):
            fields = ocr_data.get("fields", {})
            st.markdown(f"- **Amount:** {format_field_value(fields.get('amount'))}")
            st.markdown(f"- **Date:** {format_field_value(fields.get('date'))}")
            st.markdown(f"- **Time:** {format_field_value(fields.get('time'))}")
            st.markdown(f"- **UTR:** {format_field_value(fields.get('transaction_id'))}")
            st.markdown(f"- **Template:** {format_field_value(fields.get('template_type'))}")
            st.markdown(f"- **Recipient:** {format_field_value(fields.get('recipient'))}")
        else:
            st.info("Not available yet")

        # Section 2: Rule Validation
        st.subheader("Rule Validation")
        rule_data = st.session_state.get("rule_verdict")
        if rule_data is not None and isinstance(rule_data, dict):
            verdict = rule_data.get("verdict", "Not detected")
            score = rule_data.get("suspicion_score")
            score_formatted = f"{score:.2f}" if isinstance(score, (int, float)) else "Not detected"

            st.markdown(f"- **Verdict:** {verdict}")
            st.markdown(f"- **Anomaly Score:** {score_formatted}")
            st.markdown("**Rule Explanations:**")

            # Option 2: Full checklist of checks performed (violations, warnings, passed checks)
            violations = rule_data.get("violations", [])
            warnings = rule_data.get("warnings", [])
            passed_checks = rule_data.get("passed_checks", [])

            all_explanations = []
            if isinstance(violations, list):
                all_explanations.extend(violations)
            if isinstance(warnings, list):
                all_explanations.extend(warnings)
            if isinstance(passed_checks, list):
                all_explanations.extend(passed_checks)

            if all_explanations:
                for item in all_explanations:
                    st.markdown(f"- {item}")
            else:
                st.markdown("- No rule checks available")
        else:
            st.info("Not available yet")

else:
    if uploaded_file is None:
        st.info("Please upload a UPI payment screenshot above to preview and analyze.")
