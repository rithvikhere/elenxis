"""Public Integration API for Person 3 (Sanjay).

Provides stable, standardized entry points for Person 1 (Rithvik) to integrate
image forensics and CNN visual prediction into the ensemble pipeline.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from .forensics.forensics_engine import analyze_image
from .model.cnn_model import predict as cnn_predict
from .utils.device import get_device_info

DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "models" / "resnet18_baseline_best.pt"


def predict(image, weights_path: Optional[str] = None) -> Dict[str, Any]:
    """Execute CNN prediction using best trained weights if available."""
    target_weights = weights_path or (DEFAULT_WEIGHTS_PATH if DEFAULT_WEIGHTS_PATH.exists() else None)
    return cnn_predict(image, weights_path=target_weights)


def get_person3_status() -> Dict[str, Any]:
    """Return runtime capability and module readiness status for Person 3."""
    device_info = get_device_info()
    has_weights = DEFAULT_WEIGHTS_PATH.exists()
    return {
        "person": "Person 3 (Sanjay)",
        "modules": {
            "error_level_analysis": "ready",
            "metadata_inspection": "ready",
            "forensics_engine": "ready",
            "cnn_architecture": "ready",
            "cnn_weights": "trained_baseline (ResNet18)" if has_weights else "uninitialized",
            "gradcam": "planned (Phase 3/4)"
        },
        "device": device_info,
        "academic_stage": "30% Review (Baseline Model Ready)"
    }


__all__ = ["analyze_image", "predict", "get_person3_status"]
