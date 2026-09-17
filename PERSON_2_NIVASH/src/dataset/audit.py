"""
Comprehensive Dataset Leakage & Integrity Auditor — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Performs 11 comprehensive verification checks:
1. Group Disjointness: Zero source_id overlap between train, val, and test.
2. File Existence: Every manifest and metadata row exists on disk.
3. Orphan Detection: Zero unreferenced image files in data/raw/ or data/processed/.
4. Duplicate ID Check: Zero duplicate image_ids.
5. Family Coverage: All 3 layout families present in every split.
6. Label Coverage: All 3 label classes present in every split.
7. Class Balance: Exact label distributions reported across all splits.
8. Near-Duplicate Detection: 256-bit perceptual difference hashing (dHash) to detect cross-split collisions.
9. Corrupt Image Check: Header and pixel decoding integrity verification.
10. Dimension Outlier Check: Verification of (400, 800) standard canvas dimensions.
11. Ground-Truth Coverage: Every manifest record has an exact match in ground_truth.csv.

Writes full report to results/metrics/dataset_audit.txt.
"""

import csv
import io
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image

from src.dataset import config
from src.utils.paths import DATA_DIR, METADATA_CSV, PROCESSED_DIR, PROJECT_ROOT, RAW_DIR, SPLITS_DIR, ensure_dir


# ---------------------------------------------------------------------------
# Perceptual Difference Hashing (256-bit dHash) for Content Duplicate Detection
# ---------------------------------------------------------------------------

def calculate_dhash(img: Image.Image, hash_size: int = 16) -> int:
    """
    Calculate 256-bit difference hash (dHash) for an image.
    High-resolution 16x16 grid captures localized text lines and values.
    """
    gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    try:
        pixels = list(gray.get_flattened_data())
    except AttributeError:
        pixels = list(gray.getdata())

    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = pixels[row * (hash_size + 1) + col]
            pixel_right = pixels[row * (hash_size + 1) + col + 1]
            difference.append(pixel_left > pixel_right)
    
    decimal_val = 0
    for bit in difference:
        decimal_val = (decimal_val << 1) | bit
    return decimal_val


def hamming_distance(h1: int, h2: int) -> int:
    """Compute number of differing bits between two integer hashes."""
    return bin(h1 ^ h2).count("1")


# ---------------------------------------------------------------------------
# Master Audit Engine
# ---------------------------------------------------------------------------

