"""Public Integration API for Person 3 (Sanjay).

Provides stable, standardized entry points for Person 1 (Rithvik) to integrate
image forensics and CNN visual prediction into the ensemble pipeline.
"""

from typing import Dict, Any
from .forensics.forensics_engine import analyze_image
from .model.cnn_model import predict
from .utils.device import get_device_info


def get_person3_status() -> Dict[str, Any]:
    """Return runtime capability and module readiness status for Person 3."""
    device_info = get_device_info()
    return {
        "person": "Person 3 (Sanjay)",
        "modules": {
            "error_level_analysis": "ready",
            "metadata_inspection": "ready",
            "forensics_engine": "ready",
            "cnn_architecture": "ready",
            "cnn_weights": "uninitialized (Phase 1)",
            "gradcam": "planned (Phase 3)"
        },
        "device": device_info,
        "academic_stage": "30% Review (Foundations)"
    }


__all__ = ["analyze_image", "predict", "get_person3_status"]
