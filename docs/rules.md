# Rule-Based Validation Engine Documentation
**Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP)**

---

## 1. Scope & System Role

The Rule-Based Validation Engine (`src/rules/`) provides deterministic, explainable heuristic verification on extracted receipt metadata. 

While computer vision models (Person 3) analyze pixel-level tampering (ELA, noise consistency, splicing artifacts), the Rule Engine catches **semantic, logical, and structural anomalies** that a CNN cannot detect through visual features alone (e.g., a cleanly photoshopped receipt with a future date or invalid UTR character length).

```
+--------------------------------+
| OCR Extractor Output Dict      |
+--------------------------------+
               |
               v
+--------------------------------+
| Rule Engine (11 Atomic Checks) |
| - Presence & Completeness      |
| - Format & Syntactic Validity  |
| - Logical / Temporal Rules     |
+--------------------------------+
               |
               v
+--------------------------------+
| Verdict & Risk Scoring Output  |
| - verdict: SUSPICIOUS /        |
|            LIKELY_LEGITIMATE   |
| - anomaly_score (0.0 to 1.0)   |
| - violations & explanations    |
+--------------------------------+
```

---

## 2. Rule Catalogue & Weight Formulation

Each rule is implemented as an atomic validator in `src/rules/validators.py` and evaluated within `src/rules/rule_engine.py`:

| Rule Code | Rule Name | Category | Severity / Weight | Validation Logic |
|:---|:---|:---|:---:|:---|
| `RULE_AMT_PRESENT` | Amount Field Missing | Required Field | **0.30** | Verifies presence of a valid monetary amount token. |
| `RULE_AMT_POSITIVE` | Non-Positive Amount | Logical | **0.35** | Flags zero, negative, or unparsable amount numbers. |
| `RULE_AMT_FORMAT` | Irregular Decimal Format | Format | **0.15** | Checks standard 2-decimal currency representation (`.00`). |
| `RULE_DATE_PRESENT` | Date Field Missing | Required Field | **0.25** | Verifies presence of transaction date. |
| `RULE_DATE_VALID` | Invalid Calendar Date | Format | **0.30** | Catches non-existent calendar dates (e.g., `31 Feb 2026`). |
| `RULE_DATE_FUTURE` | Future Transaction Date | Logical / Temporal | **0.40** | **Critical Check**: Flags transaction dates later than current/reference system date. |
| `RULE_UTR_PRESENT` | UTR / Txn ID Missing | Required Field | **0.25** | Verifies presence of UPI reference number. |
| `RULE_UTR_LEN` | Malformed UTR Length | Format | **0.35** | Flags UTR strings that deviate from the 12-digit standard (e.g., 9 or 15 digits). |
| `RULE_UTR_NUMERIC` | Non-Numeric UTR | Format | **0.20** | Flags unexpected alphanumeric characters in pure numeric UTRs. |
| `RULE_TIME_FORMAT` | Invalid Timestamp | Format | **0.15** | Validates 12-hour or 24-hour time formatting syntax. |
| `RULE_STATUS_OK` | Missing Success Indicator | Contextual | **0.20** | Confirms receipt contains status keywords (`Success`, `Completed`, `Paid`). |

### Anomaly Scoring Equation

$$\text{Anomaly Score} = \min\left(1.0, \sum_{i \in \text{Violations}} W_i \times \text{Confidence Factor}\right)$$

Where:
- $W_i$ is the pre-calibrated severity weight for rule $i$.
- $\text{Confidence Factor} = \frac{\text{Mean OCR Confidence}}{100.0}$ (downweights minor format warnings if OCR scan quality is degraded).
- **Verdict Threshold**:
  - $\text{Score} \ge 0.35 \implies \textbf{SUSPICIOUS}$
  - $\text{Score} < 0.35 \implies \textbf{LIKELY\_LEGITIMATE}$

---

## 3. Empirical Evaluation Performance

Evaluated against the ground-truth annotations across all 60 synthetic receipts via `scripts/evaluate_ocr_rules.py`:

| Dataset Split | Precision | Recall | F1-Score | Specificity | Accuracy |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Test Split (12 images)** | **100.0%** | **66.7%** | **80.0%** | **100.0%** | **75.0%** |
| **Validation Split (12 images)** | **100.0%** | **66.7%** | **80.0%** | **100.0%** | **75.0%** |
| **Train Split (36 images)** | **90.5%** | **70.4%** | **79.2%** | **77.8%** | **72.2%** |
| **Overall Dataset (60 images)** | **93.9%** | **68.9%** | **79.5%** | **86.7%** | **73.3%** |

### Review Defense Insight: Why Recall is ~68.9% by Design
The rule engine achieves **93.9%–100% Precision** because when a logical rule is triggered (e.g., a future date or a 9-digit UTR), it is a deterministic indicator of fraud. 

However, some fraudulent receipts in the dataset alter the amount without violating numerical format rules (e.g., changing `₹450.00` to `₹950.00`). Because the format of `₹950.00` remains valid, the Rule Engine correctly defers to Person 3's **CNN & ELA Visual Forensics model** to catch the pixel-level font and compression mismatch. This demonstrates the critical complementary nature of our multi-modal ensemble.

---

## 4. Integration Contract (Person 1 Ensemble Module)

The rule engine provides a standardized JSON-serializable output schema:

```python
from src.rules import validate_transaction

verdict_dict = validate_transaction(ocr_result)

# Output Schema:
# {
#     "verdict": "SUSPICIOUS",             # 'LIKELY_LEGITIMATE' | 'SUSPICIOUS'
#     "anomaly_score": 0.40,               # Float from 0.0 to 1.0
#     "passed_checks": [
#         "RULE_AMT_PRESENT",
#         "RULE_AMT_POSITIVE",
#         "RULE_UTR_PRESENT",
#         "RULE_UTR_LEN"
#     ],
#     "violations": [
#         "RULE_DATE_FUTURE"
#     ],
#     "warnings": [],
#     "explanations": [
#         "Transaction date 2026-11-20 is in the future relative to system date 2026-09-17"
#     ],
#     "summary": "1 rule violations detected (Anomaly Score: 0.40)"
# }
```

---

## 5. Review Viva / Defense Talking Points

1. **Question**: *"Can your system query the bank or NPCI UPI server directly to verify if the UTR exists?"*
   - **Answer**: *"No. In academic and forensic research, private banking APIs and NPCI transaction ledgers are proprietary and restricted. Our platform performs zero-trust client-side IDP (Intelligent Document Processing) and forensic signal analysis to detect structural, logical, and visual tampering on the document itself."*

2. **Question**: *"How does the rule engine handle different date formats across payment apps?"*
   - **Answer**: *"The OCR field parser normalizes both textual month formats (`12 Mar 2026`) and ISO/hyphenated formats (`2026-03-12`) into standard Python `datetime.date` objects before passing them to `check_date_validity()`, ensuring format independence across Paytm, PhonePe, and Google Pay styles."*
