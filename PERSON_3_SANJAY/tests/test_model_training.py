"""Unit tests for ResNet-18 model architecture, checkpoint saving/loading, and CPU execution."""

from pathlib import Path
import pytest
import torch
from PIL import Image

from PERSON_3_SANJAY.src.model.model import (
    create_resnet18_model,
    save_model_checkpoint,
    load_model_checkpoint,
    CLASS_MAP
)
from PERSON_3_SANJAY.src.model.cnn_model import predict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "PERSON_3_SANJAY" / "models"


def test_resnet18_initialization_and_classes():
    """Verify ResNet-18 model structure and class mapping."""
    model = create_resnet18_model(pretrained=False, num_classes=2)
    assert model.num_classes == 2
    assert CLASS_MAP[0] == "original"
    assert CLASS_MAP[1] == "modified"
    
    counts = model.get_trainable_param_counts()
    assert counts["total_parameters"] > 11_000_000
    assert counts["trainable_parameters"] == counts["total_parameters"]


def test_resnet18_forward_pass_tensor_shapes():
    """Verify output logit shapes for batch execution."""
    model = create_resnet18_model(pretrained=False, num_classes=2)
    model.eval()
    
    dummy_batch = torch.randn(4, 3, 224, 224)
    with torch.no_grad():
        logits = model(dummy_batch)
        
    assert logits.shape == (4, 2)
    assert not torch.isnan(logits).any()


def test_checkpoint_save_and_load(tmp_path):
    """Verify model state saving and restoration."""
    model = create_resnet18_model(pretrained=False, num_classes=2)
    ckpt_file = tmp_path / "test_checkpoint.pt"
    
    cfg = {"seed": 42, "lr": 1e-4}
    metrics = {"accuracy": 0.85}
    
    saved_path = save_model_checkpoint(model, ckpt_file, config=cfg, metrics=metrics)
    assert saved_path.exists()
    
    loaded_model, ckpt = load_model_checkpoint(ckpt_file)
    assert loaded_model.num_classes == 2
    assert ckpt["config"]["seed"] == 42
    assert ckpt["metrics"]["accuracy"] == 0.85


def test_cpu_inference_with_trained_weights():
    """Verify inference execution with trained checkpoint weights on CPU."""
    best_ckpt = MODELS_DIR / "resnet18_baseline_best.pt"
    if not best_ckpt.exists():
        pytest.skip("Trained checkpoint not yet generated.")
        
    dummy_img = Image.new("RGB", (224, 224), color=(240, 240, 240))
    result = predict(dummy_img, weights_path=best_ckpt)
    
    assert result["available"] is True
    assert result["label"] in ("original", "modified")
    assert 0.0 <= result["probability"] <= 1.0
    assert "probabilities" in result
    assert "reasons" in result
    assert len(result["reasons"]) > 0
