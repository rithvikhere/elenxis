"""
Image Preprocessing Module for OCR Pipeline.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Provides robust image loading/validation and targeted preprocessing filters
(grayscale, contrast enhancement, Otsu binarization, denoising)
to optimise Tesseract character recognition on digital UPI receipt screenshots.
"""

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


# ---------------------------------------------------------------------------
# Image Loading & Validation
# ---------------------------------------------------------------------------

def load_image(image_input: Union[str, Path, "Image.Image"]) -> "Image.Image":
    """
    Validates and loads an image into a PIL Image instance.

    Raises:
        FileNotFoundError: Path does not exist.
        ValueError: File is unreadable or has zero dimensions.
    """
    if isinstance(image_input, Image.Image):
        if image_input.width == 0 or image_input.height == 0:
            raise ValueError("Provided PIL Image has zero dimension.")
        return image_input.copy()

    path = Path(image_input)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    try:
        with Image.open(path) as img:
            loaded = img.convert("RGB")
            if loaded.width == 0 or loaded.height == 0:
                raise ValueError(f"Image at {path} has invalid dimensions.")
            return loaded
    except Exception as exc:
        if isinstance(exc, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Cannot decode image '{path}': {exc}") from exc


# Alias — kept for backwards compat
validate_image = load_image


# ---------------------------------------------------------------------------
# Preprocessing Transforms
# ---------------------------------------------------------------------------

def to_grayscale(image: "Image.Image") -> "Image.Image":
    return image.convert("L")


def enhance_contrast(image: "Image.Image", factor: float = 2.0) -> "Image.Image":
    return ImageEnhance.Contrast(to_grayscale(image)).enhance(factor)


def apply_threshold(image: "Image.Image", threshold: int = 160) -> "Image.Image":
    gray = to_grayscale(image)
    return gray.point(lambda p: 255 if p > threshold else 0, mode="1").convert("L")


def apply_otsu_threshold(image: "Image.Image") -> "Image.Image":
    """Otsu's method via NumPy histogram — maximises inter-class variance."""
    arr = np.array(to_grayscale(image), dtype=np.uint8)
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    total = arr.size
    best_var, threshold = 0.0, 128
    w_bg = sum_bg = 0
    total_sum = int(np.dot(np.arange(256), hist))

    for i in range(256):
        w_bg += int(hist[i])
        if w_bg == 0:
            continue
        w_fg = total - w_bg
        if w_fg == 0:
            break
        sum_bg += i * int(hist[i])
        mb = sum_bg / w_bg
        mf = (total_sum - sum_bg) / w_fg
        var = w_bg * w_fg * (mb - mf) ** 2
        if var > best_var:
            best_var, threshold = var, i

    return Image.fromarray(np.where(arr > threshold, 255, 0).astype(np.uint8))


def denoise_median(image: "Image.Image", size: int = 3) -> "Image.Image":
    return to_grayscale(image).filter(ImageFilter.MedianFilter(size=size))


# ---------------------------------------------------------------------------
# Master Preprocessing Dispatcher
# ---------------------------------------------------------------------------

def preprocess_image(
    image_input: Union[str, Path, "Image.Image"],
    method: str = "contrast",
) -> "Image.Image":
    """
    Selects and applies a preprocessing pipeline optimised for Tesseract.

    Args:
        image_input: File path or PIL Image.
        method: 'raw' | 'grayscale' | 'contrast' (default) |
                'otsu' | 'threshold' | 'denoise'

    Returns:
        Preprocessed PIL.Image ready for pytesseract.
    """
    img = load_image(image_input)
    m = (method or "contrast").lower().strip()

    if m in ("raw", "none"):
        return img
    if m == "grayscale":
        return to_grayscale(img)
    if m == "contrast":
        return enhance_contrast(img, factor=2.0)
    if m == "otsu":
        return apply_otsu_threshold(img)
    if m == "threshold":
        return apply_threshold(img, 160)
    if m == "denoise":
        return denoise_median(enhance_contrast(img, 1.8), 3)
    # Default fallback
    return enhance_contrast(img, factor=2.0)
