"""Public Integration API for Person 3 (Sanjay).

Provides stable, standardized entry points for Person 1 (Rithvik) to integrate
image forensics and CNN visual prediction into the ensemble pipeline.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from .forensics.forensic_analysis import analyze_image as _analyze_image
from .model.cnn_model import predict as cnn_predict
from .utils.device import get_device_info

DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "models" / "resnet18_baseline_best.pt"


def predict(image, weights_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the trained ResNet-18 and return an integration-stable response.

    A model output is returned only when checkpoint-backed inference succeeds.
    ``weights_path`` may select another compatible checkpoint; passing a missing
    path returns ``status='unavailable'`` rather than a fabricated prediction.
    """
    target_weights = Path(weights_path) if weights_path is not None else (
        DEFAULT_WEIGHTS_PATH if DEFAULT_WEIGHTS_PATH.exists() else None
    )
    if target_weights is None or not target_weights.exists():
        return {
            "status": "unavailable", "class": None, "label": None, "probability": None,
            "model": "ResNet18", "available": False,
            "reason": "Model checkpoint not available.",
            "explanation": "No CNN prediction was produced because no trained checkpoint could be loaded.",
        }
    result = cnn_predict(image, weights_path=target_weights)
    if not result.get("available"):
        return {
            "status": "error", "class": None, "label": None, "probability": None,
            "model": "ResNet18", "available": False,
            "reason": result.get("reasons", ["CNN inference failed."])[0],
            "explanation": "No CNN prediction was produced because inference failed for this input.",
        }
    explanation = result.get("reasons", ["Model prediction completed."])[0]
    return {
        "status": "success", "class": result["label"], "label": result["label"],
        "probability": result["probability"], "probabilities": result.get("probabilities", {}),
        "model": "ResNet18", "model_version": result.get("model_version"), "available": True,
        "explanation": explanation,
    }


def analyze_image(image, ela_output_dir: Optional[str] = None, quality: int = 90) -> Dict[str, Any]:
    """Return separate ELA and metadata evidence without a forensic score."""
    return _analyze_image(image, ela_output_dir=ela_output_dir, quality=quality)


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
            "gradcam": "ready (ResNet18 Grad-CAM)"
        },
        "device": device_info,
        "academic_stage": "Phase 7 integration-ready baseline"
    }


__all__ = ["analyze_image", "predict", "get_person3_status"]
