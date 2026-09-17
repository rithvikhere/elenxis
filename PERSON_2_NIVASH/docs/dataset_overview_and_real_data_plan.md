# Dataset Overview & Real-Data Integration Roadmap
**UPI Transaction Fraud Forensics Platform (12-Month Academic IDP)**  
**Subsystem:** Person 2 (Dataset Synthesis, OCR Pipeline & Rule Engine)  
**Author:** Nivash Kumaar S (25BAI1503) / Person 2  
**Date:** September 2026  

---

## 1. Executive Summary

This document details:
1. **Current State**: The architecture, generation methodology, and verification metrics of the existing synthetic dataset (300 images).
2. **Academic & Legal Rationale**: Why synthetic procedural data was developed for the Phase 1/30% review.
3. **Future Plan (User Proposal)**: The integration roadmap for collecting, anonymizing, annotating, and benchmarking **real UPI screenshots** (Google Pay, PhonePe, Paytm) for advanced reviews and domain adaptation research.

---

## 2. Current Dataset: What is Present Right Now

The current repository contains a fully verified, procedurally generated synthetic dataset designed to benchmark OCR field extraction, rule-based validation, and CNN classification without privacy or legal risks.

```
PERSON_2_NIVASH/data/
├── raw/                          # 60 pristine original synthetic receipts
│   ├── tpl1_src001_none_01.png   # PayLite (Family 1)
│   ├── tpl2_src021_none_01.png   # QuickPe (Family 2)
│   └── tpl3_src041_none_01.png   # UniPay (Family 3)
├── processed/                    # 240 controlled manipulated variants
│   ├── tpl1_src001_amt_01.png    # Amount altered
│   ├── tpl1_src001_date_01.png   # Date tampered (future timestamp)
│   └── ...
├── ground_truth.csv              # Exact ground-truth values for all 60 originals
├── metadata.csv                  # Complete 300-row manifest with label taxonomy & edit types
└── splits/                       # Group-stratified, zero-leakage partitions
    ├── train.csv                 # 210 images (42 source groups, 70.0%)
    ├── val.csv                   # 45 images (9 source groups, 15.0%)
    └── test.csv                  # 45 images (9 source groups, 15.0%)
```

### 2.1 The 3 Non-Branded Template Families

| Template Family | Internal Code | Design Language / Layout | Canvas Dimensions | Palette / UI Elements |
|---|---|---|---|---|
| **PayLite** | `Family 1` | Minimalist light card | $720 \times 1280$ px | Pure white `#FFFFFF`, emerald green `#00875A` success badge, subtle grey divider cards |
| **QuickPe** | `Family 2` | Dark card modern UI | $720 \times 1280$ px | Charcoal dark `#1E293B`, deep navy accents, high-contrast cyan `#06B6D4` transaction details |
| **UniPay** | `Family 3` | Corporate bank receipt | $720 \times 1280$ px | Light blue header `#E0F2FE`, formal bordered table, indigo `#3B82F6` status seals |

### 2.2 Controlled Manipulation Types (9 Edit Classes)

Every source original generates 4 distinct manipulated variants:

| Edit Type | Category | Semantic / Forensic Transformation | Label Class |
|---|---|---|---|
| `none` | Clean Original | Baseline unedited render | `original` |
| `amount_change` | Tamper (Semantic) | Amount replaced with a mismatched font, size, or alignment | `synthetic_fake` |
| `date_change` | Tamper (Temporal) | Timestamp altered to a future date or invalid day | `synthetic_fake` |
| `transaction_id_change` | Tamper (Syntactic) | 12-digit UTR replaced with invalid length or alpha prefix (`TXN...`) | `synthetic_fake` |
| `text_insert` | Tamper (Visual) | Mismatched transaction notes or spoofed merchant names inserted | `synthetic_fake` |
| `text_remove` | Tamper (Incomplete) | Critical bounding box (UTR or Date) erased/in-painted to white | `synthetic_fake` |
| `stamp_overlay` | Tamper (Deceptive) | Deceptive badge overlay (`[ 100% VERIFIED ]`, `[ AUTHENTICATED ]`) | `synthetic_fake` |
| `crop` | Structural | Canvas clipped by 15% along bounding edges | `synthetic_fake` |
| `resize` | Channel Noise | Downscaled to 60% and upscaled via bilinear interpolation | `original_transformed` |
| `recompress` | Channel Noise | Re-saved at JPEG Quality 30 (lossy DCT quantization compression) | `original_transformed` |

### 2.3 Key Dataset Properties

- **Zero Data Leakage**: Source-grouped stratification ensures all 4 variants and the source original stay strictly in the same partition (`train`, `val`, or `test`).
- **Zero Duplicate Perceptual Hashes**: Verified via 256-bit dHash perceptual hashing across partitions.
- **Safety Watermarking**: All 300 images carry the permanent header: `DEMO / SYNTHETIC RECEIPT — RESEARCH ONLY`.

---

## 3. Why Synthetic Procedural Data Was Developed

1. **User Financial Privacy (DPDP Act & RBI Regulations)**:  
   Real payment receipts contain sensitive Personally Identifiable Information (PII) — real customer names, mobile numbers, bank account numbers, and live account balances. Storing or committing un-anonymized real payment data to academic repositories violates data ethics and institutional policies.
2. **Absence of Public Benchmarks**:  
   There is no open-source, labeled dataset of authentic vs. forged Indian UPI screenshots.
