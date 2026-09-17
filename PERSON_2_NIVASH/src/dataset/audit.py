"""
Dataset Sanity Audit Script — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Audits data/metadata.csv against physical disk files, reporting:
- Total images and label breakdown
- Edit type distribution
- Per-family counts
- Variants-per-original statistics (min/median/max)
- Missing file verification (CSV vs. Disk)
- Unregistered disk file verification (Disk vs. CSV)
"""

import csv
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

from src.utils.paths import DATA_DIR, METADATA_CSV, PROCESSED_DIR, RAW_DIR


def audit_dataset(metadata_csv: Path = METADATA_CSV) -> Dict[str, Any]:
    """
    Perform rigorous consistency check on metadata.csv against data/raw/ and data/processed/.
    """
    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata CSV not found at {metadata_csv}")

    with open(metadata_csv, mode="r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_images = len(rows)
    label_counts: Dict[str, int] = {}
    edit_counts: Dict[str, int] = {}
    family_counts: Dict[str, int] = {}
    source_map: Dict[str, int] = {}

    missing_files_on_disk: List[str] = []
    registered_files: Set[str] = set()

    for r in rows:
        img_id = r["image_id"]
        src_id = r["source_id"]
        lbl = r["label"]
        edit = r["edit_type"]
        fam = r["template_family"]
        fname = r["filename"]
        rel_path = r["relative_path"]

        # Counts
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
        edit_counts[edit] = edit_counts.get(edit, 0) + 1
        family_counts[fam] = family_counts.get(fam, 0) + 1

        # Track variants per source
        source_map[src_id] = source_map.get(src_id, 0) + 1

        # Check physical existence on disk
        abs_path = DATA_DIR / rel_path
        if not abs_path.exists():
            missing_files_on_disk.append(str(rel_path))
        
        registered_files.add(fname)

    # Find unreferenced files on disk in raw/ and processed/
    disk_raw_files = {p.name for p in RAW_DIR.glob("*.png")} | {p.name for p in RAW_DIR.glob("*.jpg")}
    disk_proc_files = {p.name for p in PROCESSED_DIR.glob("*.png")} | {p.name for p in PROCESSED_DIR.glob("*.jpg")}
    all_disk_files = disk_raw_files | disk_proc_files

    unregistered_disk_files = list(all_disk_files - registered_files)

    # Calculate variant statistics
    # Each source has 1 original + (count - 1) variants
    variant_counts = [count - 1 for count in source_map.values()]
    min_var = min(variant_counts) if variant_counts else 0
    max_var = max(variant_counts) if variant_counts else 0
    med_var = statistics.median(variant_counts) if variant_counts else 0

    audit_result = {
        "total_images": total_images,
        "total_sources": len(source_map),
        "label_counts": label_counts,
        "edit_counts": edit_counts,
        "family_counts": family_counts,
        "variants_per_source": {
            "min": min_var,
            "median": med_var,
            "max": max_var,
        },
        "missing_files_on_disk": missing_files_on_disk,
        "unregistered_disk_files": unregistered_disk_files,
        "passed": (len(missing_files_on_disk) == 0 and len(unregistered_disk_files) == 0),
    }

    return audit_result


def print_audit_report(res: Dict[str, Any]) -> None:
    print("\n" + "=" * 60)
    print("DATASET SANITY AUDIT REPORT — PERSON 2")
    print("=" * 60)
    print(f"Total Registered Images : {res['total_images']}")
    print(f"Total Unique Sources   : {res['total_sources']}")
    print(f"Variants per Source    : Min={res['variants_per_source']['min']}, Median={res['variants_per_source']['median']}, Max={res['variants_per_source']['max']}")
    print("\n[Label Distribution]")
    for k, v in res["label_counts"].items():
        print(f"  • {k:22s}: {v:4d} ({v/res['total_images']*100:.1f}%)")
    
    print("\n[Edit Type Distribution]")
    for k, v in res["edit_counts"].items():
        print(f"  • {k:22s}: {v:4d}")
        
    print("\n[Template Family Distribution]")
    for k, v in res["family_counts"].items():
        print(f"  • Family {k:15s}: {v:4d}")

    print("\n[Disk Integrity Check]")
    if res["missing_files_on_disk"]:
        print(f"  ❌ FAILED: {len(res['missing_files_on_disk'])} CSV entries missing on disk:")
        for f in res["missing_files_on_disk"][:5]:
            print(f"     - {f}")
    else:
        print("  ✓ All CSV image entries exist on disk.")

    if res["unregistered_disk_files"]:
        print(f"  ⚠️ WARNING: {len(res['unregistered_disk_files'])} unreferenced files on disk:")
        for f in res["unregistered_disk_files"][:5]:
            print(f"     - {f}")
    else:
        print("  ✓ Zero orphan/unregistered image files on disk.")

    print("=" * 60)
    if res["passed"]:
        print("🎉 AUDIT PASSED: 100% Data Integrity Verified.\n")
    else:
        print("❌ AUDIT FAILED: Please reconcile discrepancies.\n")


def main() -> None:
    res = audit_dataset()
    print_audit_report(res)
    if not res["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
