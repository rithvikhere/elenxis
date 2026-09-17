"""Model evaluation and error analysis tools for UPI Fraud Forensics."""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)


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
