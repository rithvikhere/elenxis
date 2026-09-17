"""Unit tests for CNN architecture, metrics, and contracts."""

import pytest
import torch
from PIL import Image

from PERSON_3_SANJAY.src.model.cnn_model import UPIForensicsCNN, predict
from PERSON_3_SANJAY.src.model.evaluate import (
    compute_classification_metrics,
    perform_error_analysis
)


def test_cnn_architecture_shapes():
    """Verify forward pass output dimensions on custom baseline and ResNet18."""
    dummy_input = torch.randn(2, 3, 224, 224)
    
    # 1. Custom Baseline
    model_custom = UPIForensicsCNN(backbone="custom_baseline", num_classes=2)
    out_custom = model_custom(dummy_input)
    assert out_custom.shape == (2, 2)
    
    # 2. ResNet18 Backbone
    model_resnet = UPIForensicsCNN(backbone="resnet18", num_classes=2, pretrained=False)
    out_resnet = model_resnet(dummy_input)
    assert out_resnet.shape == (2, 2)


def test_predict_uninitialized_contract():
    """Verify predict returns the required uninitialized contract when weights are not present."""
    img = Image.new("RGB", (224, 224), color=(255, 255, 255))
    res = predict(img)
    
    assert res["label"] is None
    assert res["probability"] is None
    assert res["available"] is False
    assert "reasons" in res
    assert len(res["reasons"]) > 0


def test_compute_classification_metrics():
    """Verify classification metrics evaluation calculation."""
    y_true = [0, 0, 1, 1, 0, 1]
    y_pred = [0, 1, 1, 1, 0, 0]
    y_probs = [0.1, 0.7, 0.8, 0.9, 0.2, 0.4]
    
    metrics = compute_classification_metrics(y_true, y_pred, y_probs)
    
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["confusion_matrix"]["true_negatives"] == 2
    assert metrics["confusion_matrix"]["false_positives"] == 1
    assert metrics["confusion_matrix"]["false_negatives"] == 1
    assert metrics["confusion_matrix"]["true_positives"] == 2


def test_perform_error_analysis():
    """Verify error analysis breakdown."""
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 0, 1]
    
    report = perform_error_analysis(y_true, y_pred)
    assert report["false_positive_count"] == 1
    assert report["false_negative_count"] == 1
    assert "hypothesized_failure_modes" in report
