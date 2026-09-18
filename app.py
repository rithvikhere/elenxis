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

# Ensure repository root and subsystem folders are on sys.path for importing modules
REPO_ROOT = pathlib.Path(__file__).resolve().parent
PERSON_2_DIR = str(REPO_ROOT / "PERSON_2_NIVASH")
if PERSON_2_DIR not in sys.path:
    sys.path.insert(0, PERSON_2_DIR)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# 1. Page Configuration
st.set_page_config(
    page_title="UPI Fraud Forensics",
    layout="wide"
)

# 2. Header & Subtitle
st.title("UPI Fraud Forensics")
st.caption("Screenshot-based forensic analysis for detecting potential manipulation indicators.")

# Standing Disclaimer (Always visible on every page state)
st.warning(
    "This tool analyzes screenshot authenticity signals. It does not verify whether a bank transaction occurred. Confirm payment through the official payment app or bank account."
)

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
    st.session_state.pop("cnn_output", None)
    st.session_state.pop("forensics_output", None)
    st.session_state.pop("gradcam_output", None)
    st.session_state.pop("analyzed_file", None)

# Helper function to format values as "Not detected" if missing or empty
def format_field_value(val):
    if val is None or str(val).strip() == "":
        return "Not detected"
    return str(val)

# 7. Action Button & Integration (Phase 4 & Phase 5)
if valid_image is not None and temp_image_path is not None:
    if st.button("Analyze Screenshot", type="primary"):
        # --- Person 2: Run OCR Extraction ---
        ocr_res = None
        try:
            from src.ocr import extract_transaction_fields
            ocr_res = extract_transaction_fields(temp_image_path)
        except Exception as exc:
            print(f"[Error] OCR extraction failed: {exc}", file=sys.stderr)
            traceback.print_exc()

        # --- Person 2: Run Rule Validation ---
        rule_res = None
        if ocr_res is not None:
            try:
                from src.rules import validate_transaction
                rule_res = validate_transaction(ocr_res)
            except Exception as exc:
                print(f"[Error] Rule validation failed: {exc}", file=sys.stderr)
                traceback.print_exc()

        # --- Person 3: Run CNN Visual Prediction ---
        cnn_res = None
        try:
            from PERSON_3_SANJAY.src.api import predict as cnn_predict
            cnn_res = cnn_predict(temp_image_path)
        except Exception as exc:
            print(f"[Error] CNN prediction failed: {exc}", file=sys.stderr)
            traceback.print_exc()

        # --- Person 3: Run Image Forensics (ELA + Metadata) ---
        forensics_res = None
        try:
            from PERSON_3_SANJAY.src.api import analyze_image as forensic_analyze_image
            forensics_res = forensic_analyze_image(temp_image_path, ela_output_dir=str(TEMP_DIR))
        except Exception as exc:
            print(f"[Error] Forensic analysis failed: {exc}", file=sys.stderr)
            traceback.print_exc()

        # --- Person 3: Run Grad-CAM Explainability ---
        gradcam_res = None
        try:
            from PERSON_3_SANJAY.src.explainability.gradcam import generate_gradcam
            weights_path = REPO_ROOT / "PERSON_3_SANJAY" / "models" / "resnet18_baseline_best.pt"
            if weights_path.exists():
                gradcam_res = generate_gradcam(
                    temp_image_path,
                    model_path=str(weights_path),
                    output_dir=str(TEMP_DIR)
                )
            else:
                print("[Warning] CNN weights not found for Grad-CAM.", file=sys.stderr)
        except Exception as exc:
            print(f"[Error] Grad-CAM generation failed: {exc}", file=sys.stderr)
            traceback.print_exc()

        # Save results to session state
        st.session_state["ocr_output"] = ocr_res
        st.session_state["rule_verdict"] = rule_res
        st.session_state["cnn_output"] = cnn_res
        st.session_state["forensics_output"] = forensics_res
        st.session_state["gradcam_output"] = gradcam_res
        st.session_state["analyzed_file"] = uploaded_file.name

    # Display analysis sections if current file has been analyzed
    if st.session_state.get("analyzed_file") == uploaded_file.name:
        st.divider()

        # =========================================================================
        # PHASE 4: PERSON 2 MODULES (OCR + RULES)
        # =========================================================================

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

        # =========================================================================
        # PHASE 5: PERSON 3 MODULES (CNN + FORENSICS + GRAD-CAM)
        # =========================================================================
        st.divider()

        # Section 3: CNN Visual Classification
        st.subheader("CNN Visual Classification")
        cnn_data = st.session_state.get("cnn_output")
        if cnn_data is not None and isinstance(cnn_data, dict) and cnn_data.get("status") == "success":
            pred_class = format_field_value(cnn_data.get("class"))
            prob = cnn_data.get("probability")
            prob_str = f"{prob:.4f}" if isinstance(prob, (int, float)) else "Not detected"

            st.markdown(f"- **Predicted Class:** {pred_class}")
            st.markdown(f"- **Probability:** {prob_str}")
            st.caption("Prediction from a small baseline model — accuracy 0.75, recall 1.00 on a 12-image held-out test set.")
        else:
            st.info("Not available yet")

        # Section 4: Image Forensics (ELA & Metadata)
        st.subheader("Image Forensics")
        forensics_data = st.session_state.get("forensics_output")
        if forensics_data is not None and isinstance(forensics_data, dict) and forensics_data.get("status") == "available":
            # Separate Block A: ELA Visualization
            st.markdown("#### Error Level Analysis (ELA)")
            ela_dict = forensics_data.get("ela", {})
            ela_path = ela_dict.get("output_visualization_path")
            if ela_path and os.path.exists(ela_path):
                st.image(ela_path, caption=None, width=400)
            st.caption("ELA and metadata are evidence for inspection, not proof of manipulation.")

            # Separate Block B: Metadata / EXIF Findings
            st.markdown("#### Metadata & EXIF Analysis")
            meta_dict = forensics_data.get("metadata", {})
            if meta_dict and meta_dict.get("status") == "available":
                st.markdown(f"- **File Format:** {format_field_value(meta_dict.get('file_format'))}")
                dims = meta_dict.get("dimensions")
                if isinstance(dims, dict):
                    st.markdown(f"- **Dimensions:** {dims.get('width', 'Not detected')} × {dims.get('height', 'Not detected')} px")
                file_size = meta_dict.get("file_size_bytes")
                st.markdown(f"- **File Size:** {file_size} bytes" if file_size else "- **File Size:** Not detected")
                st.markdown(f"- **Software:** {format_field_value(meta_dict.get('software'))}")

                has_exif = meta_dict.get("has_exif", False)
                exif_tags = meta_dict.get("exif_fields", {})
                if has_exif and exif_tags:
                    st.markdown(f"- **EXIF Header:** Present ({len(exif_tags)} tag(s) detected)")
                else:
                    st.markdown("- **EXIF Header:** No EXIF metadata is present.")
                    st.caption("Missing EXIF is normal for screenshots and shared images and is not itself suspicious.")
            else:
                st.info("Not available yet")
        else:
            st.info("Not available yet")

        # Section 5: Model Explainability (Grad-CAM)
        st.subheader("Model Explainability (Grad-CAM)")
        gradcam_data = st.session_state.get("gradcam_output")
        if gradcam_data is not None and isinstance(gradcam_data, dict) and gradcam_data.get("status") == "available":
            output_paths = gradcam_data.get("output_paths", {})
            overlay_path = output_paths.get("overlay")
            heatmap_path = output_paths.get("heatmap")
            if overlay_path and os.path.exists(overlay_path):
                st.image(overlay_path, width=400)
                st.caption("Highlights regions that influenced the model's prediction — not proof that a region was edited.")
            elif heatmap_path and os.path.exists(heatmap_path):
                st.image(heatmap_path, width=400)
                st.caption("Highlights regions that influenced the model's prediction — not proof that a region was edited.")
            else:
                st.info("Not available yet")
        else:
            st.info("Not available yet")

        # =========================================================================
        # PHASE 6: COMBINED ASSESSMENT (PROVISIONAL)
        # =========================================================================
        st.divider()
        st.subheader("Combined Assessment")

        # Hardcoded threshold for meaningfully high CNN confidence: probability >= 0.70
        CNN_CONFIDENCE_THRESHOLD = 0.70

        # Assess module availability from Phase 4 and Phase 5 outputs
        rule_available = (
            rule_data is not None
            and isinstance(rule_data, dict)
            and rule_data.get("verdict") in ("SUSPICIOUS", "LIKELY_LEGITIMATE")
        )
        cnn_available = (
            cnn_data is not None
            and isinstance(cnn_data, dict)
            and cnn_data.get("status") == "success"
            and cnn_data.get("class") in ("modified", "original")
        )

        # Derive dynamic contribution descriptor
        if rule_available and cnn_available:
            contributed_str = "Based on: rule engine, CNN"
        elif rule_available and not cnn_available:
            contributed_str = "Based on: rule engine only — CNN unavailable"
        elif not rule_available and cnn_available:
            contributed_str = "Based on: CNN only — rule engine unavailable"
        else:
            contributed_str = "Based on: none available."

        # Compute combined status using strictly specified three-state logic
        if not (rule_available and cnn_available):
            combined_status = "Insufficient evidence / unable to analyze reliably"
        else:
            rule_verdict_val = rule_data.get("verdict")
            cnn_class_val = cnn_data.get("class")
            cnn_prob_val = cnn_data.get("probability", 0.0)

            is_rule_suspicious = (rule_verdict_val == "SUSPICIOUS")
            is_cnn_suspicious = (
                cnn_class_val == "modified"
                and cnn_prob_val is not None
                and cnn_prob_val >= CNN_CONFIDENCE_THRESHOLD
            )

            if is_rule_suspicious or is_cnn_suspicious:
                combined_status = "Suspicious signals detected"
            elif rule_verdict_val == "LIKELY_LEGITIMATE" and cnn_class_val == "original":
                combined_status = "No suspicious signals detected"
            else:
                combined_status = "Insufficient evidence / unable to analyze reliably"

        st.markdown(f"- **Status:** {combined_status}")
        st.markdown(f"- *{contributed_str}*")
        st.caption("Provisional combined signal — not a calibrated ensemble. Full ensemble scoring is planned for a later milestone.")

else:
    if uploaded_file is None:
        st.info("Please upload a UPI payment screenshot above to preview and analyze.")

# =============================================================================
# 8. Footer & Academic Integrity Display (Phase 8)
# =============================================================================
st.divider()
st.subheader("About & Academic Integrity")
st.markdown(
    "All demo and sample data in this platform is synthetic and used for academic purposes only. "
    "Dataset images from Person 2 carry a visible **`DEMO / SYNTHETIC UPI RECEIPT`** watermark."
)
st.markdown("**Subsystem Benchmark Metrics:**")
st.markdown("- **OCR:** 100% extraction/field accuracy on test split")
st.markdown("- **Rule engine:** 93.9% precision / 68.9% recall overall")
st.markdown("- **CNN:** 0.75 accuracy / 1.00 recall on a 12-image held-out set")
