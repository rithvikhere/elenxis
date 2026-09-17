"""
Tests for dataset integrity and metadata (300 images, 3-label taxonomy).
"""

import os
import csv
import pytest
from src.dataset import config
from src.utils.paths import METADATA_CSV, RAW_DIR, PROCESSED_DIR, PROJECT_ROOT, DATA_DIR

VALID_LABELS = {"original", "original_transformed", "synthetic_fake"}
VALID_SPLITS = {"train", "val", "test"}
VALID_TEMPLATES = {1, 2, 3}
VALID_EDIT_TYPES = {
    "none", "amount_change", "date_change", "transaction_id_change",
    "text_insert", "text_remove", "font_alter", "crop", "resize", "recompress"
}


@pytest.fixture(scope="module")
def metadata_rows():
    assert METADATA_CSV.exists(), f"metadata.csv not found at {METADATA_CSV}"
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def test_metadata_exists():
    assert METADATA_CSV.exists(), "metadata.csv does not exist"


def test_metadata_row_count(metadata_rows):
    assert len(metadata_rows) == 300, f"Expected 300 rows, got {len(metadata_rows)}"


def test_all_images_exist(metadata_rows):
    missing = []
    for row in metadata_rows:
        img_path = DATA_DIR / row["relative_path"]
        if not img_path.exists():
            missing.append(row["relative_path"])
    assert not missing, f"Missing image files: {missing[:5]}"


def test_valid_labels(metadata_rows):
    for row in metadata_rows:
        assert row["label"] in VALID_LABELS, f"Invalid label: {row['label']}"


def test_valid_templates(metadata_rows):
    for row in metadata_rows:
        assert int(row["template_family"]) in VALID_TEMPLATES, f"Invalid template: {row['template_family']}"


def test_valid_edit_types(metadata_rows):
    for row in metadata_rows:
        assert row["edit_type"] in VALID_EDIT_TYPES, f"Invalid edit_type: {row['edit_type']}"


def test_original_label_has_none_edit_type(metadata_rows):
    for row in metadata_rows:
        if row["label"] == "original":
            assert row["edit_type"] == "none", (
                f"Original image {row['image_id']} must have edit_type='none'"
            )
