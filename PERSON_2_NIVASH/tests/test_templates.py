"""
Unit tests for Template Synthesis Engine (Phase 2).
Verifies determinism, layout family rendering, field value validity, and ground truth accuracy.
"""

import csv
import random
from pathlib import Path
from PIL import Image

from src.dataset import config
from src.dataset.templates import (
    generate_fictional_record,
    generate_originals,
    format_inr_amount,
    RENDERERS,
)


def test_inr_amount_formatting():
    assert format_inr_amount(450.0) == "₹450.00"
    assert format_inr_amount(1250.5) == "₹1,250.50"
    assert format_inr_amount(23478.99) == "₹23,478.99"
    assert format_inr_amount(100000.0) == "₹1,00,000.00"


def test_fictional_record_fields():
    rng = random.Random(42)
    for fam_id in [1, 2, 3]:
        rec = generate_fictional_record(src_id=1, template_family=fam_id, rng=rng)
        assert rec["template_family"] == fam_id
        assert rec["app_name"] in ["PayLite", "QuickPe", "UniPay"]
        assert rec["amount"].startswith("₹")
        assert len(rec["transaction_id"]) == 12
        assert rec["transaction_id"].isdigit()
        assert rec["payee"]
        assert rec["payer"]
        assert rec["status"]
        assert rec["filename"].endswith(".png")


def test_all_layout_renderers_output_valid_image():
    rng = random.Random(42)
    for fam_id, renderer in RENDERERS.items():
        rec = generate_fictional_record(src_id=fam_id, template_family=fam_id, rng=rng)
        img = renderer(rec)
        assert isinstance(img, Image.Image)
        assert img.size == config.IMAGE_SIZE
        assert img.mode == "RGB"


def test_deterministic_generation(tmp_path):
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    gt1 = tmp_path / "gt1.csv"
    gt2 = tmp_path / "gt2.csv"

    res1 = generate_originals(count=9, output_dir=out1, ground_truth_path=gt1, seed=42)
    res2 = generate_originals(count=9, output_dir=out2, ground_truth_path=gt2, seed=42)

    assert res1["total_generated"] == 9
    assert res2["total_generated"] == 9

    # Compare ground truth CSV contents
    with open(gt1, "r", encoding="utf-8") as f1, open(gt2, "r", encoding="utf-8") as f2:
        assert f1.read() == f2.read()

    # Compare image bytes
    for p1 in out1.glob("*.png"):
        p2 = out2 / p1.name
        assert p2.exists()
        assert p1.read_bytes() == p2.read_bytes()


def test_ground_truth_csv_integrity(tmp_path):
    out_dir = tmp_path / "raw"
    gt_file = tmp_path / "ground_truth.csv"
    res = generate_originals(count=12, output_dir=out_dir, ground_truth_path=gt_file, seed=42)

    assert gt_file.exists()
    with open(gt_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 12
    for r in rows:
        assert r["image_id"]
        assert int(r["template_family"]) in [1, 2, 3]
        assert r["amount"].startswith("₹")
        assert len(r["transaction_id"]) == 12
        assert (out_dir / r["filename"]).exists()