3. **Exact Pixel-Level Provenance**:  
   Real web-scraped images lack ground truth (unknown fonts, unknown original values, unknown compression cycles). Synthetic procedural generation provides an exact, mathematically verified ground-truth key (`data/ground_truth.csv`).
4. **Trademark & Copyright Protection**:  
   Avoids direct trademark infringement of proprietary brand assets (Google Pay, PhonePe, Paytm logos).

---

## 4. Real-Data Integration Plan (The User Roadmap)

As the project progresses through the 12-month lifecycle (toward Phase 4: Field Testing & Final Deployment), real-world payment screenshots will be introduced to evaluate **real-world generalization** and **domain adaptation**.

```
                       ┌───────────────────────────────┐
                       │   CURRENT SYNTHETIC ENGINE    │
                       │     (300 Controlled Assets)   │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │    REAL SCREENSHOT INGESTION  │
                       │   (Google Pay, PhonePe, Paytm) │
                       └───────────────┬───────────────┘
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     STAGE 1: ANONYMIZATION    │               │     STAGE 2: ANNOTATION       │
│  • PII & Phone Redaction      │               │  • True Amount, Date, UTR     │
│  • Bank Account Masking       │               │  • Tamper Bounding Boxes      │
│  • Local Untracked Storage    │               │  • `data/real_metadata.csv`   │
└───────────────┬───────────────┘               └───────────────┬───────────────┘
                │                                               │
                └───────────────────────┬───────────────────────┘
                                        ▼
                        ┌───────────────────────────────┐
                        │   STAGE 3: DOMAIN EVALUATION  │
                        │  • Zero-Shot Synthetic → Real  │
                        │  • Real-World Fine-Tuning     │
                        │  • Real vs Synthetic Metrics  │
                        └───────────────────────────────┘
```

### 4.1 Ingestion Directory Architecture

To protect real user data, real screenshots will be stored in a dedicated local directory that is ignored by Git:

```
PERSON_2_NIVASH/data/
├── real_raw/                     # Untracked in .gitignore (Local Only)
│   ├── real_gpay_001.jpg
│   ├── real_phonepe_002.png
│   └── real_paytm_003.jpg
├── real_metadata.csv             # Anonymized metadata manifest
└── splits_real/                  # Independent real-world validation splits
```

### 4.2 Real Dataset Metadata Schema (`data/real_metadata.csv`)

| Column Name | Data Type | Example Value | Description |
|---|---|---|---|
| `image_id` | String | `real_gpay_001` | Unique image identifier |
| `app_family` | String | `GooglePay` | Real UPI application source |
| `label` | String | `original` or `real_tampered` | Ground truth label |
| `amount_true` | String | `₹1,450.00` | Actual transaction amount |
| `date_true` | String | `18 Sep 2026` | Actual date printed |
| `utr_true` | String | `429183749102` | 12-digit UPI reference number |
| `is_tampered` | Boolean | `False` | Whether the screenshot was edited in third-party software |
| `tamper_method` | String | `photoshop_splice` | Specific editing tool used (if tampered) |

### 4.3 PII Redaction & Ethical Protocol

Before any real image is analyzed or shared:
1. **Donor Consent**: Obtain written/verbal informed consent from voluntary test donors.
2. **PII Masking**: Bank account suffixes (e.g., `••• 4821`) and mobile numbers must be redacted or sanitized.
3. **No Financial Credentials**: Never collect, store, or process PINs, OTPs, or passwords.

---

## 5. Compatibility with Existing Modules

The existing code in `PERSON_2_NIVASH` was specifically built to ingest real data without requiring architectural rewrites:

1. **OCR Field Extractor (`src/ocr/extractor.py`)**:
   - Accepts any standard image format (`.png`, `.jpg`, `.jpeg`, `.webp`, PIL Image, or file byte buffer).
   - Uses Page Segmentation Mode (`--psm 3`) to extract centered text and multi-column payment receipts.
2. **Regex Field Parser (`src/ocr/field_parser.py`)**:
   - Already equipped with regex rules for standard Indian UPI conventions:
     - 12-digit numeric UTR extraction across keywords (`UPI Ref No`, `Google Transaction ID`, `UTR`, `Txn ID`).
     - Standard Indian comma notation (`₹1,50,000.00`) and OCR error correction (e.g., `%` $\rightarrow$ `₹`).
     - Standard 12-hour/24-hour timestamps and mixed named/numerical dates.
3. **Rule Engine (`src/rules/rule_engine.py`)**:
   - Universal logical validation (temporal checks, UTR length/format, amount positivity) applies directly to real screenshots.

---

## 6. Academic Contribution: Domain Adaptation Study

Having both the **Synthetic Dataset** and the upcoming **Real Dataset** enables a high-impact research contribution for the final IDP dissertation:

| Experiment Configuration | Training Data | Evaluation Data | Research Question Answered |
|---|---|---|---|
| **Baseline** | Synthetic Train | Synthetic Test | Does the multi-signal system learn synthetic tamper signatures? |
| **Zero-Shot Domain Transfer** | Synthetic Train | **Real Test Set** | How well does a synthetically trained model generalize to unseen real-world screenshots? |
| **Domain Fine-Tuning** | Synthetic + 20% Real | **80% Real Test Set** | Does synthetic pre-training boost sample efficiency on limited real-world data? |

---

*This document serves as the official record of the current synthetic dataset implementation and the concrete architectural plan for real-data integration.*
