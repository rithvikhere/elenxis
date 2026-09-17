# Phase 4: Leakage-Safe Splitting, Integrity Audit & Dataset Documentation
**Person 2 Subsystem — UPI Transaction Fraud Forensics Platform**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic IDP Project*

---

## 📌 Phase Overview & Objectives

Phase 4 delivers a **leakage-safe, group-aware train/val/test splitting pipeline** (`src/dataset/split.py`), an **11-point automated dataset integrity and data leakage audit system** (`src/dataset/audit.py`), the complete **12-section dataset specification** (`docs/dataset.md`), and an explicit **handoff guide for Person 3** (`docs/handoff_dataset.md`).

### Key Deliverables Accomplished:
- [x] **Group-Aware Splitting by `source_id`**: Guarantees all 4 variants and original of a source receipt reside exclusively in the same partition, eliminating data leakage.
- [x] **Stratified Template Distribution**: Stratifies at the group level by `template_family`, ensuring identical 70:15:15 representation for all 3 layouts.
- [x] **Realized Split Manifests**: Generated `data/splits/train.csv` (210 images, 70.0%), `data/splits/val.csv` (45 images, 15.0%), and `data/splits/test.csv` (45 images, 15.0%).
- [x] **11-Point Automated Dataset Integrity Audit**: Built `src/dataset/audit.py` with 256-bit perceptual difference hashing (dHash), validating zero cross-split near-duplicate visual collisions.
- [x] **Deterministic Byte-Identical Splits**: Verified split reproducibility with random seed `42`.
- [x] **Comprehensive Documentation**: Completed full 12-section `docs/dataset.md` and `docs/handoff_dataset.md` with explicit instructions for Person 3 to independently re-verify.
- [x] **Unit Tests**: Created `tests/test_split.py` (7/7 tests passing; 26/26 tests passing across Phases 1–4).

---

## 🛡️ Why Data Leakage is the Highest Risk & How We Solved It

```
                                  +----------------------------+
                                  | Original Source (src001)   |
                                  +----------------------------+
                                                |
                   +----------------------------+----------------------------+
                   |                            |                            |
                   v                            v                            v
          [Variant: Amount Change]      [Variant: Font Alter]        [Variant: Recompress]

 ❌ NAIVE SPLIT (BY IMAGE_ID):
    • Train: Original + Variant 1 + Variant 2
    • Test:  Variant 3  <-- LEAKAGE! Model memorized background geometry & recipient layout.

 ✅ GROUP-AWARE SPLIT (BY SOURCE_ID):
    • ALL variants of src001 go to TRAIN together.
    • TEST split contains ONLY completely unseen sources (e.g. src018, src019, src020).
    • ZERO overlap of source_id, background styles, or transaction entities.
```

---

## 📊 Realized Split Metrics & Distributions

### Realized Counts by Split
- **Train Set**: 42 sources $\rightarrow$ **210 images (70.0%)**
- **Validation Set**: 9 sources $\rightarrow$ **45 images (15.0%)**
- **Test Set**: 9 sources $\rightarrow$ **45 images (15.0%)**
- **Total**: 60 sources $\rightarrow$ **300 images (100.0%)**

### Template Family Stratification
| Split | Family 1 (`PayLite`) | Family 2 (`QuickPe`) | Family 3 (`UniPay`) | Total |
|:---|:---:|:---:|:---:|:---:|
| **TRAIN** | 70 | 70 | 70 | **210** |
| **VAL** | 15 | 15 | 15 | **45** |
| **TEST** | 15 | 15 | 15 | **45** |
| **Total** | **100** | **100** | **100** | **300** |

### Label Class Breakdown
| Split | `original` | `original_transformed` | `synthetic_fake` | Total |
|:---|:---:|:---:|:---:|:---:|
| **TRAIN** | 42 (20.0%) | 30 (14.3%) | 138 (65.7%) | **210** |
| **VAL** | 9 (20.0%) | 13 (28.9%) | 23 (51.1%) | **45** |
| **TEST** | 9 (20.0%) | 3 (6.7%) | 33 (73.3%) | **45** |
| **Total** | **60 (20.0%)** | **46 (15.3%)** | **194 (64.7%)** | **300** |

---

## 🔍 Automated Audit Results (11 Checks Passed)

Output from `python -m src.dataset.audit`:

```
======================================================================
DATASET INTEGRITY & DATA LEAKAGE AUDIT REPORT — PERSON 2
======================================================================
Total Images Audited    : 300
Train Split Manifest    : 210 images (42 unique sources, 70.0%)
Val Split Manifest      : 45 images (9 unique sources, 15.0%)
Test Split Manifest     : 45 images (9 unique sources, 15.0%)
----------------------------------------------------------------------
[VERIFICATION CHECKS BREAKDOWN]
  [✓ PASS] 1. Group Disjointness (Zero Source Leakage)
  [✓ PASS] 2. File Existence on Disk
  [✓ PASS] 3. Zero Orphan Disk Files
  [✓ PASS] 4. Zero Duplicate Image IDs
  [✓ PASS] 5. Template Family Coverage across all splits
  [✓ PASS] 6. Label Class Coverage across all splits
  [✓ PASS] 7. Class Balance Consistency Reporting
  [✓ PASS] 8. Cross-Split Perceptual Near-Duplicate Hash Check (256-bit dHash)
  [✓ PASS] 9. Image Header & Pixel Decoding Check
  [✓ PASS] 10. Dimension Outlier & Canvas Constraint Check
  [✓ PASS] 11. Ground-Truth Answer Key Coverage
----------------------------------------------------------------------
🎉 OVERALL VERDICT: 100% AUDIT PASSED. DATASET IS LEAKAGE-FREE.
======================================================================
```

Full report archived at [`results/metrics/dataset_audit.txt`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/results/metrics/dataset_audit.txt).

---

## 📂 Phase 4 Artifacts & Deliverables

| Component | File Path | Description |
|:---|:---|:---|
| **Split Generator** | [`src/dataset/split.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/split.py) | Group-aware splitting stratified by `template_family`. |
| **Dataset Auditor** | [`src/dataset/audit.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/audit.py) | 11-point leakage and integrity audit runner with dHash collision check. |
| **Split Manifests** | `data/splits/` | `train.csv` (210), `val.csv` (45), `test.csv` (45). |
| **Audit Report** | [`results/metrics/dataset_audit.txt`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/results/metrics/dataset_audit.txt) | Generated plain text audit verification report. |
| **Dataset Specification** | [`docs/dataset.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/dataset.md) | Complete 12-section specification with actual counts and limitations. |
| **Handoff Document** | [`docs/handoff_dataset.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/handoff_dataset.md) | Person 3 dataloader guide and independent verification commands. |
| **Unit Tests** | [`tests/test_split.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/tests/test_split.py) | Unit tests verifying group disjointness, stratification, and determinism. |

---

## 🚀 Execution & Verification Commands

### 1. Run Complete Unit Test Suite (Phases 1–4: 26 passed)
```bash
cd PERSON_2_NIVASH
pytest tests/test_paths_config.py tests/test_templates.py tests/test_manipulate.py tests/test_dataset.py tests/test_split.py -v
```

### 2. Run Dataset Integrity & Leakage Audit
```bash
python -m src.dataset.audit
```

### 3. Regenerate Leakage-Safe Splits
```bash
python -m src.dataset.split --train 0.70 --val 0.15 --test 0.15 --seed 42
```
