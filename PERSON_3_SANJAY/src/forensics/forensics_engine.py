"""Forensics Engine combining Error Level Analysis and Metadata Inspection.

Exposes the standardized integration contract:
    def analyze_image(image) -> dict
"""

from typing import Dict, Any
from PIL import Image

from .ela import compute_ela
from .metadata import inspect_metadata
from ..utils.image_io import load_image


def analyze_image(image_input) -> Dict[str, Any]:
    """Analyze image using forensic techniques (ELA, EXIF, compression artifacts).

    Conforms to the standardized team integration contract.

    Args:
        image_input: File path, bytes, PIL Image, or numpy array.

    Returns:
        Dict containing forensic signals, metrics, reasons, and limitations.
    """
    try:
        pil_img = load_image(image_input)
    except Exception as err:
        return {
            "status": "error",
            "available": False,
            "signals": {},
            "indicators": [],
            "reasons": [f"Failed to load image for forensic analysis: {str(err)}"],
            "limitations": ["Invalid image input format."]
        }
        
    try:
        # 1. Compute Error Level Analysis
        ela_img, ela_metrics = compute_ela(pil_img)
        
        # 2. Inspect Metadata & EXIF
        meta_info = inspect_metadata(pil_img)
        
        # 3. Formulate unified forensic indicators and reasons
        indicators = []
        indicators.extend(ela_metrics.get("indicators", []))
        indicators.extend(meta_info.get("indicators", []))
        
        limitations = [
            "Forensic signals provide visual and structural indicators, not absolute proof of fraud.",
            "Legitimate mobile screenshots may show compression artifacts due to social media sharing."
        ]
        limitations.extend(meta_info.get("limitations", []))
        
        reasons = []
        if meta_info.get("editing_software_detected"):
            reasons.append("Image header contains editing application signature.")
        if ela_metrics.get("anomaly_score", 0.0) > 0.60:
            reasons.append("Localized error level analysis indicates high compression rate discrepancy.")
        if not reasons:
            reasons.append("No definitive image-level tampering anomalies flagged by current baseline checks.")
            
        return {
            "status": "available",
            "available": True,
            "signals": {
                "ela_anomaly_score": ela_metrics.get("anomaly_score"),
                "ela_mean_error": ela_metrics.get("mean_error"),
                "ela_max_error": ela_metrics.get("max_error"),
                "ela_p95_error": ela_metrics.get("p95_error"),
                "metadata_has_exif": meta_info.get("has_exif"),
                "metadata_editing_software_detected": meta_info.get("editing_software_detected"),
                "software_signature": meta_info.get("software")
            },
            "ela_metrics": ela_metrics,
            "metadata": {
                "has_exif": meta_info.get("has_exif"),
                "software": meta_info.get("software"),
                "detected_software_tags": meta_info.get("detected_software_tags"),
                "datetime": meta_info.get("datetime")
            },
            "indicators": indicators,
            "reasons": reasons,
            "limitations": limitations
        }
    except Exception as err:
        return {
            "status": "error",
            "available": False,
            "signals": {},
            "indicators": [],
            "reasons": [f"Forensics analysis error: {str(err)}"],
            "limitations": ["Encountered unexpected processing failure during forensic computation."]
        }
