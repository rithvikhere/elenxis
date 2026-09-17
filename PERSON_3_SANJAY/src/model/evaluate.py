"""Model evaluation and error analysis tools for UPI Fraud Forensics.

The held-out evaluator in this module is deliberately separate from training.  It
loads an already-selected checkpoint and reads only metadata rows assigned to the
``test`` split; it never fits or tunes a model.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)

from .dataset import LABEL_MAP, UPIScreenshotDataset
from .model import CLASS_MAP, load_model_checkpoint


def compute_classification_metrics(
    y_true: List[int],
    y_pred: List[int],
    y_probs: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Compute standard classification evaluation metrics.

    Args:
        y_true: Ground truth binary labels (0 = original, 1 = modified).
        y_pred: Predicted binary labels.
        y_probs: Predicted probability scores for positive class (modified).

    Returns:
        Dict with accuracy, precision, recall, f1, confusion matrix, and ROC-AUC.
    """
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    
    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))
    
    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "support": {
            "total_samples": len(y_true),
            "original_samples": int(np.sum(y_true_arr == 0)),
            "modified_samples": int(np.sum(y_true_arr == 1))
        }
    }
    
    if y_probs is not None:
        try:
            auc = float(roc_auc_score(y_true_arr, y_probs))
            metrics["roc_auc"] = round(auc, 4)
        except Exception:
            metrics["roc_auc"] = None
            
    return metrics


