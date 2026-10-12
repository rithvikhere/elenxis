"""
Ingestion & Cataloging Script for Real UPI Screenshots.
Complies with Project Rules & Security Protocol:
- Strips all EXIF/camera metadata
- Renames raw files anonymously (e.g., real_001.png ... real_018.png)
- Standardizes color modes to RGB
- Calculates SHA-256 hashes
- Builds the Section 12 extended metadata schema into data/real_metadata.csv
- Leaves images strictly local (ignored by Git)
"""

import os
import sys
import hashlib
from pathlib import Path
import pandas as pd
from PIL import Image

# Ensure paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.paths import REAL_RAW_DIR, REAL_METADATA_CSV, REAL_GROUND_TRUTH_CSV

EXTENDED_COLUMNS = [
    "image_id", "source_id", "group_id", "contributor_id", "device_id",
    "label", "edit_type", "amount_changed", "date_changed", "transaction_id_changed",
    "data_origin", "capture_path", "screen_type", "app_name", "app_version",
    "os_version", "device_model", "font_size_setting", "display_size_setting",
    "theme", "language", "width", "height", "file_format", "jpeg_quality",
    "color_mode", "redaction_applied", "redacted_fields", "sha256",
    "dataset_version", "consent_id"
]


def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def detect_app(filename: str, width: int, height: int) -> str:
    lower_fn = filename.lower()
    if "google pay" in lower_fn or "gpay" in lower_fn:
        return "GooglePay"
    if "phonepe" in lower_fn or "transactionreceipt" in lower_fn:
        return "PhonePe"
    # Fallback by aspect ratio / height characteristics observed
    if height > 2400:
        return "GooglePay"
    return "PhonePe"


def ingest_all():
    print(f"Scanning {REAL_RAW_DIR}...")
    files = sorted([f for f in os.listdir(REAL_RAW_DIR) if not f.startswith(".") and not f.endswith(".csv")])
    if not files:
        print("No image files found in real_raw directory.")
        return

    metadata_rows = []
    
    # Check if already renamed
    already_renamed = all(f.startswith("real_") for f in files)
    
    for idx, filename in enumerate(files, start=1):
        original_path = REAL_RAW_DIR / filename
        if not original_path.is_file():
            continue

        ext = original_path.suffix.lower()
        if ext == ".jpeg":
            ext = ".jpg"
            
        new_image_id = f"real_{idx:03d}"
        target_filename = f"{new_image_id}{ext}"
        target_path = REAL_RAW_DIR / target_filename

        # Load with PIL, strip metadata, convert mode if needed
        with Image.open(original_path) as img:
            width, height = img.size
            orig_mode = img.mode
            orig_format = img.format or ("PNG" if ext == ".png" else "JPEG")
            app_name = detect_app(filename, width, height)

            # Strip EXIF & metadata: create clean RGB image
            clean_img = Image.new("RGB", img.size)
            if img.mode in ("RGBA", "LA", "P"):
                # Blend with white background if alpha
                bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                bg.paste(img, (0, 0), img)
                clean_img = bg.convert("RGB")
            else:
                clean_img = img.convert("RGB")

        # Save to temporary path if renaming
        temp_path = REAL_RAW_DIR / f"temp_{new_image_id}{ext}"
        if ext == ".png":
            clean_img.save(temp_path, format="PNG", optimize=True)
        else:
            clean_img.save(temp_path, format="JPEG", quality=95)

        # Remove original and rename temp to target
        if original_path != target_path:
            original_path.unlink()
        if temp_path.exists():
            temp_path.replace(target_path)

        sha256 = calculate_sha256(target_path)

        # Assign device and group IDs
        # Group: images from same app/aspect ratio
        device_id = "dev_01" if width == 1080 and height >= 2376 else "dev_02"
        theme = "light"  # standard receipts are white card based

        row = {
            "image_id": new_image_id,
            "source_id": f"src_{new_image_id}",
            "group_id": f"grp_{device_id}_{app_name.lower()}",
            "contributor_id": "contrib_01",
            "device_id": device_id,
            "label": "original",
            "edit_type": "none",
            "amount_changed": False,
            "date_changed": False,
            "transaction_id_changed": False,
            "data_origin": "real",
            "capture_path": "direct",
            "screen_type": "success",
            "app_name": app_name,
            "app_version": "unspecified",
            "os_version": "Android",
            "device_model": "Android_1080p",
            "font_size_setting": "default",
            "display_size_setting": "default",
            "theme": theme,
            "language": "en",
            "width": width,
            "height": height,
            "file_format": "PNG" if ext == ".png" else "JPEG",
            "jpeg_quality": "95" if ext in (".jpg", ".jpeg") else "lossless",
            "color_mode": "RGB",
            "redaction_applied": False,
            "redacted_fields": "none",
            "sha256": sha256,
            "dataset_version": "v0.1",
            "consent_id": "consent_01"
        }
        metadata_rows.append(row)
        print(f"[{idx:02d}/18] Ingested: {filename[:30]} -> {target_filename} ({app_name}, {width}x{height})")

    df = pd.DataFrame(metadata_rows, columns=EXTENDED_COLUMNS)
    df.to_csv(REAL_METADATA_CSV, index=False)
    print(f"\nSuccessfully created {REAL_METADATA_CSV} with {len(df)} records.")


if __name__ == "__main__":
    ingest_all()
