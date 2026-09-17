"""Unit tests for Person 3 public API surface."""

from PIL import Image
from PERSON_3_SANJAY.src.api import analyze_image, predict, get_person3_status


def test_api_surface():
    """Verify all top-level API functions operate and return expected dictionary schemas."""
    status = get_person3_status()
    assert status["person"] == "Person 3 (Sanjay)"
    assert "modules" in status
    assert "device" in status
    
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    
    forensics_res = analyze_image(img)
    assert forensics_res["status"] == "available"
    assert "ela" in forensics_res
    assert "metadata" in forensics_res
    
    cnn_res = predict(img)
    assert cnn_res["available"] is True
    assert cnn_res["label"] in ("original", "modified")
    assert "probability" in cnn_res
    assert "reasons" in cnn_res