def perform_error_analysis(
    y_true: List[int],
    y_pred: List[int],
    sample_metadata: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Analyze False Positives and False Negatives to identify failure modes.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        sample_metadata: Optional list of dicts containing image paths, app types, notes.

    Returns:
        Structured error analysis breakdown.
    """
    fp_indices = [i for i, (t, p) in enumerate(zip(y_true, y_pred)) if t == 0 and p == 1]
    fn_indices = [i for i, (t, p) in enumerate(zip(y_true, y_pred)) if t == 1 and p == 0]
    
    error_report = {
        "false_positive_count": len(fp_indices),
        "false_negative_count": len(fn_indices),
        "false_positive_indices": fp_indices,
        "false_negative_indices": fn_indices,
        "hypothesized_failure_modes": {
            "false_positives": [
                "Heavy double-compression artifacts introduced during messaging app sharing.",
                "Non-standard device display scaling, dark mode variations, or OEM font rendering.",
                "High noise levels from photo-of-screen captures."
            ],
            "false_negatives": [
                "High-precision vector-level tampering where background compression was preserved.",
                "Single character / digit replacement with matched antialiasing."
            ]
        }
    }
    return error_report


def _label_name(label: int, class_map: Dict[Any, str]) -> str:
    """Return a stable label name when checkpoint keys are ints or strings."""
    return str(class_map.get(label, class_map.get(str(label), str(label))))


def _possible_error_reason(true_label: str, predicted_label: str, edit_type: str) -> str:
    """Return a deliberately tentative, non-causal error-analysis hypothesis."""
    if true_label == "original" and predicted_label == "modified":
        return (
            "Possible reason: this original image may contain layout or compression "
            "features resembling signals learned for the modified class; this is a hypothesis."
        )
    if edit_type == "amount_change":
        detail = "the localized amount edit may not remain distinctive after resizing"
    elif edit_type == "date_change":
        detail = "the localized date edit may be visually subtle relative to the full screenshot"
    elif edit_type == "transaction_id_change":
        detail = "the transaction-ID edit may be a small region relative to the full screenshot"
    else:
        detail = "the image may share visual characteristics with the opposite learned class"
    return f"Possible reason: {detail}; this is a hypothesis, not demonstrated causation."


def _validate_held_out_test_split(metadata_csv: Union[str, Path], dataset: UPIScreenshotDataset) -> pd.DataFrame:
    """Confirm that evaluation samples exactly match the isolated test partition."""
    metadata = pd.read_csv(metadata_csv).copy()
    if "split" not in metadata.columns:
        raise ValueError("Metadata must contain a split column for held-out evaluation.")
    if "group_id" not in metadata.columns:
        metadata["group_id"] = metadata.index // 4

    normalized_split = metadata["split"].astype(str).str.lower()
    expected_test = metadata[normalized_split == "test"].copy()
    non_test = metadata[normalized_split != "test"].copy()
    if expected_test.empty:
        raise ValueError("No test rows were found in metadata.")
    if len(dataset) != len(expected_test):
        raise ValueError("Dataset test count does not match metadata test count.")

    expected_filenames = set(expected_test["filename"].astype(str))
    actual_filenames = set(dataset.df["filename"].astype(str))
    if actual_filenames != expected_filenames:
        raise ValueError("Evaluation dataset does not exactly match the metadata test split.")
    overlap = set(expected_test["group_id"]).intersection(set(non_test["group_id"]))
    if overlap:
        raise ValueError(f"Group leakage detected between test and non-test splits: {sorted(overlap)}")
    return expected_test


def evaluate_checkpoint_on_test_set(
    checkpoint_path: Union[str, Path],
    metadata_csv: Union[str, Path],
    images_dir: Union[str, Path],
    batch_size: int = 8,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """Run one fixed checkpoint over the held-out test split and collect predictions.

    Class ``1`` (``modified``) is the positive class for precision, recall, F1,
    and TP/TN/FP/FN.  No training, threshold tuning, or metadata changes occur.
    """
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_dataset = UPIScreenshotDataset(metadata_csv, images_dir, split="test", is_training=False)
    expected_test = _validate_held_out_test_split(metadata_csv, test_dataset)
    model, checkpoint = load_model_checkpoint(checkpoint_path, device=device)
    model.eval()
    class_map = checkpoint.get("class_map", CLASS_MAP)

    loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    records: List[Dict[str, Any]] = []
    y_true: List[int] = []
    y_pred: List[int] = []
    y_probs: List[float] = []

    with torch.no_grad():
        for batch in loader:
            logits = model(batch["image"].to(device))
            probabilities = torch.softmax(logits, dim=1).cpu()
            predicted = torch.argmax(probabilities, dim=1).tolist()
            labels = batch["label"].tolist()
            for index, (actual, prediction) in enumerate(zip(labels, predicted)):
                true_name = _label_name(actual, class_map)
                predicted_name = _label_name(prediction, class_map)
                modified_probability = float(probabilities[index, 1].item())
                records.append({
                    "image_id": str(batch["image_id"][index]),
                    "filename": str(batch["filename"][index]),
                    "group_id": int(batch["group_id"][index]),
                    "true_label": true_name,
                    "predicted_label": predicted_name,
                    "modified_probability": round(modified_probability, 6),
                    "confidence": round(float(probabilities[index, prediction].item()), 6),
                    "correct": actual == prediction,
                    "edit_type": str(batch["edit_type"][index]),
                    "template_type": str(batch["template_type"][index]),
                })
                y_true.append(actual)
                y_pred.append(prediction)
                y_probs.append(modified_probability)

    if test_dataset.corrupted_files:
        raise ValueError(f"Evaluation stopped because test images could not be read: {test_dataset.corrupted_files}")
    if len(records) != len(expected_test):
        raise ValueError("Prediction count does not match the held-out test count.")

    metrics = compute_classification_metrics(y_true, y_pred, y_probs)
    errors = []
    for record in records:
        if not record["correct"]:
            error_type = "false_positive" if record["true_label"] == "original" else "false_negative"
            errors.append({
                "image": record["filename"],
                "true_label": record["true_label"],
                "prediction": record["predicted_label"],
                "error_type": error_type,
                "confidence": record["confidence"],
                "possible_reason": _possible_error_reason(
                    record["true_label"], record["predicted_label"], record["edit_type"]
                ),
            })
    return {
        "checkpoint": checkpoint,
        "metrics": metrics,
        "predictions": records,
        "errors": errors,
        "test_count": len(records),
        "test_groups": sorted(int(value) for value in expected_test["group_id"].unique()),
        "positive_class": _label_name(1, class_map),
    }


def write_evaluation_artifacts(evaluation: Dict[str, Any], output_dir: Union[str, Path]) -> Dict[str, Path]:
    """Write reproducible metrics, predictions, error analysis, and a matrix figure."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    metrics_path = destination / "metrics.json"
    predictions_path = destination / "predictions.csv"
    error_path = destination / "error_analysis.csv"
    matrix_path = destination / "confusion_matrix.png"
    report_path = destination / "evaluation_report.md"

    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump({
            "positive_class": evaluation["positive_class"],
            "test_count": evaluation["test_count"],
            "test_groups": evaluation["test_groups"],
            **evaluation["metrics"],
        }, handle, indent=2)
    pd.DataFrame(evaluation["predictions"]).to_csv(predictions_path, index=False)
    error_columns = ["image", "true_label", "prediction", "error_type", "confidence", "possible_reason"]
    pd.DataFrame(evaluation["errors"], columns=error_columns).to_csv(error_path, index=False)

    confusion = evaluation["metrics"]["confusion_matrix"]
    matrix = np.array([
        [confusion["true_negatives"], confusion["false_positives"]],
        [confusion["false_negatives"], confusion["true_positives"]],
    ])
    figure, axis = plt.subplots(figsize=(5, 4))
    image = axis.imshow(matrix, cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["original", "modified"],
             yticklabels=["original", "modified"], xlabel="Predicted label", ylabel="True label",
             title="Held-out Test Confusion Matrix")
    for row in range(2):
        for column in range(2):
            axis.text(column, row, str(matrix[row, column]), ha="center", va="center")
    figure.tight_layout()
    figure.savefig(matrix_path, dpi=200)
    plt.close(figure)

    error_rows = "\n".join(
        f"| {entry['image']} | {entry['true_label']} | {entry['prediction']} | {entry['error_type']} | {entry['confidence']:.4f} | {entry['possible_reason']} |"
        for entry in evaluation["errors"]
    ) or "| None | — | — | — | — | No errors were observed in this held-out evaluation. |"
    report_path.write_text(f"""# Held-out CNN Evaluation and Error Analysis

## Methodology

The fixed ResNet-18 checkpoint was evaluated once on the metadata rows explicitly assigned to the held-out `test` split. No training, threshold tuning, or label changes were performed. The evaluator verified that prediction count matched the test-set count and that test groups did not overlap non-test groups.

- Test samples: {evaluation['test_count']} (groups {', '.join(map(str, evaluation['test_groups']))})
- Positive class: `{evaluation['positive_class']}` (class index 1)
- Class distribution: {evaluation['metrics']['support']['original_samples']} original, {evaluation['metrics']['support']['modified_samples']} modified

## Metrics

| Accuracy | Precision | Recall | F1-score |
|---:|---:|---:|---:|
| {evaluation['metrics']['accuracy']:.4f} | {evaluation['metrics']['precision']:.4f} | {evaluation['metrics']['recall']:.4f} | {evaluation['metrics']['f1_score']:.4f} |

Precision, recall, and F1 treat `modified` as positive. Since this test split contains three times as many modified as original examples, accuracy alone can mask poor original-class performance.

## Confusion Matrix

| | Predicted original | Predicted modified |
|---|---:|---:|
| True original | {confusion['true_negatives']} (TN) | {confusion['false_positives']} (FP) |
| True modified | {confusion['false_negatives']} (FN) | {confusion['true_positives']} (TP) |

The corresponding figure is `confusion_matrix.png`.

## Error Analysis

| Image | True label | Prediction | Error type | Confidence | Possible reason |
|---|---|---|---|---:|---|
{error_rows}

The possible reasons are hypotheses based on the observed samples, not demonstrated causes. This CNN prediction and the associated image-forensics indicators are not proof that a financial transaction occurred or that fraud occurred.

## Limitations

This is a small (12-image), synthetic, imbalanced held-out test set covering three templates and three edit categories. Results should be interpreted as a baseline measurement rather than evidence of real-world generalization.
""", encoding="utf-8")
    return {
        "metrics": metrics_path,
        "predictions": predictions_path,
        "errors": error_path,
        "confusion_matrix": matrix_path,
        "report": report_path,
    }
