"""Evidence-only Error Level Analysis (ELA) utilities.

ELA compares an RGB image with a controlled JPEG recompression. It is a visual
indicator, not a fraud score or proof of manipulation.
"""

import io
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image

from ..utils.image_io import load_image


def compute_ela(image_input: Any, quality: int = 90, scale_factor: float = 15.0) -> Tuple[Image.Image, Dict[str, Any]]:
    """Create an amplified ELA image and descriptive pixel-difference statistics."""
    if not 1 <= quality <= 100:
        raise ValueError("JPEG recompression quality must be between 1 and 100.")
    if scale_factor <= 0:
        raise ValueError("ELA scale_factor must be greater than zero.")
    original = load_image(image_input)
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    with Image.open(buffer) as saved_image:
        resaved = saved_image.convert("RGB")
    difference = np.abs(np.asarray(original, dtype=np.float32) - np.asarray(resaved, dtype=np.float32))
    ela_image = Image.fromarray(np.clip(difference * scale_factor, 0, 255).astype(np.uint8), mode="RGB")
    return ela_image, {
        "mean_absolute_difference": round(float(np.mean(difference)), 4),
        "max_absolute_difference": round(float(np.max(difference)), 4),
        "std_absolute_difference": round(float(np.std(difference)), 4),
        "p95_absolute_difference": round(float(np.percentile(difference, 95)), 4),
        "recompression_quality": quality,
        "visualization_scale_factor": scale_factor,
    }


def analyze_ela(image_input: Any, quality: int = 90, output_dir: Optional[Union[str, Path]] = None,
                scale_factor: float = 15.0) -> Dict[str, Any]:
    """Return ELA evidence; processing failures are returned as structured errors."""
    input_path = str(image_input) if isinstance(image_input, (str, Path)) else None
    try:
        ela_image, statistics = compute_ela(image_input, quality, scale_factor)
        visualization_path = None
        warnings = [
            "ELA shows differences caused by JPEG recompression; it is not proof of manipulation.",
            "Resizing, prior recompression, screenshots, and normal processing can create ELA differences.",
        ]
        if output_dir is not None:
            destination = Path(output_dir)
            destination.mkdir(parents=True, exist_ok=True)
            name = Path(input_path).stem if input_path else "in_memory_image"
            path = destination / f"{name}_ela_q{quality}.png"
            ela_image.save(path, format="PNG")
            visualization_path = str(path)
        else:
            warnings.append("The ELA visualisation was generated in memory but not written to disk.")
        return {
            "status": "available", "input_path": input_path,
            "recompression_quality": quality, "output_visualization_path": visualization_path,
            "summary_statistics": statistics, "warnings": warnings,
            "explanation": "The visualisation amplifies pixel differences between the input and a controlled JPEG recompression.",
        }
    except Exception as error:
        return {
            "status": "error", "input_path": input_path, "recompression_quality": quality,
            "output_visualization_path": None, "summary_statistics": {},
            "warnings": ["No ELA evidence was produced because the image could not be processed."],
            "explanation": "ELA is unavailable for this input.", "error": str(error),
        }
