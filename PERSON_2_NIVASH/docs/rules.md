# Rule-Based Consistency Validation Engine
**Person 2 — UPI Transaction Fraud Forensics Platform**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai*

---

## 1. Architectural Role & Overview

The **Rule-Based Consistency Engine (Subsystem B)** acts as the deterministic semantic verification layer in the multi-modal forensics pipeline. While the CNN classifier (Subsystem D) evaluates visual texture and Error Level Analysis (Subsystem C) evaluates JPEG compression artifacts, the Rule Engine evaluates **logical, syntactic, and temporal invariants** of payment transactions.

### Core Objectives:
1. **Deterministic Verification**: Fast, transparent, rule-based verification with zero neural network opacity.
2. **Instant Tamper Detection**: Flags obvious semantic blunders committed by fraudsters (future timestamps, non-12-digit UTRs, missing critical fields).
3. **Explainability Driver (Subsystem F)**: Directly outputs structured violation explanations (e.g. `"Transaction date 2029-12-28 is in the FUTURE"`) for merchant-facing dashboards.

---

## 2. Complete Catalogue of Consistency Rules

The engine implements 11 atomic validators (`src/rules/validators.py`):

| Rule ID | Name | Category | Weight | Logic & Pass Criterion | Forensic Indicator |
|:---|:---|:---:|:---:|:---|:---|
| **`RULE-01`** | `amount_present` | Presence | $0.15$ | Amount field non-empty and detected by parser. | Blanks out amount or extreme cropping. |
| **`RULE-02`** | `amount_positive` | Semantic | $0.10$ | Amount value is positive numeric ($> ₹0.00$). | Negative or non-numeric placeholder. |
| **`RULE-03`** | `amount_range` | Range | $0.05$ | Amount within plausible daily UPI limits ($₹1.00$ to $₹1,00,000.00$). | Outlier amounts or test artifacts. |
| **`RULE-04`** | `date_present` | Presence | $0.15$ | Date string extractable. | Blanked date field. |
| **`RULE-05`** | `date_not_future` | Temporal | $0.25$ | $T_{\text{txn}} \le T_{\text{ref}}$ (Date $\le$ reference date). | **Critical Tamper Signal**: Fraudsters carelessly reusing old templates with future fake dates. |
| **`RULE-06`** | `date_not_too_old` | Temporal | $0.05$ | $T_{\text{txn}} \ge T_{\text{ref}} - 5\text{ years}$. | Stale screenshot reused from distant past. |
| **`RULE-07`** | `utr_present` | Presence | $0.10$ | UTR / Reference ID non-empty. | Missing reference number. |
| **`RULE-08`** | `utr_numeric` | Syntactic | $0.15$ | UTR contains exclusively digits ($0–9$). | **Tamper Signal**: Non-numeric prefixes like `UTR2719583` or `UTRS614226`. |
| **`RULE-09`** | `utr_length` | Syntactic | $0.10$ | UTR length is exactly 12 digits (NPCI standard). | Truncated 7–10 digit modified UTRs. |
| **`RULE-10`** | `status_present` | Integrity | $0.05$ | Status matches legitimate success keyword (`Paid Successfully`, `SUCCESS`, `Payment Completed`). | Status line blanked or edited. |
| **`RULE-11`** | `recipient_present` | Integrity | $0.05$ | Recipient / Payee entity extracted. | Blanked or unreadable recipient. |

---

## 3. Suspicion Scoring Formulation & Decision Logic

### Mathematical Formulation
The overall suspicion score $S \in [0.0, 1.0]$ is computed as a weighted linear combination of failed rule checks:

$$S = \min\left(1.0, \sum_{i \in \text{Fails}} w_i + 0.4 \times \sum_{j \in \text{Warnings}} w_j\right)$$

where:
- $w_i$ is the configured severity weight for rule $i$.
- Hard failures (`FAIL`) contribute full weight $w_i$.
- Soft warnings (`WARN` / `SKIP`) contribute discounted weight $0.4 \times w_j$.

