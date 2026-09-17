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
    assert cnn_res["status"] == "success"
    assert cnn_res["class"] in ("original", "modified")
    assert cnn_res["available"] is True
    assert cnn_res["label"] in ("original", "modified")
    assert "probability" in cnn_res
    assert "explanation" in cnn_res


def test_predict_missing_checkpoint_is_unavailable():
    result = predict(Image.new("RGB", (20, 20)), weights_path="missing_checkpoint.pt")
    assert result["status"] == "unavailable"
    assert result["class"] is None
    assert result["available"] is False
