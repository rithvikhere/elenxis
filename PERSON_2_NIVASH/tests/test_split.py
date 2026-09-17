"""
Unit tests for Leakage-Safe Dataset Splitting & Integrity Audit (Phase 4).
Verifies:
- Group disjointness across splits (no source_id overlap).
- Deterministic reproducibility of split generation.
- Stratification of template families across splits.
- Split manifest file existence and schema integrity.
- Full 11-point dataset integrity audit execution.
"""

import csv
import tempfile
from pathlib import Path
import pytest

from src.dataset import config
from src.dataset.split import split_dataset
from src.dataset.audit import audit_dataset_integrity
from src.utils.paths import METADATA_CSV, SPLITS_DIR, DATA_DIR


@pytest.fixture(scope="module")
def split_results():
    """Run split generation and return results."""
    return split_dataset()


def test_split_manifests_exist(split_results):
    """Test that all three split CSV files exist on disk."""
    for s in ["train", "val", "test"]:
        manifest_path = SPLITS_DIR / f"{s}.csv"
        assert manifest_path.exists(), f"Missing split manifest: {manifest_path}"


def test_split_manifest_schemas():
    """Test that split manifest files contain the mandatory columns."""
    expected_cols = {
        "image_id", "source_id", "template_family", "label",
        "edit_type", "filename", "relative_path", "split"
    }
    for s in ["train", "val", "test"]:
        manifest_path = SPLITS_DIR / f"{s}.csv"
        with open(manifest_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cols = set(reader.fieldnames or [])
            assert expected_cols.issubset(cols), f"Missing columns in {s}.csv: {expected_cols - cols}"


def test_group_disjointness_no_leakage():
    """
    CRITICAL CHECK:
    Verify that no source_id appears in more than one split manifest.
    Guarantees zero data leakage for downstream CNN models.
    """
    split_sources = {}
    for s in ["train", "val", "test"]:
        manifest_path = SPLITS_DIR / f"{s}.csv"
        with open(manifest_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            split_sources[s] = {row["source_id"] for row in reader}

    train_sources = split_sources["train"]
    val_sources = split_sources["val"]
    test_sources = split_sources["test"]

    train_val_overlap = train_sources.intersection(val_sources)
    train_test_overlap = train_sources.intersection(test_sources)
    val_test_overlap = val_sources.intersection(test_sources)

    assert len(train_val_overlap) == 0, f"Data leakage detected! train/val overlap: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"Data leakage detected! train/test overlap: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"Data leakage detected! val/test overlap: {val_test_overlap}"


def test_template_family_stratification():
    """Verify all 3 template families are present in each split."""
    for s in ["train", "val", "test"]:
        manifest_path = SPLITS_DIR / f"{s}.csv"
        with open(manifest_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            families = {int(row["template_family"]) for row in reader}
            assert families == {1, 2, 3}, f"Split {s} is missing template families: { {1, 2, 3} - families }"


def test_label_class_coverage():
    """Verify all 3 label classes are present in each split."""
    expected_labels = {"original", "original_transformed", "synthetic_fake"}
    for s in ["train", "val", "test"]:
        manifest_path = SPLITS_DIR / f"{s}.csv"
        with open(manifest_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            labels = {row["label"] for row in reader}
            assert expected_labels.issubset(labels), f"Split {s} is missing label classes: {expected_labels - labels}"


def test_split_determinism_and_reproducibility():
    """Verify running the split with the exact same seed generates byte-identical manifests."""
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        p1 = Path(d1)
        p2 = Path(d2)
        split_dataset(splits_dir=p1, seed=42)
        split_dataset(splits_dir=p2, seed=42)

        for s in ["train", "val", "test"]:
            content_1 = (p1 / f"{s}.csv").read_text(encoding="utf-8")
            content_2 = (p2 / f"{s}.csv").read_text(encoding="utf-8")
            assert content_1 == content_2, f"Split {s} was not byte-identical between runs with seed 42"


def test_dataset_integrity_audit_execution():
    """Verify that the full 11-point audit runs and all checks pass without error."""
    res = audit_dataset_integrity()
    assert res["all_checks_passed"] is True, f"Audit failed checks: {res['checks_passed']}"
    assert len(res["checks_passed"]) == 11, f"Expected 11 audit checks, got {len(res['checks_passed'])}"
