import pathlib
import streamlit as st
from PIL import Image

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

# 7. Action Button / 8. Neutral Empty State
if valid_image is not None:
    if st.button("Analyze Screenshot", type="primary"):
        st.info("Analysis modules will be wired in during Phase 4/5.")
else:
    if uploaded_file is None:
        st.info("Please upload a UPI payment screenshot above to preview and analyze.")
