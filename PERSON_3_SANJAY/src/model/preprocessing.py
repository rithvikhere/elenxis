"""Preprocessing and conservative augmentation pipeline for UPI screenshot forensics.

Forensics Rationale:
Aggressive transformations (such as large random crops, random rotations, strong blurring,
or horizontal flipping) must be strictly avoided in financial screenshot analysis because:
1. Horizontal flipping creates mirror-reversed text, corrupting semantic layout.
2. Large crops can eliminate the exact region where the amount/date/UTR tampering occurred.
3. Strong blurring or heavy compression jitter destroys micro-level pixel noise and
   compression boundaries needed to distinguish tampered from authentic regions.

Therefore, our training preprocessing applies conservative transformations, while
evaluation and test preprocessing is 100% deterministic.
"""

from typing import Union, Tuple
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

from ..utils.image_io import load_image

# Standard ImageNet normalization parameters
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_transforms(
    img_size: int = 224,
    conservative: bool = True
) -> transforms.Compose:
    """Return PyTorch transform pipeline for training.

    Args:
        img_size: Target image height and width (default: 224).
        conservative: If True, uses subtle, forensics-safe augmentations.

    Returns:
        torchvision.transforms.Compose pipeline.
    """
    transform_list = [
        transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR),
    ]
    
    if conservative:
        # Forensics-safe subtle brightness/contrast variations (+/- 5%)
        # Simulates different screen backlight settings without destroying edges
        transform_list.append(
            transforms.ColorJitter(brightness=0.05, contrast=0.05)
        )
        
    transform_list.extend([
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])
    
    return transforms.Compose(transform_list)


def get_eval_transforms(img_size: int = 224) -> transforms.Compose:
    """Return deterministic PyTorch transform pipeline for validation and test.

    Args:
        img_size: Target image height and width (default: 224).

    Returns:
        torchvision.transforms.Compose pipeline.
    """
    return transforms.Compose([
        transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def preprocess_image_tensor(
    image_input: Union[str, Image.Image, np.ndarray, bytes],
    is_training: bool = False,
    img_size: int = 224
) -> torch.Tensor:
    """Safely preprocess a single image into a model-ready batch tensor [1, 3, H, W].

    Args:
        image_input: Candidate image in any supported format.
        is_training: Whether to apply training augmentations.
        img_size: Target spatial dimension (default: 224).

    Returns:
        torch.Tensor of shape [1, 3, img_size, img_size].
    """
    pil_img = load_image(image_input)
    transform = get_train_transforms(img_size) if is_training else get_eval_transforms(img_size)
    tensor = transform(pil_img)  # Shape [3, H, W]
    return tensor.unsqueeze(0)   # Shape [1, 3, H, W]
