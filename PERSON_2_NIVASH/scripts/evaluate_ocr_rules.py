#!/usr/bin/env python3
"""
Empirical Evaluation Script — OCR + Rule Engine.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Measures actual extraction accuracy and tamper-detection performance
against the ground-truth metadata.csv for the full 60-image dataset
and separately for the 12-image held-out test split.

Run from PERSON_2_NIVASH/:
    python scripts/evaluate_ocr_rules.py
"""

import csv
import os
import sys
import re
from pathlib import Path

# Allow imports from this folder
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr import extract_transaction_fields
from src.rules import validate_transaction


DATA_DIR   = Path(__file__).parent.parent / "data"
IMG_DIR    = DATA_DIR / "raw"
META_PATH  = DATA_DIR / "metadata.csv"


def normalise_amount(s: str) -> str:
    """Strip currency symbol and commas for comparison."""
    if not s:
        return ""
    return re.sub(r'[₹,\s]', '', s).strip()


def normalise_utr(s: str) -> str:
    if not s:
        return ""
    return s.strip().upper()


def load_metadata() -> list[dict]:
    with open(META_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_evaluation(rows: list[dict], split_label: str) -> dict:
    total = len(rows)
    amt_correct = date_correct = utr_correct = 0
    extracted = 0

    tp = fp = tn = fn = 0  # tamper detection

    for row in rows:
        img_path = IMG_DIR / row["filename"]
        ocr = extract_transaction_fields(str(img_path))
        verdict = validate_transaction(ocr)
        f = ocr["fields"]

        is_tampered = row["label"] == "synthetic_fake"
        predicted_suspicious = verdict["verdict"] == "SUSPICIOUS"

        # Confusion matrix
        if is_tampered and predicted_suspicious:
            tp += 1
        elif not is_tampered and not predicted_suspicious:
            tn += 1
        elif not is_tampered and predicted_suspicious:
            fp += 1
        else:
            fn += 1

        if ocr["success"]:
            extracted += 1

        # Amount accuracy
        gt_amt = normalise_amount(row.get("ground_truth_amount", ""))
        ex_amt = normalise_amount(f.get("amount", "") or "")
        if gt_amt and ex_amt and gt_amt == ex_amt:
            amt_correct += 1

        # Date accuracy
        gt_date = row.get("ground_truth_date", "").strip()
        ex_date = (f.get("date", "") or "").strip()
        if gt_date and ex_date and gt_date.lower() == ex_date.lower():
            date_correct += 1

        # UTR accuracy
        gt_utr = normalise_utr(row.get("ground_truth_utr", ""))
        ex_utr = normalise_utr(f.get("transaction_id", "") or "")
        if gt_utr and ex_utr and gt_utr == ex_utr:
            utr_correct += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    accuracy    = (tp + tn) / total if total else 0.0

    return {
        "split": split_label,
        "total": total,
        "extraction_rate": extracted / total if total else 0,
        "amount_accuracy": amt_correct / total if total else 0,
        "date_accuracy": date_correct / total if total else 0,
        "utr_accuracy": utr_correct / total if total else 0,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "specificity": specificity,
        "accuracy": accuracy,
    }


def print_table(metrics: dict) -> None:
    s = metrics["split"]
    n = metrics["total"]
    print(f"\n{'='*60}")
    print(f"  Split: {s}  ({n} images)")
    print(f"{'='*60}")
    print(f"  OCR Extraction Rate  : {metrics['extraction_rate']*100:.1f}%")
    print(f"  Amount Accuracy      : {metrics['amount_accuracy']*100:.1f}%")
    print(f"  Date Accuracy        : {metrics['date_accuracy']*100:.1f}%")
    print(f"  UTR Accuracy         : {metrics['utr_accuracy']*100:.1f}%")
    print()
    print(f"  Tamper Detection (Rule Engine):")
    print(f"    TP={metrics['tp']}  TN={metrics['tn']}  FP={metrics['fp']}  FN={metrics['fn']}")
    print(f"    Precision   : {metrics['precision']*100:.1f}%")
    print(f"    Recall      : {metrics['recall']*100:.1f}%")
    print(f"    F1-Score    : {metrics['f1_score']*100:.1f}%")
    print(f"    Specificity : {metrics['specificity']*100:.1f}%")
    print(f"    Accuracy    : {metrics['accuracy']*100:.1f}%")
    print(f"{'='*60}")


def main() -> None:
    print("\nUPI Transaction Forensics — Person 2 Evaluation")
    print("OCR Pipeline + Rule-Based Tamper Detection")
    print("-" * 60)

    rows = load_metadata()
    print(f"Loaded {len(rows)} records from metadata.csv")

    # Full dataset
    full_metrics = run_evaluation(rows, "ALL (60 images)")
    print_table(full_metrics)

    # Per-split
    for split in ("train", "val", "test"):
        split_rows = [r for r in rows if r["split"] == split]
        m = run_evaluation(split_rows, split.upper())
        print_table(m)

    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()
