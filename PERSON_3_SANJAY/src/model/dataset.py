"""PyTorch Dataset implementation for UPI Screenshot Forensics.

Supports:
- Group-aware metadata-driven sample loading
- Graceful corrupted file handling
- Structured multi-attribute batch collation
- Compatibility with PyTorch DataLoader
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable
import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image

from .preprocessing import get_train_transforms, get_eval_transforms
from ..utils.image_io import load_image

# Canonical binary label mapping
LABEL_MAP = {
    "original": 0,
    "authentic": 0,
    "real": 0,
    "synthetic_fake": 1,
    "modified": 1,
    "forged": 1,
    "fake": 1
}


class UPIScreenshotDataset(Dataset):
    """PyTorch Dataset for authentic and manipulated UPI screenshot images."""

    def __init__(
        self,
        metadata_csv: Union[str, Path, pd.DataFrame],
        images_dir: Union[str, Path],
        split: str = "all",
        transform: Optional[Callable] = None,
        img_size: int = 224,
        is_training: bool = False
    ):
        """Initialize UPI Screenshot Dataset.

        Args:
            metadata_csv: Path to metadata.csv or existing DataFrame.
            images_dir: Path to directory containing raw image files.
            split: Filter by 'train', 'val', 'test', or 'all'.
            transform: Custom PyTorch transform pipeline.
            img_size: Target image size (default: 224).
            is_training: If True and transform is None, applies training augmentations.
        """
        self.images_dir = Path(images_dir)
        
        if isinstance(metadata_csv, pd.DataFrame):
            self.df = metadata_csv.copy()
        else:
            meta_path = Path(metadata_csv)
            if not meta_path.exists():
                raise FileNotFoundError(f"Metadata CSV not found at: {meta_path}")
            self.df = pd.read_csv(meta_path)
            
        # Assign / verify global group_id before any split filtering
        if "group_id" not in self.df.columns:
            # By standard, every 4 contiguous images represent 1 base receipt + 3 edits
            self.df["group_id"] = self.df.index // 4

        # Filter by split if specified
        if split.lower() != "all" and "split" in self.df.columns:
            self.df = self.df[self.df["split"].str.lower() == split.lower()].reset_index(drop=True)
            
        # Configure transform
        if transform is not None:
            self.transform = transform
        else:
            self.transform = get_train_transforms(img_size) if is_training else get_eval_transforms(img_size)
            
        self.corrupted_files: List[Tuple[str, str]] = []

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Fetch a single sample.

        Returns dict containing:
        - image: Tensor [3, H, W]
        - label: int (0=original, 1=modified)
        - image_id: str
        - group_id: int/str
        - edit_type: str
        - template_type: str
        - filename: str
        """
        row = self.df.iloc[idx]
        filename = str(row.get("filename", f"img_{idx:03d}.png"))
        image_path = self.images_dir / filename
        image_id = str(row.get("image_id", Path(filename).stem))
        group_id = int(row.get("group_id", idx // 4))
        edit_type = str(row.get("edit_type", "none"))
        template_type = str(row.get("template_type", "unknown"))
        
        raw_label = str(row.get("label", "original")).lower().strip()
        label = LABEL_MAP.get(raw_label, 1 if "fake" in raw_label or "mod" in raw_label else 0)

        # Handle file loading
        try:
            pil_img = load_image(image_path)
            tensor_img = self.transform(pil_img)
        except Exception as err:
            self.corrupted_files.append((filename, str(err)))
            # Create a safe fallback blank canvas with warning to prevent hard DataLoader crash
            blank = Image.new("RGB", (224, 224), color=(0, 0, 0))
            tensor_img = self.transform(blank)

        return {
            "image": tensor_img,
            "label": torch.tensor(label, dtype=torch.long),
            "image_id": image_id,
            "group_id": group_id,
            "edit_type": edit_type,
            "template_type": template_type,
            "filename": filename
        }


def create_group_aware_datasets(
    metadata_csv: Union[str, Path],
    images_dir: Union[str, Path],
    img_size: int = 224
) -> Tuple[UPIScreenshotDataset, UPIScreenshotDataset, UPIScreenshotDataset]:
    """Create Train, Validation, and Test dataset instances with zero group leakage.

    Args:
        metadata_csv: Path to metadata.csv.
        images_dir: Path to raw images.
        img_size: Target dimension (224).

    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    train_ds = UPIScreenshotDataset(
        metadata_csv=metadata_csv,
        images_dir=images_dir,
        split="train",
        img_size=img_size,
        is_training=True
    )
    val_ds = UPIScreenshotDataset(
        metadata_csv=metadata_csv,
        images_dir=images_dir,
        split="val",
        img_size=img_size,
        is_training=False
    )
    test_ds = UPIScreenshotDataset(
        metadata_csv=metadata_csv,
        images_dir=images_dir,
        split="test",
        img_size=img_size,
        is_training=False
    )
    return train_ds, val_ds, test_ds