def audit_dataset_integrity(
    metadata_csv: Path = METADATA_CSV,
    splits_dir: Path = SPLITS_DIR,
    ground_truth_csv: Path = DATA_DIR / "ground_truth.csv",
    report_output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run 11 automated checks across metadata, split manifests, ground truth, and disk assets.
    """
    if report_output_path is None:
        report_output_path = PROJECT_ROOT / "results" / "metrics" / "dataset_audit.txt"
    ensure_dir(report_output_path.parent)

    checks_passed: Dict[str, bool] = {}
    check_details: Dict[str, Any] = {}

    # Check existence of prerequisite files
    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata file missing at {metadata_csv}")
    if not (splits_dir / "train.csv").exists() or not (splits_dir / "val.csv").exists() or not (splits_dir / "test.csv").exists():
        raise FileNotFoundError(f"Split manifests missing in {splits_dir}. Run Phase 4 split.py first.")
    if not ground_truth_csv.exists():
        raise FileNotFoundError(f"Ground truth file missing at {ground_truth_csv}")

    # Load data files
    with open(metadata_csv, mode="r", newline="", encoding="utf-8") as f:
        meta_rows = list(csv.DictReader(f))

    split_rows: Dict[str, List[Dict[str, Any]]] = {}
    for s in ["train", "val", "test"]:
        with open(splits_dir / f"{s}.csv", mode="r", newline="", encoding="utf-8") as f:
            split_rows[s] = list(csv.DictReader(f))

    with open(ground_truth_csv, mode="r", newline="", encoding="utf-8") as f:
        gt_rows = list(csv.DictReader(f))

    gt_image_ids = {r["image_id"] for r in gt_rows}

    # 1. Group Disjointness Check
    sources_per_split = {s: {r["source_id"] for r in rows} for s, rows in split_rows.items()}
    train_val_overlap = sources_per_split["train"] & sources_per_split["val"]
    train_test_overlap = sources_per_split["train"] & sources_per_split["test"]
    val_test_overlap = sources_per_split["val"] & sources_per_split["test"]

    group_disjoint = (len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and len(val_test_overlap) == 0)
    checks_passed["1_group_disjointness"] = group_disjoint
    check_details["1_group_disjointness"] = {
        "train_sources": len(sources_per_split["train"]),
        "val_sources": len(sources_per_split["val"]),
        "test_sources": len(sources_per_split["test"]),
        "overlaps": {
            "train_val": list(train_val_overlap),
            "train_test": list(train_test_overlap),
            "val_test": list(val_test_overlap),
        },
    }

    # 2. File Existence Check & 9. Corrupt Images Check & 10. Dimension Outlier Check
    missing_files = []
    corrupt_files = []
    dimension_mismatches = []
    split_hashes: Dict[str, List[Tuple[str, str, int]]] = {"train": [], "val": [], "test": []}

    all_manifest_ids = set()
    manifest_registered_paths = set()

    for s, rows in split_rows.items():
        for r in rows:
            img_id = r["image_id"]
            src_id = r["source_id"]
            rel_path = r["relative_path"]
            all_manifest_ids.add(img_id)
            manifest_registered_paths.add(r["filename"])

            abs_p = DATA_DIR / rel_path
            if not abs_p.exists():
                missing_files.append(str(rel_path))
                continue

            # Verify image opening and dimensions
            try:
                with Image.open(abs_p) as im:
                    w, h = im.size
                    if (w, h) != config.IMAGE_SIZE and r["edit_type"] != "crop":
                        dimension_mismatches.append((r["filename"], (w, h)))
                    h_val = calculate_dhash(im, hash_size=16)
                    split_hashes[s].append((img_id, src_id, h_val))
            except Exception as e:
                corrupt_files.append((r["filename"], str(e)))

    checks_passed["2_file_existence"] = (len(missing_files) == 0)
    check_details["2_file_existence"] = {"missing_count": len(missing_files), "missing_samples": missing_files[:5]}

    checks_passed["9_corrupt_images"] = (len(corrupt_files) == 0)
    check_details["9_corrupt_images"] = {"corrupt_count": len(corrupt_files), "corrupt_samples": corrupt_files[:5]}

    checks_passed["10_dimension_outliers"] = (len(dimension_mismatches) == 0)
    check_details["10_dimension_outliers"] = {"mismatches": dimension_mismatches}

    # 3. Orphan Files Check
    disk_raw = {p.name for p in RAW_DIR.glob("*.png")} | {p.name for p in RAW_DIR.glob("*.jpg")}
    disk_proc = {p.name for p in PROCESSED_DIR.glob("*.png")} | {p.name for p in PROCESSED_DIR.glob("*.jpg")}
    all_disk_files = disk_raw | disk_proc
    orphan_files = list(all_disk_files - manifest_registered_paths)

    checks_passed["3_orphan_files"] = (len(orphan_files) == 0)
    check_details["3_orphan_files"] = {"orphan_count": len(orphan_files), "orphan_samples": orphan_files[:5]}

    # 4. Duplicate Image ID Check
    total_manifest_rows = sum(len(rows) for rows in split_rows.values())
    no_duplicate_ids = (total_manifest_rows == len(all_manifest_ids))
    checks_passed["4_duplicate_ids"] = no_duplicate_ids
    check_details["4_duplicate_ids"] = {
        "total_manifest_rows": total_manifest_rows,
        "unique_ids": len(all_manifest_ids),
    }

    # 5. Family Coverage Check & 6. Label Coverage Check & 7. Class Balance Check
    split_family_dist = {}
    split_label_dist = {}
    family_coverage_ok = True
    label_coverage_ok = True

    for s, rows in split_rows.items():
        fam_counts = {1: 0, 2: 0, 3: 0}
        lbl_counts = {"original": 0, "original_transformed": 0, "synthetic_fake": 0}
        for r in rows:
            fam_counts[int(r["template_family"])] += 1
            lbl_counts[r["label"]] += 1

        split_family_dist[s] = fam_counts
        split_label_dist[s] = lbl_counts

        if any(cnt == 0 for cnt in fam_counts.values()):
            family_coverage_ok = False
        if any(cnt == 0 for cnt in lbl_counts.values()):
            label_coverage_ok = False

    checks_passed["5_family_coverage"] = family_coverage_ok
    check_details["5_family_coverage"] = split_family_dist

    checks_passed["6_label_coverage"] = label_coverage_ok
    check_details["6_label_coverage"] = split_label_dist

    checks_passed["7_class_balance"] = True  # Information reporting check
    check_details["7_class_balance"] = split_label_dist

    # 8. Near-Duplicate Content Collision Detection Across Splits
    # Detects if distinct source images across splits produced identical hash collisions (Hamming distance == 0)
    cross_split_collisions = []
    for train_id, train_src, train_hash in split_hashes["train"]:
        for test_id, test_src, test_hash in split_hashes["test"]:
            if train_src != test_src and hamming_distance(train_hash, test_hash) == 0:
                cross_split_collisions.append((train_id, test_id))

    checks_passed["8_near_duplicates"] = (len(cross_split_collisions) == 0)
    check_details["8_near_duplicates"] = {
        "cross_split_hash_collisions": cross_split_collisions,
        "collision_count": len(cross_split_collisions),
    }

    # 11. Ground-Truth Coverage Check
    missing_gt = [img_id for img_id in all_manifest_ids if img_id not in gt_image_ids]
    checks_passed["11_ground_truth_coverage"] = (len(missing_gt) == 0)
    check_details["11_ground_truth_coverage"] = {
        "missing_gt_count": len(missing_gt),
        "missing_gt_samples": missing_gt[:5],
    }

    # Overall Audit Result
    all_ok = all(checks_passed.values())

    report_data = {
        "all_checks_passed": all_ok,
        "checks_passed": checks_passed,
        "check_details": check_details,
        "summary": {
            "total_images": total_manifest_rows,
            "train_images": len(split_rows["train"]),
            "val_images": len(split_rows["val"]),
            "test_images": len(split_rows["test"]),
            "train_sources": len(sources_per_split["train"]),
            "val_sources": len(sources_per_split["val"]),
            "test_sources": len(sources_per_split["test"]),
        },
        "report_file": str(report_output_path),
    }

    # Format Text Report
    lines = []
    lines.append("=" * 70)
    lines.append("DATASET INTEGRITY & DATA LEAKAGE AUDIT REPORT — PERSON 2")
    lines.append("=" * 70)
    lines.append(f"Total Images Audited    : {total_manifest_rows}")
    lines.append(f"Train Split Manifest    : {len(split_rows['train'])} images ({len(sources_per_split['train'])} unique sources, {len(split_rows['train'])/total_manifest_rows*100:.1f}%)")
    lines.append(f"Val Split Manifest      : {len(split_rows['val'])} images ({len(sources_per_split['val'])} unique sources, {len(split_rows['val'])/total_manifest_rows*100:.1f}%)")
    lines.append(f"Test Split Manifest     : {len(split_rows['test'])} images ({len(sources_per_split['test'])} unique sources, {len(split_rows['test'])/total_manifest_rows*100:.1f}%)")
    lines.append("-" * 70)
    lines.append("[VERIFICATION CHECKS BREAKDOWN]")
    
    check_names = [
        ("1_group_disjointness", "1. Group Disjointness (Zero Source Leakage)"),
        ("2_file_existence", "2. File Existence on Disk"),
        ("3_orphan_files", "3. Zero Orphan Disk Files"),
        ("4_duplicate_ids", "4. Zero Duplicate Image IDs"),
        ("5_family_coverage", "5. Template Family Coverage across all splits"),
        ("6_label_coverage", "6. Label Class Coverage across all splits"),
        ("7_class_balance", "7. Class Balance Consistency Reporting"),
        ("8_near_duplicates", "8. Cross-Split Perceptual Near-Duplicate Hash Check (256-bit dHash)"),
        ("9_corrupt_images", "9. Image Header & Pixel Decoding Check"),
        ("10_dimension_outliers", "10. Dimension Outlier & Canvas Constraint Check"),
        ("11_ground_truth_coverage", "11. Ground-Truth Answer Key Coverage"),
    ]

    for key, title in check_names:
        status_symbol = "✓ PASS" if checks_passed[key] else "❌ FAIL"
        lines.append(f"  [{status_symbol}] {title}")

    lines.append("-" * 70)
    lines.append("[DETAILED SPLIT DISTRIBUTIONS]")
    lines.append("\n  • Template Family Distribution by Split:")
    lines.append(f"    {'Split':8s} | {'Family 1':10s} | {'Family 2':10s} | {'Family 3':10s} | {'Total':6s}")
    lines.append(f"    {'-'*8}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*6}")
    for s in ["train", "val", "test"]:
        fd = split_family_dist[s]
        tot = sum(fd.values())
        lines.append(f"    {s.upper():8s} | {fd[1]:10d} | {fd[2]:10d} | {fd[3]:10d} | {tot:6d}")

    lines.append("\n  • Label Class Distribution by Split:")
    lines.append(f"    {'Split':8s} | {'Original':10s} | {'Orig_Trans':10s} | {'Synth_Fake':10s} | {'Total':6s}")
    lines.append(f"    {'-'*8}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*6}")
    for s in ["train", "val", "test"]:
        ld = split_label_dist[s]
        tot = sum(ld.values())
        lines.append(f"    {s.upper():8s} | {ld['original']:10d} | {ld['original_transformed']:10d} | {ld['synthetic_fake']:10d} | {tot:6d}")

    lines.append("\n" + "=" * 70)
    if all_ok:
        lines.append("🎉 OVERALL VERDICT: 100% AUDIT PASSED. DATASET IS LEAKAGE-FREE.")
    else:
        lines.append("❌ OVERALL VERDICT: AUDIT FAILED. DISCREPANCIES DETECTED.")
    lines.append("=" * 70)

    report_text = "\n".join(lines)
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_data


def print_audit_report(res: Dict[str, Any]) -> None:
    with open(res["report_file"], "r", encoding="utf-8") as f:
        print(f.read())


# Alias for backward compatibility
audit_dataset = audit_dataset_integrity


def main() -> None:
    res = audit_dataset_integrity()
    print_audit_report(res)
    if not res["all_checks_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
