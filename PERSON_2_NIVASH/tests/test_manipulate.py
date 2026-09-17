"""
Unit tests for Controlled Manipulation Engine (Phase 3).
Verifies all 9 manipulation types, label semantics (including original_transformed),
metadata.csv schema integrity, and dataset audit validation.
"""

import csv
import random
from pathlib import Path
from PIL import Image

from src.dataset import config
from src.dataset.templates import generate_fictional_record, RENDERERS
from src.dataset.manipulate import (
    apply_amount_change,
    apply_date_change,
    apply_transaction_id_change,
    apply_text_insert,
    apply_text_remove,
    apply_font_alter,
    apply_crop,
    apply_resize,
    apply_recompress,
    generate_manipulated_dataset,
    MANIPULATORS,
)
from src.dataset.audit import audit_dataset


def test_individual_manipulators():
    rng = random.Random(42)
    rec = generate_fictional_record(src_id=1, template_family=1, rng=rng)
    base_img = RENDERERS[1](rec)

    # 1. Amount change
    img_amt, rec_amt = apply_amount_change(base_img, rec, rng)
    assert rec_amt["label"] == "synthetic_fake"
    assert rec_amt["edit_type"] == "amount_change"
    assert rec_amt["amount_changed"] == "yes"
    assert img_amt.size == config.IMAGE_SIZE

    # 2. Date change
    img_date, rec_date = apply_date_change(base_img, rec, rng)
    assert rec_date["label"] == "synthetic_fake"
    assert rec_date["edit_type"] == "date_change"
    assert rec_date["date_changed"] == "yes"

    # 3. UTR change
    img_utr, rec_utr = apply_transaction_id_change(base_img, rec, rng)
    assert rec_utr["label"] == "synthetic_fake"
    assert rec_utr["edit_type"] == "transaction_id_change"
    assert rec_utr["transaction_id_changed"] == "yes"

    # 4. Text insert
    img_ins, rec_ins = apply_text_insert(base_img, rec, rng)
    assert rec_ins["label"] == "synthetic_fake"
    assert rec_ins["edit_type"] == "text_insert"

    # 5. Text remove
    img_rem, rec_rem = apply_text_remove(base_img, rec, rng)
    assert rec_rem["label"] == "synthetic_fake"
    assert rec_rem["edit_type"] == "text_remove"

    # 6. Font alter
    img_font, rec_font = apply_font_alter(base_img, rec, rng)
    assert rec_font["label"] == "synthetic_fake"
    assert rec_font["edit_type"] == "font_alter"

    # 7. Crop
    img_crop, rec_crop = apply_crop(base_img, rec, rng)
    assert rec_crop["label"] == "synthetic_fake"
    assert rec_crop["edit_type"] == "crop"
    assert img_crop.size == config.IMAGE_SIZE

    # 8. Resize (Benign -> original_transformed)
    img_res, rec_res = apply_resize(base_img, rec, rng)
    assert rec_res["label"] == "original_transformed"
    assert rec_res["edit_type"] == "resize"
    assert img_res.size == config.IMAGE_SIZE

    # 9. Recompress (Benign -> original_transformed)
    img_rec, rec_rec = apply_recompress(base_img, rec, rng)
    assert rec_rec["label"] == "original_transformed"
    assert rec_rec["edit_type"] == "recompress"
    assert img_rec.size == config.IMAGE_SIZE


def test_metadata_csv_schema(tmp_path):
    raw_dir = tmp_path / "raw"
    proc_dir = tmp_path / "processed"
    meta_csv = tmp_path / "metadata.csv"
    gt_in = tmp_path / "gt_in.csv"
    gt_out = tmp_path / "gt_out.csv"

    # Generate 3 originals
    from src.dataset.templates import generate_originals
    generate_originals(count=3, output_dir=raw_dir, ground_truth_path=gt_in, seed=42)

    # Generate 2 variants per original
    res = generate_manipulated_dataset(
        raw_dir=raw_dir,
        processed_dir=proc_dir,
        ground_truth_in=gt_in,
        metadata_out=meta_csv,
        ground_truth_out=gt_out,
        variants_per_original=2,
        seed=42,
    )

    assert res["total_images"] == 3 + 6  # 3 originals + 6 variants = 9 total
    assert meta_csv.exists()

    with open(meta_csv, mode="r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 9
    for r in rows:
        assert r["image_id"]
        assert r["source_id"]
        assert r["label"] in ["original", "original_transformed", "synthetic_fake"]
        assert r["edit_type"] in config.EDIT_TYPES
        assert (tmp_path / r["relative_path"]).exists()


def test_audit_dataset_passes():
    res = audit_dataset()
    assert res["all_checks_passed"] is True
    assert res["summary"]["total_images"] == 300
    assert res["check_details"]["2_file_existence"]["missing_count"] == 0
    assert res["check_details"]["3_orphan_files"]["orphan_count"] == 0
