# Person 2 (Nivash) — Dataset, OCR & Rule Engine Subsystem
**UPI Transaction Fraud Forensics Platform (IDP)**
*Second-Year CSE (AI & ML) — Academic Project Review (30% Milestone)*

---

## 📌 Module Overview

Person 2 is responsible for the foundational data and heuristic intelligence layer of the platform:
1. **Synthetic Dataset Generation & Ground Truth**: 60 controlled synthetic UPI payment receipt images across 3 templates (ApexPay, ZenithUPI, NovaPay) with split isolation (`train` 60%, `val` 20%, `test` 20%) and zero data leakage.
2. **OCR Preprocessing & Extraction Pipeline (`src/ocr/`)**: Tesseract OCR (PSM 3) with configurable preprocessing pipelines (contrast enhancement, adaptive thresholding, denoise) and resilient field parsing (Amount, Date, Time, UTR, Template, Recipient).
3. **Rule-Based Validation Engine (`src/rules/`)**: Deterministic verification using 11 atomic rule checks, calculating weighted anomaly scores and explainable violations for Person 1's ensemble aggregator.
4. **Empirical Evaluation & Unit Test Suite**: Comprehensive measurement script (`scripts/evaluate_ocr_rules.py`) and 78 unit tests (`tests/`).
5. **Technical Documentation (`docs/`)**: Rigorous academic documentation for `dataset.md`, `ocr.md`, and `rules.md`.

---

## 📂 Directory Structure

```
PERSON_2_NIVASH/
├── data/
│   ├── metadata.csv          # Ground-truth labels, splits, bounding boxes, and field values
│   └── raw/                  # 60 synthetic receipt images (img_001.png to img_060.png)
├── docs/
│   ├── dataset.md            # Dataset specification, template schemas, and split strategy
│   ├── ocr.md                # OCR pipeline, preprocessing comparison, and error analysis
│   └── rules.md              # Rule catalogue, anomaly formulation, and evaluation metrics
├── scripts/
│   ├── generate_dataset.py   # Deterministic dataset generation script
│   └── evaluate_ocr_rules.py # Empirical evaluation benchmark across all splits
├── src/
│   ├── ocr/
│   │   ├── __init__.py       # Public API: extract_transaction_fields, preprocess_image
│   │   ├── extractor.py      # Main OCR pipeline (PSM 3 page segmentation)
│   │   ├── field_parser.py   # Regex & heuristic normalization engine
│   │   └── preprocess.py     # Image loading & transformation pipelines
│   └── rules/
│       ├── __init__.py       # Public API: validate_transaction
│       ├── rule_engine.py    # Weighted anomaly scoring & verdict generation
│       └── validators.py     # 11 atomic rule check functions
├── tests/
│   ├── test_field_parser.py  # Regex & parser unit tests
│   ├── test_ocr_extractor.py # End-to-end OCR extraction tests
│   ├── test_preprocess.py    # Image transformation tests
│   └── test_rules.py         # Rule engine & violation tests
└── README.md                 # Person 2 Quickstart & Architecture Guide
```

---

## 🚀 Quickstart & Execution

### 1. Run Unit Tests (78 tests)
```bash
cd PERSON_2_NIVASH
pytest tests/ -v
```

### 2. Run Empirical Evaluation Script
```bash
cd PERSON_2_NIVASH
python scripts/evaluate_ocr_rules.py
```

### 3. Re-generate Synthetic Dataset (Optional)
```bash
cd PERSON_2_NIVASH
python scripts/generate_dataset.py
```

---

## 📊 Key Evaluation Metrics (Empirically Measured)

### OCR Extraction Accuracy (Test Split - 12 images)
- **Extraction Success Rate**: `100.0%`
- **Exact Amount Accuracy**: `100.0%`
- **Exact Date Accuracy**: `100.0%`
- **Exact UTR Accuracy**: `100.0%`

### Rule Engine Tamper Detection (Overall Dataset - 60 images)
- **Precision**: `93.9%` (Test Split: `100.0%`)
- **Recall**: `68.9%` (Test Split: `66.7%`)
- **F1-Score**: `79.5%` (Test Split: `80.0%`)
- **Specificity**: `86.7%` (Test Split: `100.0%`)
- **Accuracy**: `73.3%` (Test Split: `75.0%`)

---

## 🔗 Integration Contract for Person 1 (Ensemble / UI)

```python
from src.ocr import extract_transaction_fields
from src.rules import validate_transaction

# Step 1: Extract fields via OCR
ocr_output = extract_transaction_fields("path/to/receipt.png")

# Step 2: Validate fields via Rule Engine
rule_verdict = validate_transaction(ocr_output)

# Results ready for UI display or Fusion with Person 3's CNN score:
print(rule_verdict["verdict"])        # 'LIKELY_LEGITIMATE' or 'SUSPICIOUS'
print(rule_verdict["anomaly_score"])  # Float between 0.0 and 1.0
print(rule_verdict["explanations"])   # List of plain-English violation descriptions
```

---

## 🎓 Academic Defense & Integrity
- **Synthetic Watermark**: Every receipt image contains a visible footer watermark `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY`.
- **Zero Data Leakage**: All 60 receipts were generated with seeded independent variations and strictly partitioned into 36 train, 12 validation, and 12 test records.
- **Explainability**: No black-box decisions in the rule layer — every flagged anomaly directly cites the offending field and the exact validation rule violated.
