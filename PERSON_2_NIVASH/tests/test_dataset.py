"""
Tests for dataset integrity and metadata.
"""

import os
import csv
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(ROOT, "data", "metadata.csv")
DATA_RAW_DIR = os.path.join(ROOT, "data", "raw")

REQUIRED_COLUMNS = {
    "image_id", "filename", "label", "edit_type",
    "template_type", "split",
    "ground_truth_amount", "ground_truth_date",
    "ground_truth_time", "ground_truth_utr", "ground_truth_recipient"
}

VALID_LABELS = {"original", "synthetic_fake"}
VALID_SPLITS = {"train", "val", "test"}
VALID_TEMPLATES = {"apex", "zenith", "nova"}
VALID_EDIT_TYPES = {"none", "amount_change", "date_change", "transaction_id_change", "text_tamper"}


@pytest.fixture(scope="module")
def metadata_rows():
    assert os.path.exists(METADATA_PATH), f"metadata.csv not found at {METADATA_PATH}"
    with open(METADATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def test_metadata_exists():
    assert os.path.exists(METADATA_PATH), "metadata.csv does not exist"


def test_metadata_columns(metadata_rows):
    actual_cols = set(metadata_rows[0].keys())
    missing = REQUIRED_COLUMNS - actual_cols
    assert not missing, f"Missing columns: {missing}"


def test_metadata_row_count(metadata_rows):
    assert len(metadata_rows) == 60, f"Expected 60 rows, got {len(metadata_rows)}"


def test_all_images_exist(metadata_rows):
    missing = []
    for row in metadata_rows:
        img_path = os.path.join(DATA_RAW_DIR, row["filename"])
        if not os.path.exists(img_path):
            missing.append(row["filename"])
    assert not missing, f"Missing image files: {missing[:5]}"


def test_valid_labels(metadata_rows):
    for row in metadata_rows:
        assert row["label"] in VALID_LABELS, f"Invalid label: {row['label']}"


def test_valid_splits(metadata_rows):
    for row in metadata_rows:
        assert row["split"] in VALID_SPLITS, f"Invalid split: {row['split']}"


def test_valid_templates(metadata_rows):
    for row in metadata_rows:
        assert row["template_type"] in VALID_TEMPLATES, f"Invalid template: {row['template_type']}"


def test_valid_edit_types(metadata_rows):
    for row in metadata_rows:
        assert row["edit_type"] in VALID_EDIT_TYPES, f"Invalid edit_type: {row['edit_type']}"


def test_split_distribution(metadata_rows):
    counts = {"train": 0, "val": 0, "test": 0}
    for row in metadata_rows:
        counts[row["split"]] += 1
    assert counts["train"] > counts["val"], "Train set should be larger than val"
    assert counts["val"] == counts["test"], "Val and test sets should be equal size"


def test_original_label_has_none_edit_type(metadata_rows):
    for row in metadata_rows:
        if row["label"] == "original":
            assert row["edit_type"] == "none", (
                f"Original image {row['image_id']} must have edit_type='none'"
            )


def test_utr_ground_truth_not_empty(metadata_rows):
    for row in metadata_rows:
        assert row["ground_truth_utr"].strip(), (
            f"Image {row['image_id']} has empty ground_truth_utr"
        )
