"""Unit tests for Image Forensics (ELA & Metadata)."""

import pytest
import numpy as np
from PIL import Image, ImageDraw

from PERSON_3_SANJAY.src.forensics.ela import compute_ela
from PERSON_3_SANJAY.src.forensics.metadata import inspect_metadata
from PERSON_3_SANJAY.src.forensics.forensics_engine import analyze_image


@pytest.fixture
def synthetic_sample_image():
    """Create a basic synthetic UPI-like payment receipt image for testing."""
    img = Image.new("RGB", (300, 500), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 280, 100], fill=(220, 235, 250))
    draw.text((30, 40), "Paid to Merchant", fill=(20, 20, 20))
    draw.text((30, 70), "INR 500.00", fill=(0, 120, 0))
    return img


def test_compute_ela_structure(synthetic_sample_image):
    """Test that ELA computation returns valid image and expected metrics."""
    ela_img, metrics = compute_ela(synthetic_sample_image, quality=90, scale_factor=15.0)
    
    assert isinstance(ela_img, Image.Image)
    assert ela_img.size == synthetic_sample_image.size
    assert "mean_error" in metrics
    assert "max_error" in metrics
    assert "anomaly_score" in metrics
    assert 0.0 <= metrics["anomaly_score"] <= 1.0
    assert len(metrics["indicators"]) > 0


def test_inspect_metadata(synthetic_sample_image):
    """Test metadata inspection on an in-memory image."""
    meta = inspect_metadata(synthetic_sample_image)
    
    assert isinstance(meta, dict)
    assert "has_exif" in meta
    assert "editing_software_detected" in meta
    assert isinstance(meta["indicators"], list)
    assert isinstance(meta["limitations"], list)


def test_analyze_image_contract(synthetic_sample_image):
    """Test the unified forensics contract."""
    res = analyze_image(synthetic_sample_image)
    
    assert res["status"] == "available"
    assert res["available"] is True
    assert "signals" in res
    assert "ela_anomaly_score" in res["signals"]
    assert "reasons" in res
    assert len(res["reasons"]) > 0
    assert "limitations" in res
