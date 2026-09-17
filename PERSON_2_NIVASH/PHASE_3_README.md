# Phase 3: Controlled Manipulation Engine & Labeled Metadata
**Person 2 Subsystem — UPI Transaction Fraud Forensics Platform**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic IDP Project*

---

## 📌 Phase Overview & Objectives

Phase 3 implements the **Controlled Manipulation Engine** (`src/dataset/manipulate.py`) and dataset sanity audit mechanism (`src/dataset/audit.py`). It applies 9 distinct programmatic transformations to the synthesized originals, records the ground truth for modified fields, and creates the canonical [`data/metadata.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/metadata.csv) index for downstream CNN training, forensics, and rule validation.

### Key Goals Accomplished:
- [x] Implemented 9 distinct manipulation functions across visual, logical, and structural categories.
- [x] Adopted and documented the **Tri-State Label Taxonomy** (`original`, `original_transformed`, `synthetic_fake`), explicitly preventing benign compression/resizing from being mislabeled as fraud.
- [x] Generated **240 controlled variants** (4 per original) linked back to source originals via `source_id`.
- [x] Produced unified [`data/metadata.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/metadata.csv) (300 total images).
- [x] Updated [`data/ground_truth.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/ground_truth.csv) with accurate ground-truth values for altered fields.
- [x] Created dataset sanity audit script (`src/dataset/audit.py`) ensuring 100% disk-to-CSV integrity.
- [x] Exported sample before/after image pairs to `docs/samples/`.
- [x] Created unit test suite in `tests/test_manipulate.py` (3/3 passing tests; 12/12 total).

---

## 🔬 Label Semantics & Manipulation Categories

```
                              +-------------------------------------------+
                              |      All Dataset Images (300 Total)       |
                              +-------------------------------------------+
                                                    |
                         +--------------------------+-------------------------+
                         |                                                     |
                         v                                                     v
          +-----------------------------+                       +-----------------------------+
          |      Content-Identical      |                       |      Content-Altered        |
          |       (106 images)          |                       |       (194 images)          |
          +-----------------------------+                       +-----------------------------+
          |  label: original            |                       |  label: synthetic_fake      |
          |  • none (60 images)         |                       |  • amount_change (24)       |
          |                             |                       |  • date_change (29)         |
          |  label: original_transformed|                       |  • transaction_id_change(28)|
          |  • resize (22 images)       |                       |  • text_insert (27)         |
          |  • recompress (24 images)   |                       |  • text_remove (25)         |
          |                             |                       |  • font_alter (31)          |
          | (Benign Channel Noise)      |                       |  • crop (30)                |
          +-----------------------------+                       +-----------------------------+
```

### Why `original_transformed` is NOT Labeled Fake:
Forwarding receipts over chat apps naturally resizes and recompresses images. If benign compression were labeled `synthetic_fake`, the CNN model would learn to detect JPEG compression artifacts rather than actual payment manipulation. The `original_transformed` label allows the model to learn invariance to benign channel degradation.

---

## 📂 Phase 3 Artifacts & Deliverables

| Component | File Path | Description |
|:---|:---|:---|
| **Manipulation Engine** | [`src/dataset/manipulate.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/manipulate.py) | Functions for 9 edit types, batch orchestrator, and CLI runner. |
| **Dataset Audit Script** | [`src/dataset/audit.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/audit.py) | Automated sanity auditor checking CSV schema, disk presence, orphan files, and family distributions. |
| **Dataset Package Init** | [`src/dataset/__init__.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/__init__.py) | Exports manipulation functions and audit runner. |
| **Dataset Metadata** | [`data/metadata.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/metadata.csv) | Master index with 300 rows containing labels, edit types, source IDs, dimensions, and relative paths. |
| **Ground-Truth CSV** | [`data/ground_truth.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/ground_truth.csv) | 300 reference rows with updated ground truth for modified amounts, dates, and UTRs. |
| **Sample Pairs** | `docs/samples/` | Added `sample_amount_change_after.png`, `sample_date_change_after.png`, `sample_recompress_after.png`. |
| **Documentation** | [`docs/dataset.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/dataset.md) | Added Section 10 "Generation — Manipulations" detailing exact counts, class balance, and label semantics. |
| **Unit Tests** | [`tests/test_manipulate.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/tests/test_manipulate.py) | Tests all 9 manipulators, metadata schema, and audit verification. |

---

## 🚀 Execution & Verification Commands

### 1. Run Unit Tests (12/12 passing across Phases 1, 2, 3)
```bash
cd PERSON_2_NIVASH
pytest tests/ -v
```

### 2. Run Dataset Sanity Audit
```bash
python -m src.dataset.audit
```

### 3. Regenerate Manipulated Dataset CLI
```bash
python -m src.dataset.manipulate --variants-per-original 4 --samples
```

---

## 📊 Empirical Dataset Summary (Audit Output)

```
============================================================
DATASET SANITY AUDIT REPORT — PERSON 2
============================================================
Total Registered Images : 300
Total Unique Sources   : 60
Variants per Source    : Min=4, Median=4.0, Max=4

[Label Distribution]
  • original              :   60 (20.0%)
  • synthetic_fake        :  194 (64.7%)
  • original_transformed  :   46 (15.3%)

[Edit Type Distribution]
  • none                  :   60
  • date_change           :   29
  • font_alter            :   31
  • crop                  :   30
  • transaction_id_change :   28
  • text_insert           :   27
  • text_remove           :   25
  • amount_change         :   24
  • recompress            :   24
  • resize                :   22

[Template Family Distribution]
  • Family 1 (PayLite)    :  100
  • Family 2 (QuickPe)    :  100
  • Family 3 (UniPay)     :  100

[Disk Integrity Check]
  ✓ All CSV image entries exist on disk.
  ✓ Zero orphan/unregistered image files on disk.
============================================================
🎉 AUDIT PASSED: 100% Data Integrity Verified.
```

---
*Phase 3 is complete and verified. Standing by for Phase 4: Leakage-Free Dataset Splitting.*
