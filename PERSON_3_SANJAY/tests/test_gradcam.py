"""Regression tests for real ResNet-18 Grad-CAM outputs."""

from pathlib import Path

from PIL import Image

from PERSON_3_SANJAY.src.explainability.gradcam import TARGET_LAYER, generate_gradcam

ROOT = Path(__file__).resolve().parent.parent.parent
CHECKPOINT = ROOT / "PERSON_3_SANJAY" / "models" / "resnet18_baseline_best.pt"


def test_gradcam_generates_heatmap_and_overlay(tmp_path):
    if not CHECKPOINT.exists():
        return
    image = tmp_path / "input.png"
    Image.new("RGB", (128, 160), "white").save(image)
    result = generate_gradcam(image, CHECKPOINT, output_dir=tmp_path)
    assert result["status"] == "available"
    assert result["target_layer"] == TARGET_LAYER
    assert result["prediction"]["label"] in ("original", "modified")
    assert all(Path(path).exists() for path in result["output_paths"].values())


def test_gradcam_invalid_image_returns_error(tmp_path):
    bad = tmp_path / "bad.png"
    bad.write_bytes(b"not an image")
    result = generate_gradcam(bad, CHECKPOINT)
    assert result["status"] == "error"
