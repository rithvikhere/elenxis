"""
Unit Tests: Image Preprocessing Module.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).
"""

import sys
from pathlib import Path
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr.preprocess import (
    load_image, preprocess_image,
    to_grayscale, enhance_contrast,
    apply_threshold, apply_otsu_threshold, denoise_median,
)

SAMPLE_IMG = Path(__file__).parent.parent / "data" / "raw" / "img_001.png"


class TestLoadImage:
    def test_load_valid_path(self):
        img = load_image(str(SAMPLE_IMG))
        assert img.mode == "RGB"
        assert img.width > 0 and img.height > 0

    def test_load_pil_image(self):
        pil = Image.new("RGB", (100, 100), "white")
        img = load_image(pil)
        assert img.size == (100, 100)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_image("/nonexistent/path/img.png")

    def test_zero_dimension_pil_raises(self):
        pil = Image.new("RGB", (1, 1), "white")
        pil_zero = pil.crop((0, 0, 0, 0))
        with pytest.raises(ValueError):
            load_image(pil_zero)

    def test_returns_copy_not_reference(self):
        pil = Image.new("RGB", (50, 50), "red")
        loaded = load_image(pil)
        pil.close()
        assert loaded.getpixel((0, 0)) == (255, 0, 0)


class TestPreprocessingMethods:
    def setup_method(self):
        self.img = load_image(str(SAMPLE_IMG))

    def test_to_grayscale(self):
        gray = to_grayscale(self.img)
        assert gray.mode == "L"
        assert gray.size == self.img.size

    def test_enhance_contrast(self):
        out = enhance_contrast(self.img, factor=2.0)
        assert out.mode == "L"
        assert out.size == self.img.size

    def test_apply_threshold(self):
        out = apply_threshold(self.img, threshold=160)
        assert out.mode == "L"
        pixels = set(out.getdata())
        assert pixels.issubset({0, 255})

    def test_apply_otsu_threshold(self):
        out = apply_otsu_threshold(self.img)
        assert out.mode in ("L", "1")

    def test_denoise_median(self):
        out = denoise_median(self.img, size=3)
        assert out.mode == "L"


class TestPreprocessImageDispatcher:
    def setup_method(self):
        self.path = str(SAMPLE_IMG)

    def test_raw_mode(self):
        out = preprocess_image(self.path, method="raw")
        assert out.mode == "RGB"

    def test_grayscale_mode(self):
        out = preprocess_image(self.path, method="grayscale")
        assert out.mode == "L"

    def test_contrast_mode(self):
        out = preprocess_image(self.path, method="contrast")
        assert out.mode == "L"

    def test_otsu_mode(self):
        out = preprocess_image(self.path, method="otsu")
        assert out is not None

    def test_threshold_mode(self):
        out = preprocess_image(self.path, method="threshold")
        assert out.mode == "L"

    def test_denoise_mode(self):
        out = preprocess_image(self.path, method="denoise")
        assert out.mode == "L"

    def test_unknown_method_falls_back_to_contrast(self):
        out = preprocess_image(self.path, method="xyz_unknown")
        assert out.mode == "L"
