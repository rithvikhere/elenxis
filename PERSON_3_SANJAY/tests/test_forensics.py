"""Tests for evidence-only ELA, metadata, and wrapper behavior."""

from pathlib import Path

from PIL import Image

from PERSON_3_SANJAY.src.forensics.ela import analyze_ela, compute_ela
from PERSON_3_SANJAY.src.forensics.forensic_analysis import analyze_image
from PERSON_3_SANJAY.src.forensics.metadata import inspect_metadata


def test_ela_png_and_output(tmp_path):
    image = Image.new("RGB", (80, 60), "white")
    path = tmp_path / "sample.png"
    image.save(path)
    result = analyze_ela(path, output_dir=tmp_path)
    assert result["status"] == "available"
    assert Path(result["output_visualization_path"]).exists()
    assert "mean_absolute_difference" in result["summary_statistics"]
    ela, stats = compute_ela(path)
    assert ela.size == image.size and stats["recompression_quality"] == 90


def test_ela_invalid_and_corrupted_input(tmp_path):
    corrupted = tmp_path / "bad.png"
    corrupted.write_bytes(b"not an image")
    for candidate in (tmp_path / "missing.jpg", corrupted):
        result = analyze_ela(candidate)
        assert result["status"] == "error"
        assert result["output_visualization_path"] is None


def test_metadata_png_jpeg_missing_exif_and_corrupted(tmp_path):
    png = tmp_path / "sample.png"
    jpg = tmp_path / "sample.jpg"
    Image.new("RGB", (80, 60), "white").save(png)
    Image.new("RGB", (80, 60), "white").save(jpg, quality=85)
    for path, expected_format in ((png, "PNG"), (jpg, "JPEG")):
        result = inspect_metadata(path)
        assert result["status"] == "available"
        assert result["file_format"] == expected_format
        assert result["dimensions"] == {"width": 80, "height": 60}
        assert result["has_exif"] is False
    bad = tmp_path / "bad.jpg"
    bad.write_bytes(b"bad")
    assert inspect_metadata(bad)["status"] == "error"


def test_forensic_wrapper_has_raw_evidence_only(tmp_path):
    path = tmp_path / "sample.png"
    Image.new("RGB", (80, 60), "white").save(path)
    result = analyze_image(path, ela_output_dir=tmp_path)
    assert result["status"] == "available"
    assert result["ela"]["status"] == "available"
    assert result["metadata"]["status"] == "available"
    assert "score" not in result
