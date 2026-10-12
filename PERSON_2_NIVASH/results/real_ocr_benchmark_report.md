# Real UPI Screenshot Benchmark Report
**Subsystem:** Person 2 (Nivash Kumaar S) — Dataset, OCR Pipeline & Rule Engine  
**Dataset Size:** 18 Real Screenshots (Google Pay & PhonePe)  
**Date:** October 2026  
**Source Metrics:** `results/metrics/real_ocr_benchmark.json`

---

## 1. Overall Extraction Accuracy

| Field | Accuracy (%) | Matched / Total |
|---|---|---|
| **Amount (₹)** | **100.0%** | 18 / 18 |
| **Date & Timestamp** | **100.0%** | 18 / 18 |
| **12-Digit UTR** | **100.0%** | 18 / 18 |
| **Recipient (Payee)** | **100.0%** | 18 / 18 |
| **Transaction Status** | **83.33%** | 15 / 18 |

- **Average OCR Confidence:** `83.5%`
- **Average Extraction Latency:** `585.3 ms` per receipt

---

## 2. App-Family Breakdown

| Metric | Google Pay (10 receipts) | PhonePe (8 receipts) |
|---|---|---|
| **Amount Accuracy** | 100.0% | 100.0% |
| **Date Accuracy** | 100.0% | 100.0% |
| **UTR Accuracy** | 100.0% | 100.0% |
| **Recipient Accuracy** | 100.0% | 100.0% |

---

## 3. Viewport & Scrolling Analysis
- **Full Scrolled Screenshots:** 15 images.
- **Unscrolled Viewports:** 3 images (e.g. PhonePe transaction details where top date header was scrolled out of view).
- **Date Recovery via App Txn ID:** Handled cleanly using PhonePe timestamp prefixes (`T26...`).

---

## 4. Rule-Based Forensic Validation (RULE-01 to RULE-11)
- **Likely Legitimate Rate:** 100.0% (18 / 18)
- **Suspicious Flags:** 0
- **Unreadable Fallbacks:** 0
- **False Positive Violations:** 0 (all genuine receipts correctly pass amount, date, 12-digit numeric UTR, and recognized payment status).

---

*Generated automatically by `PERSON_2_NIVASH/scripts/evaluate_real_ocr.py`. All figures are traceable to `results/metrics/real_ocr_benchmark.json`.*
