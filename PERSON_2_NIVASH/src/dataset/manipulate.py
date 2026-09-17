"""
Controlled Manipulation Engine — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Generates realistic, controlled synthetic manipulations on original receipts:
- amount_change: Overwrite amount with a new value (font/size variance)
- date_change: Overwrite date with past or future date (testing temporal rules)
- transaction_id_change: Overwrite UTR with format-valid or malformed strings
- text_insert: Splice an extra line or badge into white space
- text_remove: Patch over an existing field with background color
- font_alter: Re-render a field with mismatched font family/weight
- crop: Asymmetric cropping of canvas margins
- resize: Benign downscale & upscale (content identical)
- recompress: Benign JPEG recompression at quality 50-70 (content identical)

Maintains accurate ground-truth values and emits comprehensive metadata.csv.
"""

import argparse
import csv
import io
import os
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.dataset import config
from src.dataset.templates import (
    format_inr_amount,
    get_font,
    generate_fictional_record,
    FICTIONAL_PAYEES,
)
from src.utils.paths import DATA_DIR, DOCS_DIR, PROCESSED_DIR, RAW_DIR, ensure_dir


# ---------------------------------------------------------------------------
# Coordinate Maps for Overwrite Patches by Template Family
# ---------------------------------------------------------------------------

# Coordinates for patching and re-rendering fields per layout family
FAMILY_PATCH_ZONES = {
    1: {  # PayLite (White background #FFFFFF, Primary Blue #1A73E8)
        "bg_color": "#FFFFFF",
        "text_color": "#202124",
        "amount_patch": (50, 210, 350, 265),
        "amount_color": "#1A73E8",
        "date_patch": (160, 365, 365, 400),
        "time_patch": (160, 405, 365, 440),
        "utr_patch": (160, 445, 365, 480),
        "recipient_patch": (160, 285, 365, 320),
    },
    2: {  # QuickPe (Dark Theme Card background #1E2738, Cyan #00D2C6)
        "bg_color": "#1E2738",
        "text_color": "#F1F5F9",
        "amount_patch": (35, 165, 360, 215),
        "amount_color": "#00D2C6",
        "date_patch": (35, 355, 360, 390),
        "time_patch": (35, 403, 360, 438),
        "utr_patch": (35, 307, 360, 342),
        "recipient_patch": (35, 115, 360, 145),
    },
    3: {  # UniPay (Hero bg #FAFAFA, Table bg #FFFFFF, Text #212121)
        "bg_color": "#FFFFFF",
        "text_color": "#212121",
        "amount_patch": (25, 100, 360, 155),
        "amount_color": "#212121",
        "date_patch": (35, 328, 360, 360),
        "time_patch": (35, 384, 360, 416),
        "utr_patch": (35, 440, 360, 472),
        "recipient_patch": (35, 216, 360, 248),
    },
}


# ---------------------------------------------------------------------------
# Individual Manipulation Functions
# ---------------------------------------------------------------------------

def apply_amount_change(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Overwrite the original hero amount with a new random amount.
    Simulates realistic copy-paste fraud by drawing a patch and re-rendering text.
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    zone = FAMILY_PATCH_ZONES[fam_id]

    # Generate a new disparate amount
    old_amt = float(record["amount_val"])
    new_amt = round(rng.uniform(10.0, 50000.0), 2)
    while abs(new_amt - old_amt) < 50.0:
        new_amt = round(rng.uniform(10.0, 50000.0), 2)
    new_amt_str = format_inr_amount(new_amt)

    # 1. Paste patch over old amount
    patch_box = zone["amount_patch"]
    draw.rectangle(patch_box, fill=zone["bg_color"])

    # 2. Render new amount text
    if fam_id == 1:
        font = get_font(34, bold=True)
        w, _ = config.IMAGE_SIZE
        bbox = draw.textbbox((0, 0), new_amt_str, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, 215), new_amt_str, fill=zone["amount_color"], font=font)
    elif fam_id == 2:
        font = get_font(32, bold=True)
        draw.text((38, 170), new_amt_str, fill=zone["amount_color"], font=font)
    else:
        font = get_font(34, bold=True)
        draw.text((30, 105), new_amt_str, fill=zone["amount_color"], font=font)

    new_record = record.copy()
    new_record["amount"] = new_amt_str
    new_record["amount_val"] = new_amt
    new_record["amount_changed"] = "yes"
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "amount_change"
    return out_img, new_record


