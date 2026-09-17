"""PyTorch Dataset definitions and data preparation for UPI Screenshot Forensics."""

from pathlib import Path
from typing import List, Tuple, Optional, Callable
from PIL import Image
import torch
from torch.utils.data import Dataset, random_split

from .cnn_model import get_default_transform
from ..utils.image_io import load_image


class UPIScreenshotDataset(Dataset):
    """Dataset for real and synthetically manipulated UPI payment screenshots."""

    def __init__(
        self,
        samples: List[Tuple[Path, int]],
        transform: Optional[Callable] = None
    ):
        """Initialize dataset with a list of (image_path, label) pairs.

        Label encoding:
            0: Original / Authentic
            1: Modified / Synthetic / Forged
        """
        self.samples = samples
        self.transform = transform or get_default_transform()

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        img = load_image(img_path)
        
        if self.transform is not None:
            tensor_img = self.transform(img)
        else:
            tensor_img = get_default_transform()(img)
            
        return tensor_img, label


def create_train_val_test_splits(
    dataset: Dataset,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[Dataset, Dataset, Dataset]:
    """Deterministically split a dataset into train, validation, and test subsets."""
    total = len(dataset)
    train_len = int(total * train_ratio)
    val_len = int(total * val_ratio)
    test_len = total - train_len - val_len
    
    generator = torch.Generator().manual_seed(seed)
    return random_split(dataset, [train_len, val_len, test_len], generator=generator)
