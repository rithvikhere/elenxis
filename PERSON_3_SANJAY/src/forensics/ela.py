"""Error Level Analysis (ELA) implementation for payment screenshot forensics.

Error Level Analysis works by re-saving the candidate image at a known JPEG quality
level (e.g. 90-95%) and computing the absolute pixel-wise difference between the
original and the resaved image.

Because lossy compression compresses unmodified regions at a uniform rate,
digitally inserted text, spliced boxes, or modified amount numbers often present
noticeably higher or lower error levels.
"""

import io
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageEnhance

from ..utils.image_io import load_image


def compute_ela(
    image_input,
    quality: int = 90,
    scale_factor: float = 15.0
) -> Tuple[Image.Image, Dict[str, Any]]:
    """Compute the Error Level Analysis (ELA) map and statistical anomaly metrics.

    Args:
        image_input: Path, bytes, PIL Image, or numpy array.
        quality: JPEG re-compression quality factor (1-100, default 90).
        scale_factor: Multiplier to amplify error visualization.

    Returns:
        Tuple of (ela_image, metrics_dict)
    """
    original = load_image(image_input)
    
    # Save image to in-memory buffer with lossy JPEG compression
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer).convert("RGB")
    
    # Calculate pixel-level difference
    orig_arr = np.array(original, dtype=np.float32)
    resaved_arr = np.array(resaved, dtype=np.float32)
    
    diff = np.abs(orig_arr - resaved_arr)
    
    # Compute statistical metrics across the canvas
    mean_error = float(np.mean(diff))
    max_error = float(np.max(diff))
    std_error = float(np.std(diff))
    
    # 95th percentile deviation indicates localized spikes
    p95_error = float(np.percentile(diff, 95))
    
    # Localized high-frequency variance indicator (0.0 to 1.0)
    # A high anomaly score suggests localized compression inconsistencies
    anomaly_score = float(np.clip((p95_error - mean_error) / 50.0, 0.0, 1.0))
    
    # Create amplified visual ELA representation
    ela_amplified = np.clip(diff * scale_factor, 0, 255).astype(np.uint8)
    ela_image = Image.fromarray(ela_amplified)
    
    metrics = {
        "mean_error": round(mean_error, 4),
        "max_error": round(max_error, 4),
        "std_error": round(std_error, 4),
        "p95_error": round(p95_error, 4),
        "anomaly_score": round(anomaly_score, 4),
        "resave_quality": quality,
        "scale_factor": scale_factor,
        "indicators": []
    }
    
    # Diagnostic indicators (cautious scientific phrasing)
    if anomaly_score > 0.65:
        metrics["indicators"].append(
            "High localized compression variance detected in ELA map (warrants visual inspection)."
        )
    elif anomaly_score > 0.35:
        metrics["indicators"].append(
            "Moderate compression variance observed across canvas."
        )
    else:
        metrics["indicators"].append(
            "Relatively uniform error level distribution across image canvas."
        )
        
    return ela_image, metrics