def apply_date_change(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Overwrite the transaction date.
    50% probability of setting a future date (e.g. 2029) to test temporal consistency rules.
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    zone = FAMILY_PATCH_ZONES[fam_id]

    is_future = rng.choice([True, False])
    if is_future:
        # Deliberate future date for rule engine validation
        if fam_id == 1:
            new_date = "28 Dec 2029"
        elif fam_id == 2:
            new_date = "28-12-2029"
        else:
            new_date = "2029-12-28"
    else:
        # Different past date
        if fam_id == 1:
            new_date = "05 Jan 2025"
        elif fam_id == 2:
            new_date = "05-01-2025"
        else:
            new_date = "2025-01-05"

    patch_box = zone["date_patch"]
    draw.rectangle(patch_box, fill=zone["bg_color"])

    # Render new date
    if fam_id == 1:
        font = get_font(13, bold=True)
        draw.text((165, 375), new_date, fill=zone["text_color"], font=font)
    elif fam_id == 2:
        font = get_font(13, bold=True)
        draw.text((38, 361), new_date, fill=zone["text_color"], font=font)
    else:
        font = get_font(13, bold=False)
        draw.text((40, 333), new_date, fill=zone["text_color"], font=font)

    new_record = record.copy()
    new_record["date"] = new_date
    new_record["date_changed"] = "yes"
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "date_change"
    return out_img, new_record


def apply_transaction_id_change(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Overwrite the transaction ID (UTR).
    Includes format violations (alpha prefix, wrong digit length) and valid-format mutations.
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    zone = FAMILY_PATCH_ZONES[fam_id]

    edit_mode = rng.choice(["alpha_prefix", "short_digits", "valid_mutated"])
    if edit_mode == "alpha_prefix":
        new_utr = "UTR" + "".join(str(rng.randint(0, 9)) for _ in range(7))
    elif edit_mode == "short_digits":
        new_utr = "".join(str(rng.randint(0, 9)) for _ in range(8))
    else:
        new_utr = "".join(str(rng.randint(0, 9)) for _ in range(12))

    patch_box = zone["utr_patch"]
    draw.rectangle(patch_box, fill=zone["bg_color"])

    if fam_id == 1:
        font = get_font(13, bold=True)
        draw.text((165, 455), new_utr, fill=zone["text_color"], font=font)
    elif fam_id == 2:
        font = get_font(13, bold=True)
        draw.text((38, 313), new_utr, fill=zone["text_color"], font=font)
    else:
        font = get_font(13, bold=False)
        draw.text((40, 445), new_utr, fill=zone["text_color"], font=font)

    new_record = record.copy()
    new_record["transaction_id"] = new_utr
    new_record["transaction_id_changed"] = "yes"
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "transaction_id_change"
    return out_img, new_record


def apply_text_insert(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Splicing an artificial extra stamp or verification badge into white space.
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    w, h = config.IMAGE_SIZE

    # Spliced banner / stamp
    stamp_text = rng.choice(["[ AUTHENTICATED BY BANK ]", "[ PRIORITY MERCHANT SETTLEMENT ]", "[ 100% VERIFIED RECEIPT ]"])
    font = get_font(11, bold=True)
    
    y_pos = 580 if fam_id != 2 else 580
    draw.rectangle([(30, y_pos), (w - 30, y_pos + 26)], fill="#E8F0FE" if fam_id != 2 else "#1E3A5F", outline="#1A73E8")
    draw.text((45, y_pos + 6), stamp_text, fill="#1A73E8" if fam_id != 2 else "#60A5FA", font=font)

    new_record = record.copy()
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "text_insert"
    return out_img, new_record


def apply_text_remove(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Blanks out a required field with background color patch (testing missing field rules).
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    zone = FAMILY_PATCH_ZONES[fam_id]

    field_to_remove = rng.choice(["utr", "recipient"])
    new_record = record.copy()

    if field_to_remove == "utr":
        draw.rectangle(zone["utr_patch"], fill=zone["bg_color"])
        new_record["transaction_id"] = ""
        new_record["transaction_id_changed"] = "yes"
    else:
        draw.rectangle(zone["recipient_patch"], fill=zone["bg_color"])
        new_record["payee"] = ""

    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "text_remove"
    return out_img, new_record


def apply_font_alter(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Re-renders a field in a mismatched font size/weight or awkward baseline.
    """
    out_img = img.copy()
    draw = ImageDraw.Draw(out_img)
    fam_id = int(record["template_family"])
    zone = FAMILY_PATCH_ZONES[fam_id]

    # Patch recipient and re-render with mismatched heavy/small font
    draw.rectangle(zone["recipient_patch"], fill=zone["bg_color"])
    mismatched_font = get_font(18, bold=True)
    
    if fam_id == 1:
        draw.text((165, 292), record["payee"], fill="#000000", font=mismatched_font)
    elif fam_id == 2:
        draw.text((38, 115), record["payee"], fill="#E2E8F0", font=mismatched_font)
    else:
        draw.text((40, 214), record["payee"], fill="#000000", font=mismatched_font)

    new_record = record.copy()
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "font_alter"
    return out_img, new_record


def apply_crop(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Asymmetric margin cropping simulating merchant camera framing errors.
    """
    w, h = img.size
    crop_top = rng.randint(15, 35)
    crop_bottom = rng.randint(20, 45)
    crop_left = rng.randint(10, 25)
    crop_right = rng.randint(10, 25)

    cropped = img.crop((crop_left, crop_top, w - crop_right, h - crop_bottom))
    # Resize back to canvas size
    out_img = cropped.resize((w, h), Image.Resampling.BILINEAR)

    new_record = record.copy()
    new_record["label"] = "synthetic_fake"
    new_record["edit_type"] = "crop"
    return out_img, new_record


def apply_resize(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    BENIGN TRANSFORMATION: Downscale & upscale (content identical).
    Label remains 'original_transformed' (NOT a forgery).
    """
    w, h = img.size
    scale = rng.choice([0.65, 0.75, 0.85])
    small_w, small_h = int(w * scale), int(h * scale)
    
    downscaled = img.resize((small_w, small_h), Image.Resampling.BILINEAR)
    out_img = downscaled.resize((w, h), Image.Resampling.BILINEAR)

    new_record = record.copy()
    new_record["label"] = "original_transformed"
    new_record["edit_type"] = "resize"
    return out_img, new_record


def apply_recompress(img: Image.Image, record: Dict[str, Any], rng: random.Random) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    BENIGN TRANSFORMATION: JPEG recompression at quality 50-70.
    Label remains 'original_transformed' (NOT a forgery).
    Feeds Person 3's Error Level Analysis (ELA) benchmark.
    """
    quality = rng.randint(50, 70)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    out_img = Image.open(buf).convert("RGB")

    new_record = record.copy()
    new_record["label"] = "original_transformed"
    new_record["edit_type"] = "recompress"
    new_record["jpeg_quality"] = quality
    return out_img, new_record


# ---------------------------------------------------------------------------
# Manipulation Dispatcher Map
# ---------------------------------------------------------------------------

MANIPULATORS = {
    "amount_change": apply_amount_change,
    "date_change": apply_date_change,
    "transaction_id_change": apply_transaction_id_change,
    "text_insert": apply_text_insert,
    "text_remove": apply_text_remove,
    "font_alter": apply_font_alter,
    "crop": apply_crop,
    "resize": apply_resize,
    "recompress": apply_recompress,
}


# ---------------------------------------------------------------------------
# Master Batch Orchestrator
# ---------------------------------------------------------------------------

def generate_manipulated_dataset(
    raw_dir: Optional[Path] = None,
    processed_dir: Optional[Path] = None,
    ground_truth_in: Optional[Path] = None,
    metadata_out: Optional[Path] = None,
    ground_truth_out: Optional[Path] = None,
    variants_per_original: int = 4,
    seed: int = config.RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Reads original receipts from raw_dir, generates controlled variants in processed_dir,
    and produces data/metadata.csv and updated data/ground_truth.csv.
    """
    if raw_dir is None:
        raw_dir = RAW_DIR
    if processed_dir is None:
        processed_dir = PROCESSED_DIR
    if ground_truth_in is None:
        ground_truth_in = DATA_DIR / "ground_truth.csv"
    if metadata_out is None:
        metadata_out = DATA_DIR / "metadata.csv"
    if ground_truth_out is None:
        ground_truth_out = DATA_DIR / "ground_truth.csv"

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    ensure_dir(processed_dir)
    ensure_dir(metadata_out.parent)

    rng = random.Random(seed)

    # Load original records from ground_truth_in
    if not ground_truth_in.exists():
        raise FileNotFoundError(f"Original ground truth file not found at {ground_truth_in}. Run Phase 2 generator first.")

    with open(ground_truth_in, mode="r", newline="", encoding="utf-8") as f:
        original_records = list(csv.DictReader(f))

    all_metadata_rows: List[Dict[str, Any]] = []
    all_ground_truth_rows: List[Dict[str, Any]] = []

    manipulation_names = list(MANIPULATORS.keys())
    edit_counts: Dict[str, int] = {e: 0 for e in config.EDIT_TYPES}
    label_counts: Dict[str, int] = {"original": 0, "original_transformed": 0, "synthetic_fake": 0}

    # 1. Process Originals
    for orig in original_records:
        orig_img_path = raw_dir / orig["filename"]
        if not orig_img_path.exists():
            continue
        
        with Image.open(orig_img_path) as im:
            w, h = im.size
            fmt = im.format or "PNG"

        meta_row = {
            "image_id": orig["image_id"],
            "source_id": orig["image_id"],
            "template_family": orig["template_family"],
            "label": "original",
            "edit_type": "none",
            "amount_changed": "no",
            "date_changed": "no",
            "transaction_id_changed": "no",
            "width": w,
            "height": h,
            "file_format": fmt,
            "jpeg_quality": 95,
            "filename": orig["filename"],
            "relative_path": f"raw/{orig['filename']}",
        }
        all_metadata_rows.append(meta_row)
        all_ground_truth_rows.append(orig)
        edit_counts["none"] += 1
        label_counts["original"] += 1

        # 2. Generate Variants for this Original
        # Pick variants_per_original distinct manipulation types deterministically
        chosen_edits = rng.sample(manipulation_names, min(variants_per_original, len(manipulation_names)))

        for var_idx, edit_type in enumerate(chosen_edits, start=1):
            manip_func = MANIPULATORS[edit_type]
            with Image.open(orig_img_path) as im:
                var_img, var_rec = manip_func(im, orig, rng)

            # Generate new image ID: tpl{F}_src{NNN}_{edit}_{VV}
            fam_id = int(orig["template_family"])
            src_num = int(orig["image_id"].split("_")[1].replace("src", ""))
            var_image_id = config.ID_PATTERN.format(
                tpl_id=fam_id,
                src_id=src_num,
                edit_type=edit_type,
                var_id=var_idx,
            )
            var_filename = f"{var_image_id}.png"
            var_save_path = processed_dir / var_filename
            var_img.save(var_save_path, format="PNG")

            # Update variant ground truth record
            var_rec["image_id"] = var_image_id
            var_rec["filename"] = var_filename
            all_ground_truth_rows.append(var_rec)

            # Construct Metadata Row
            var_meta = {
                "image_id": var_image_id,
                "source_id": orig["image_id"],
                "template_family": fam_id,
                "label": var_rec.get("label", "synthetic_fake"),
                "edit_type": edit_type,
                "amount_changed": var_rec.get("amount_changed", "no"),
                "date_changed": var_rec.get("date_changed", "no"),
                "transaction_id_changed": var_rec.get("transaction_id_changed", "no"),
                "width": var_img.size[0],
                "height": var_img.size[1],
                "file_format": "PNG",
                "jpeg_quality": var_rec.get("jpeg_quality", 95),
                "filename": var_filename,
                "relative_path": f"processed/{var_filename}",
            }
            all_metadata_rows.append(var_meta)
            edit_counts[edit_type] += 1
            label_counts[var_meta["label"]] += 1

    # Write metadata.csv
    meta_fieldnames = [
        "image_id",
        "source_id",
        "template_family",
        "label",
        "edit_type",
        "amount_changed",
        "date_changed",
        "transaction_id_changed",
        "width",
        "height",
        "file_format",
        "jpeg_quality",
        "filename",
        "relative_path",
    ]
    with open(metadata_out, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=meta_fieldnames)
        writer.writeheader()
        for r in all_metadata_rows:
            writer.writerow(r)

    # Write updated ground_truth.csv
    gt_fieldnames = [
        "image_id",
        "template_family",
        "app_name",
        "amount",
        "amount_val",
        "date",
        "time",
        "transaction_id",
        "payer",
        "payee",
        "status",
        "filename",
    ]
    with open(ground_truth_out, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=gt_fieldnames)
        writer.writeheader()
        for r in all_ground_truth_rows:
            # Clean non-standard keys
            clean_r = {k: r.get(k, "") for k in gt_fieldnames}
            writer.writerow(clean_r)

    return {
        "total_images": len(all_metadata_rows),
        "total_originals": len(original_records),
        "total_variants": len(all_metadata_rows) - len(original_records),
        "label_breakdown": label_counts,
        "edit_breakdown": edit_counts,
        "metadata_csv": str(metadata_out),
        "ground_truth_csv": str(ground_truth_out),
        "seed": seed,
    }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate controlled synthetic receipt manipulations.")
    parser.add_argument("--variants-per-original", type=int, default=4, help="Number of variants to generate per original (default: 4)")
    parser.add_argument("--raw-dir", type=str, default=str(RAW_DIR), help="Directory containing original raw images")
    parser.add_argument("--out", type=str, default=str(PROCESSED_DIR), help="Output directory for processed variants")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED, help="Random seed for reproducibility")
    parser.add_argument("--samples", action="store_true", help="Also export 3 before/after sample pairs to docs/samples/")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("UPI Fraud Forensics — Person 2: Controlled Manipulation Engine")
    print("=" * 60)
    print(f"Generating {args.variants_per_original} variants per original (Seed: {args.seed})...")

    summary = generate_manipulated_dataset(
        raw_dir=Path(args.raw_dir),
        processed_dir=Path(args.out),
        variants_per_original=args.variants_per_original,
        seed=args.seed,
    )

    print("\nManipulation Generation Complete:")
    print(f"  • Total Images in Dataset : {summary['total_images']}")
    print(f"  • Originals (Untouched)  : {summary['total_originals']}")
    print(f"  • Variants Generated     : {summary['total_variants']}")
    print("\n  Label Distribution:")
    for lbl, cnt in summary["label_breakdown"].items():
        print(f"    - {lbl:20s}: {cnt}")
    print("\n  Edit Type Distribution:")
    for edt, cnt in summary["edit_breakdown"].items():
        print(f"    - {edt:22s}: {cnt}")
    print(f"\n  • Metadata CSV           : {summary['metadata_csv']}")
    print("=" * 60 + "\n")

    if args.samples:
        samples_dir = DOCS_DIR / "samples"
        ensure_dir(samples_dir)
        # Copy 3 before/after pairs
        # Pair 1: Amount change
        amt_img = list(Path(args.out).glob("*_amount_change_*.png"))[0]
        shutil.copy(amt_img, samples_dir / "sample_amount_change_after.png")
        
        # Pair 2: Date change
        date_img = list(Path(args.out).glob("*_date_change_*.png"))[0]
        shutil.copy(date_img, samples_dir / "sample_date_change_after.png")
        
        # Pair 3: Recompress (benign)
        recomp_img = list(Path(args.out).glob("*_recompress_*.png"))[0]
        shutil.copy(recomp_img, samples_dir / "sample_recompress_after.png")
        print(f"Exported before/after sample images to {samples_dir}")


if __name__ == "__main__":
    main()