### Tri-State Verdict Mapping
- **`LIKELY_LEGITIMATE`** ($S < 0.25$): All critical consistency rules satisfied. Minimal or zero discrepancies.
- **`SUSPICIOUS`** ($S \ge 0.25$): At least one major rule (e.g. future date or non-numeric UTR) or multiple minor rules violated.
- **`UNREADABLE`**: OCR extraction yielded empty fields or image could not be parsed. Pushes toward conservative human review.

---

## 4. API Interface for Person 1 (Streamlit UI & Ensemble)

### Function: `validate_transaction()`
```python
from src.rules import validate_transaction

rule_result = validate_transaction(ocr_result)
```

### Output JSON Schema:
```json
{
  "verdict": "SUSPICIOUS",
  "suspicion_score": 0.55,
  "violations": [
    "RULE-05 FAIL: Transaction date 2029-12-28 is in the FUTURE (reference: 2026-09-17). Strong tamper indicator.",
    "RULE-08 FAIL: UTR 'UTR8078673' contains non-numeric characters. Standard UPI UTRs are 12-digit numeric strings."
  ],
  "warnings": [],
  "passed_checks": [
    "RULE-01 PASS: Amount field present.",
    "RULE-02 PASS: Amount ₹450.00 is positive.",
    "RULE-03 PASS: Amount ₹450.00 is within plausible UPI range."
  ],
  "explanation": "Receipt flagged as SUSPICIOUS (score=0.55/1.00). 2 violation(s) detected. Primary concern: RULE-05 FAIL: Transaction date 2029-12-28 is in the FUTURE (reference: 2026-09-17). Strong tamper indicator.",
  "fields_used": {
    "amount": "₹450.00",
    "amount_value": 450.0,
    "date": "28 Dec 2029",
    "date_iso": "2029-12-28",
    "transaction_id": "UTR8078673"
  }
}
```

---

## 5. Empirical Benchmark Results across Full 300-Image Dataset

The Rule Engine was benchmarked across all 300 images in the dataset (60 originals, 46 transformed, 194 fake):

```
================================================================================
RULE-BASED VALIDATION ENGINE BENCHMARK REPORT — PERSON 2
================================================================================
Total Receipts Evaluated : 300 images (60 original, 46 transformed, 194 fake)
Reference System Date    : 17 Sep 2026
--------------------------------------------------------------------------------
[CLASSIFICATION PERFORMANCE MATRIX]
  • True Positives  (TP) :  89  (Tampered receipts correctly flagged)
  • True Negatives  (TN) :  61  (Legitimate receipts correctly cleared)
  • False Positives (FP) :  45  (Legitimate receipts flagged as suspicious)
  • False Negatives (FN) : 105  (Tampered receipts missed by heuristic rules)
--------------------------------------------------------------------------------
  • Accuracy             :  50.00%
  • Precision            :  66.42%
  • Recall (Sensitivity) :  45.88%
  • F1-Score             :  54.27%
--------------------------------------------------------------------------------
[PER-EDIT-TYPE DETECTION BREAKDOWN]
Edit Type                | Total  | Flagged  | Detection Rate
-------------------------|--------|----------|---------------
date_change              |     29 |       18 |          62.1%
text_remove              |     25 |       14 |          56.0%
amount_change            |     24 |       12 |          50.0%
transaction_id_change    |     28 |       13 |          46.4%
crop                     |     30 |       12 |          40.0%
font_alter               |     31 |       11 |          35.5%
text_insert              |     27 |        9 |          33.3%
--------------------------------------------------------------------------------
```

### Forensic Analysis & Ensemble Justification:
- Explicit syntactic and temporal alterations (`date_change`, `text_remove`, `amount_change`) trigger high detection rates via explicit rule invariants.
- Subtle spatial and typographic anomalies (`font_alter`, `crop`, `text_insert`) do not violate syntactic constraints and are naturally handled by **Subsystem C (Image Forensics / ELA)** and **Subsystem D (CNN Classifier)**, demonstrating why multi-modal ensemble cooperation is essential.

---

## 6. Academic & Forensic Scope

> **Important Boundary Condition**: The Rule Engine evaluates structural, temporal, and semantic consistency within the document. It does **not** make live API requests to banking backends or NPCI switch networks. In a forensic triage setting, a rule failure constitutes strong evidence of document tampering rather than banking ledger invalidation.
