"""Unit tests for dataset loading, preprocessing, group-aware splitting, and tensor shapes."""

from pathlib import Path
import pytest
import pandas as pd
import torch
from torch.utils.data import DataLoader
from PIL import Image

from PERSON_3_SANJAY.src.model.dataset import (
    UPIScreenshotDataset,
    create_group_aware_datasets,
    LABEL_MAP
)
from PERSON_3_SANJAY.src.model.preprocessing import (
    get_train_transforms,
    get_eval_transforms,
    preprocess_image_tensor
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
METADATA_PATH = REPO_ROOT / "PERSON_2_NIVASH" / "data" / "metadata.csv"
IMAGES_DIR = REPO_ROOT / "PERSON_2_NIVASH" / "data" / "raw"


def test_label_mapping():
    """Verify standard binary label mappings."""
    assert LABEL_MAP["original"] == 0
    assert LABEL_MAP["synthetic_fake"] == 1
    assert LABEL_MAP["forged"] == 1
    assert LABEL_MAP["real"] == 0


def test_preprocessing_transforms():
    """Verify transform output tensor shapes and value ranges."""
    dummy_img = Image.new("RGB", (300, 600), color=(100, 150, 200))
    
    train_tf = get_train_transforms(img_size=224)
    eval_tf = get_eval_transforms(img_size=224)
    
    t_train = train_tf(dummy_img)
    t_eval = eval_tf(dummy_img)
    
    assert isinstance(t_train, torch.Tensor)
    assert t_train.shape == (3, 224, 224)
    assert t_eval.shape == (3, 224, 224)
    
    # Preprocess single image tensor utility
    batch_t = preprocess_image_tensor(dummy_img, is_training=False, img_size=224)
    assert batch_t.shape == (1, 3, 224, 224)


def test_dataset_loading_and_attributes():
    """Verify loading from Person 2's dataset with metadata attributes."""
    if not METADATA_PATH.exists() or not IMAGES_DIR.exists():
        pytest.skip("Dataset path not available in test environment.")

    dataset = UPIScreenshotDataset(
        metadata_csv=METADATA_PATH,
        images_dir=IMAGES_DIR,
        split="all"
    )
    
    assert len(dataset) == 60
    
    sample = dataset[0]
    assert "image" in sample
    assert "label" in sample
    assert "image_id" in sample
    assert "group_id" in sample
    assert "edit_type" in sample
    assert sample["image"].shape == (3, 224, 224)
    assert sample["label"].item() in (0, 1)


def test_group_aware_splits_and_leakage():
    """Verify train, val, test split isolation and zero group leakage."""
    if not METADATA_PATH.exists() or not IMAGES_DIR.exists():
        pytest.skip("Dataset path not available in test environment.")

    train_ds, val_ds, test_ds = create_group_aware_datasets(
        metadata_csv=METADATA_PATH,
        images_dir=IMAGES_DIR,
        img_size=224
    )
    
    assert len(train_ds) == 36
    assert len(val_ds) == 12
    assert len(test_ds) == 12
    
    train_groups = set(train_ds.df["group_id"].unique())
    val_groups = set(val_ds.df["group_id"].unique())
    test_groups = set(test_ds.df["group_id"].unique())
    
    # Assert zero overlap across splits
    assert len(train_groups.intersection(val_groups)) == 0, "Data leakage between train and val!"
    assert len(train_groups.intersection(test_groups)) == 0, "Data leakage between train and test!"
    assert len(val_groups.intersection(test_groups)) == 0, "Data leakage between val and test!"


def test_dataloader_batch_compatibility():
    """Verify PyTorch DataLoader batch collation."""
    if not METADATA_PATH.exists() or not IMAGES_DIR.exists():
        pytest.skip("Dataset path not available in test environment.")

    train_ds, _, _ = create_group_aware_datasets(
        metadata_csv=METADATA_PATH,
        images_dir=IMAGES_DIR,
        img_size=224
    )
    
    loader = DataLoader(train_ds, batch_size=4, shuffle=True)
    batch = next(iter(loader))
    
    assert batch["image"].shape == (4, 3, 224, 224)
    assert batch["label"].shape == (4,)
    assert len(batch["image_id"]) == 4
    assert len(batch["group_id"]) == 4


def test_corrupted_image_graceful_handling(tmp_path):
    """Verify corrupted or missing image files do not crash the dataset loader."""
    dummy_meta = pd.DataFrame([
        {"filename": "non_existent.png", "image_id": "img_missing", "label": "original", "split": "train", "group_id": 0}
    ])
    
    ds = UPIScreenshotDataset(
        metadata_csv=dummy_meta,
        images_dir=tmp_path,
        split="train"
    )
    
    sample = ds[0]
    assert sample["image"].shape == (3, 224, 224)
    assert len(ds.corrupted_files) == 1

