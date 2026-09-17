# UPI Fraud Forensics Platform

## Project Overview

**Project title:** UPI Fraud Forensics Platform  
**Duration:** 12 months  
**Current stage:** 30% progress  
**Project type:** Image-based payment screenshot authenticity and fraud-forensics analysis platform

## Team

| Member | Responsibility | Module Folder | Status (30% Review) |
|---|---|---|:---:|
| **Person 1 (Rithvik)** | Project lead, Streamlit frontend, integration, ensemble orchestration, deployment, documentation | `PERSON_1_RITHVIK/` | In Progress |
| **Person 2 (Nivash)** | Dataset generation, preprocessing, Tesseract OCR pipeline (PSM 3), Rule Engine, 89 unit tests, documentation | `PERSON_2_NIVASH/` | **Completed (100%)** |
| **Person 3 (Sanjay)** | CNN model, image forensics (ELA, noise maps), pixel-level tamper detection, evaluation | `PERSON_3_SANJAY/` | In Progress |

---

# 1. Problem Statement

UPI payment screenshots are often shared as proof of payment. However, screenshots can be edited, recreated, or manipulated. Possible changes may involve the amount, transaction ID, UPI ID, date, time, payment status, names, font rendering, layout, compression, or image regions.

Manual inspection is unreliable, especially when the manipulation is subtle. This project aims to build a modular platform that analyzes screenshots for authenticity-related signals using OCR, rule-based validation, image forensics, CNN-based visual analysis, and an ensemble decision layer.

The platform is an investigation-support tool. It must not claim to verify that a real bank transaction occurred solely from an image.

# 2. Main Objectives

- Accept PNG, JPG, and JPEG screenshots.
- Extract visible transaction information using OCR.
- Validate extracted fields using logical rules.
- Detect suspicious image-level manipulation signals.
- Train and use a CNN for visual classification when sufficient data is available.
- Combine available module outputs through an explainable ensemble layer.
- Display individual results, reasons, missing evidence, and limitations.
- Handle incomplete or unavailable modules without crashing.
- Provide a clean Streamlit interface for demonstration.
- Maintain a reproducible and academically honest workflow.

# 3. Scope of the Current 30% Stage

The 30% milestone focuses on establishing the foundation of the complete system rather than completing every advanced model.

Expected progress:

- Repository organization and team ownership.
- Basic Streamlit frontend.
- Image upload and preview.
- Initial integration architecture.
- Defined module contracts.
- Complete synthetic dataset, OCR, and rule-engine implementation by Person 2 (Nivash).
- Initial image-forensics and CNN work by Person 3.
- Early result display and ensemble orchestration by Person 1.
- Unit testing and academic documentation.
- Safe demonstration using synthetic or fictional data.

# 4. High-Level Architecture

```text
User
  |
  v
Streamlit Frontend (Person 1)
  |
  v
Image Upload and Validation
  |
  +---------------------------------------------+
  |                                             |
  v                                             v
OCR Module (Person 2 - Nivash)          Image Forensics (Person 3)
  |                                             |
  v                                             v
Extracted Fields                           Forensic Signals
  |                                             |
  v                                             v
Rule Engine (Person 2 - Nivash)             CNN Model (Person 3)
  |                                             |
  +---------------------+-----------------------+
                        |
                        v
                 Ensemble Layer (Person 1)
                        |
                        v
                Combined Assessment
                        |
                        v
               Reasons and Results
```

---

# 5. Person 2 (Nivash) — Deliverables & Architecture

All deliverables for Person 2 are housed in [`PERSON_2_NIVASH/`](file:///Users/nivash/elenxis/PERSON_2_NIVASH):

### 1. Controlled Synthetic Dataset (`data/`)
- **60 Synthetic UPI Receipts** generated across 3 distinct design templates (`ApexPay`, `ZenithUPI`, `NovaPay`).
- **Data Splitting**: Strict `train` (36), `val` (12), `test` (12) partition with zero data leakage.
- **Ground Truth**: [`data/metadata.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/metadata.csv) with tamper type annotations, bounding boxes, and ground-truth values.
- **Academic Safety**: All receipts are stamped with `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY`.

### 2. OCR Preprocessing & Extraction Pipeline (`src/ocr/`)
- Preprocessing engine with 4 modes (`contrast`, `adaptive_thresh`, `grayscale`, `denoise`).
- **PSM 3 Layout Optimization**: Fully automatic segmentation detecting top header, large centered hero amount, and transaction details grid.
- **Field Normalization**: Resilient extraction of Amount, Date, Time, 12-digit UTR, App Template, and Recipient.

### 3. Rule-Based Validation Engine (`src/rules/`)
- **11 Atomic Validators**: Format checks, completeness verification, and logical rules (e.g., future date detection, 12-digit UTR length constraints).
- **Weighted Anomaly Score**: Computes risk score $S \in [0.0, 1.0]$ with clear human-readable explanations.

### 4. Empirical Evaluation & Test Suite (`scripts/`, `tests/`)
- **89 Passing Unit Tests** with deterministic coverage across preprocessing, parsing, extraction, and rule validation.
- **Evaluation Benchmark**: Full accuracy metrics measured on ground truth:
  - **OCR Extraction Rate**: `100.0%`
  - **Amount Accuracy (Test Split)**: `100.0%`
  - **Date Accuracy (Test Split)**: `100.0%`
  - **UTR Accuracy (Test Split)**: `100.0%`
  - **Rule Engine Precision**: `93.9%` (Overall) / `100.0%` (Test Split)

---

## 🚀 Quickstart & Commands

### Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Person 2 Tests (89 unit tests)
```bash
cd PERSON_2_NIVASH
pytest tests/ -v
```

### Run Person 2 Empirical Evaluation
```bash
cd PERSON_2_NIVASH
python scripts/evaluate_ocr_rules.py
```

---

## 📚 Technical Documentation
- [Dataset Specification & Schema](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/dataset.md)
- [OCR Extraction Pipeline & Error Analysis](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/ocr.md)
- [Rule Engine Catalogue & Scoring Formulation](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/rules.md)
- [Person 2 Quickstart Guide](file:///Users/nivash/elenxis/PERSON_2_NIVASH/README.md)
