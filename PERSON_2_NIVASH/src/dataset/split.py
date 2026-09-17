"""
Leakage-Safe Dataset Splitting Module — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Partitions the dataset into train, validation, and test splits strictly by grouping on
source_id (never image_id). Guarantees that all variants of an original receipt reside
within the exact same split, preventing data leakage.
Stratifies at the group level by template_family.
"""

import argparse
import csv
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.dataset import config
from src.utils.paths import DATA_DIR, METADATA_CSV, SPLITS_DIR, ensure_dir


def split_dataset(
    metadata_csv: Optional[Path] = None,
    splits_dir: Optional[Path] = None,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = config.RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Partition metadata.csv into train, val, and test manifests grouped strictly by source_id.
    
    Args:
        metadata_csv: Path to data/metadata.csv.
        splits_dir: Path to output directory data/splits/.
        train_ratio: Target proportion for training set (default 0.70).
        val_ratio: Target proportion for validation set (default 0.15).
        test_ratio: Target proportion for test set (default 0.15).
        seed: Random seed for deterministic group assignment.
        
    Returns:
        Summary dictionary with realized group and image counts per split.
    """
    if metadata_csv is None:
        metadata_csv = METADATA_CSV
    if splits_dir is None:
        splits_dir = SPLITS_DIR

    metadata_csv = Path(metadata_csv)
    splits_dir = Path(splits_dir)
    ensure_dir(splits_dir)

    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata CSV not found at {metadata_csv}. Run Phase 3 generator first.")

    with open(metadata_csv, mode="r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 1. Group rows by source_id and record template_family per group
    groups: Dict[str, List[Dict[str, Any]]] = {}
    group_family: Dict[str, int] = {}

    for r in rows:
        src = r["source_id"]
        if src not in groups:
            groups[src] = []
            group_family[src] = int(r["template_family"])
        groups[src].append(r)

    # 2. Stratify sources by template_family
    sources_by_family: Dict[int, List[str]] = {1: [], 2: [], 3: []}
    for src, fam in group_family.items():
        sources_by_family[fam].append(src)

    rng = random.Random(seed)
    train_sources: List[str] = []
    val_sources: List[str] = []
    test_sources: List[str] = []

    # 3. For each family, partition sources deterministically
    for fam_id, src_list in sources_by_family.items():
        shuffled = list(src_list)
        rng.shuffle(shuffled)
        
        n_total = len(shuffled)
        n_train = int(round(n_total * train_ratio))
        n_val = int(round(n_total * val_ratio))
        
        # Ensure remaining sources go to test
        train_part = shuffled[:n_train]
        val_part = shuffled[n_train:n_train + n_val]
        test_part = shuffled[n_train + n_val:]

        train_sources.extend(train_part)
        val_sources.extend(val_part)
        test_sources.extend(test_part)

    # Convert source sets for rapid membership testing
    train_src_set = set(train_sources)
    val_src_set = set(val_sources)
    test_src_set = set(test_sources)

    # 4. Assemble split manifests
    split_manifests: Dict[str, List[Dict[str, Any]]] = {
        "train": [],
        "val": [],
        "test": [],
    }

    manifest_fieldnames = [
        "image_id",
        "source_id",
        "template_family",
        "label",
        "edit_type",
        "filename",
        "relative_path",
        "split",
    ]

    for src, item_rows in groups.items():
        if src in train_src_set:
            split_name = "train"
        elif src in val_src_set:
            split_name = "val"
        elif src in test_src_set:
            split_name = "test"
        else:
            raise ValueError(f"Orphan source_id {src} not allocated to any split.")

        for item in item_rows:
            manifest_row = {
                "image_id": item["image_id"],
                "source_id": item["source_id"],
                "template_family": item["template_family"],
                "label": item["label"],
                "edit_type": item["edit_type"],
                "filename": item["filename"],
                "relative_path": item["relative_path"],
                "split": split_name,
            }
            split_manifests[split_name].append(manifest_row)

    # 5. Write CSV manifests
    for split_name, manifest_rows in split_manifests.items():
        out_csv = splits_dir / f"{split_name}.csv"
        with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=manifest_fieldnames)
            writer.writeheader()
            for r in manifest_rows:
                writer.writerow(r)

    total_images = len(rows)
    summary = {
        "total_images": total_images,
        "total_sources": len(groups),
        "splits": {
            "train": {
                "sources": len(train_sources),
                "images": len(split_manifests["train"]),
                "realized_ratio": len(split_manifests["train"]) / total_images if total_images else 0,
            },
            "val": {
                "sources": len(val_sources),
                "images": len(split_manifests["val"]),
                "realized_ratio": len(split_manifests["val"]) / total_images if total_images else 0,
            },
            "test": {
                "sources": len(test_sources),
                "images": len(split_manifests["test"]),
                "realized_ratio": len(split_manifests["test"]) / total_images if total_images else 0,
            },
        },
        "splits_dir": str(splits_dir),
        "seed": seed,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate leakage-safe group-aware train/val/test splits.")
    parser.add_argument("--train", type=float, default=0.70, help="Train ratio (default: 0.70)")
    parser.add_argument("--val", type=float, default=0.15, help="Validation ratio (default: 0.15)")
    parser.add_argument("--test", type=float, default=0.15, help="Test ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED, help="Random seed for deterministic split")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("UPI Fraud Forensics — Person 2: Leakage-Safe Dataset Splitter")
    print("=" * 60)
    print(f"Target Ratios : Train={args.train*100:.0f}%, Val={args.val*100:.0f}%, Test={args.test*100:.0f}% (Seed: {args.seed})")

    res = split_dataset(
        train_ratio=args.train,
        val_ratio=args.val,
        test_ratio=args.test,
        seed=args.seed,
    )

    print("\nRealized Split Summary:")
    for s_name, s_data in res["splits"].items():
        print(f"  • {s_name.upper():5s} Split : {s_data['sources']:2d} sources -> {s_data['images']:3d} images ({s_data['realized_ratio']*100:.1f}%)")
    print(f"\nManifests written to: {res['splits_dir']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
