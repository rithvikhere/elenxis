"""
Generates Leakage-Free Stratified Splits for Real UPI Dataset.
Follows Section 6 of the Project Specification:
- Groups by transaction_group_id so same transactions NEVER leak across splits
- Produces Standard Split (Train / Test)
- Produces Held-Out Device Split (evaluating model on completely unseen device)
- Writes splits to data/splits_real/
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.paths import REAL_METADATA_CSV, REAL_GROUND_TRUTH_CSV, REAL_SPLITS_DIR


def generate_real_splits():
    REAL_SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    meta_df = pd.read_csv(REAL_METADATA_CSV)
    gt_df = pd.read_csv(REAL_GROUND_TRUTH_CSV, dtype={"utr": str})

    # Merge transaction_group_id from ground truth into metadata
    df = pd.merge(meta_df, gt_df[["image_id", "transaction_group_id", "viewport"]], on="image_id", how="left")

    print(f"Total real images: {len(df)}")
    print(f"Unique transaction groups: {df['transaction_group_id'].nunique()}")

    # 1. Standard Leakage-Free Split (Group-stratified by transaction_group_id)
    # 15 unique transaction groups: 11 for train (~73%), 4 for test (~27%)
    unique_groups = df["transaction_group_id"].unique()
    rng = np.random.default_rng(seed=42)
    shuffled_groups = rng.permutation(unique_groups)

    test_groups = set(shuffled_groups[:4])
    train_groups = set(shuffled_groups[4:])

    train_df = df[df["transaction_group_id"].isin(train_groups)].copy()
    test_df = df[df["transaction_group_id"].isin(test_groups)].copy()

    train_path = REAL_SPLITS_DIR / "train.csv"
    test_path = REAL_SPLITS_DIR / "test.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"Standard Split: Train={len(train_df)} images ({len(train_groups)} groups), Test={len(test_df)} images ({len(test_groups)} groups)")

    # 2. Held-Out Device Split (Section 6.4)
    # dev_01 vs dev_02
    dev1_df = df[df["device_id"] == "dev_01"].copy()
    dev2_df = df[df["device_id"] == "dev_02"].copy()

    held_out_train_path = REAL_SPLITS_DIR / "held_out_device_train.csv"
    held_out_test_path = REAL_SPLITS_DIR / "held_out_device_test.csv"

    dev1_df.to_csv(held_out_train_path, index=False)
    dev2_df.to_csv(held_out_test_path, index=False)

    print(f"Held-Out Device Split: Train (dev_01)={len(dev1_df)} images, Held-out Test (dev_02)={len(dev2_df)} images")


if __name__ == "__main__":
    generate_real_splits()
