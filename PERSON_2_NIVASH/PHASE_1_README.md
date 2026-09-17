# Phase 1: Foundation, Scaffolding & Template Design Specification
**Person 2 Subsystem — UPI Transaction Fraud Forensics Platform**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic IDP Project*

---

## 📌 Phase Overview & Objectives

Phase 1 establishes the architectural foundation, path resolution mechanism, dataset configuration system, and comprehensive template design specifications that all subsequent phases (Phases 2 through 8) depend on.

### Key Goals Accomplished:
- [x] Set up modular package scaffolding with strict ownership boundaries.
- [x] Create a centralized, dynamic path resolution manager to eliminate hard-coded paths.
- [x] Define global dataset constants, seed reproducibility, and fictional template identities.
- [x] Author the 10-point **Template Design Specification** in `docs/dataset.md`.
- [x] Pin minimal, non-redundant dependencies with documented rationale in `requirements.txt`.
- [x] Create deterministic unit tests verifying paths and configuration integrity.

---

## 📂 Phase 1 Artifacts & Deliverables

| Component | File Path | Description |
|:---|:---|:---|
| **Path Manager** | [`src/utils/paths.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/utils/paths.py) | Resolves `PROJECT_ROOT`, `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `SPLITS_DIR`, `METADATA_CSV`, `DOCS_DIR`, `TESTS_DIR` dynamically. Includes `ensure_dir()` utility. |
| **Path Package Init** | [`src/utils/__init__.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/utils/__init__.py) | Exports all path constants and helpers for clean cross-module imports. |
| **Dataset Config** | [`src/dataset/config.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/config.py) | Central repository constants: `RANDOM_SEED = 42`, `IMAGE_SIZE = (400, 800)`, `TEMPLATE_NAMES = ["PayLite", "QuickPe", "UniPay"]`, 10 `EDIT_TYPES`, `AMOUNT_RANGE`, `DATE_RANGE`, `TXN_ID_FORMAT`, and `DEMO_WATERMARK_TEXT`. |
| **Dataset Package Init** | [`src/dataset/__init__.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/__init__.py) | Exports dataset package configuration. |
| **Template Design Spec** | [`docs/dataset.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/dataset.md) | Complete 10-point specification covering: synthetic rationale, fictional templates, 3 layout families, coordinate anchors, ground-truth schema, 10 edit types, group-aware naming, watermark policy, ethical safety, and target scale. |
| **OCR Documentation Stub** | [`docs/ocr.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/ocr.md) | Initial stub pointing to Phases 5 & 6. |
| **Rules Documentation Stub** | [`docs/rules.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/rules.md) | Initial stub pointing to Phase 7. |
| **Dependencies** | [`requirements.txt`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/requirements.txt) | Pinned dependencies with inline comments: `pillow==12.3.0`, `opencv-python==4.11.0.86`, `numpy==2.5.3`, `pandas==3.0.5`, `pytest==9.1.1`, `python-dateutil==2.9.0.post0`. |
| **Unit Test Suite** | [`tests/test_paths_config.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/tests/test_paths_config.py) | Deterministic unit tests covering root existence, subdirectory auto-creation, and configuration parameter validity. |

---

## 🏗️ Architectural Decisions & Design Rationale

### 1. Zero Hard-Coded Paths (`src/utils/paths.py`)
- **Problem**: Hard-coded relative strings like `../../data` break when scripts are run from different working directories.
- **Solution**: `paths.py` uses `Path(__file__).resolve().parent.parent.parent` to lock `PROJECT_ROOT`, ensuring that imports and file writes function identically from repo root, subdirectories, or testing runners.

### 2. Three Distinct Layout Families
- **Problem**: Training a detector on a single rigid receipt layout leads to severe overfitting.
- **Solution**: Designed 3 distinct layout families:
  1. **`PayLite`**: Traditional flat top header banner + large centered hero amount ($y \approx 260\text{px}$).
  2. **`QuickPe`**: Elevated central card container + stacked inline transaction attributes.
  3. **`UniPay`**: Clean minimalist two-tone grid + ISO date formatting (`YYYY-MM-DD`).

### 3. Data Leakage Prevention by Design
- **Problem**: Distributing near-identical visual edits of the same receipt across train and test sets leads to inflated, artificial test accuracy.
- **Solution**: Structured image IDs as `tpl{F}_src{NNN}_{edit}_{VV}`. Data splitting in Phase 4 is grouped strictly by `src{NNN}`, guaranteeing zero source overlap between train, validation, and test splits.

---

## 🧪 Verification & Acceptance Checklist

To execute the automated verification test for Phase 1:

```bash
# Run Phase 1 unit tests
cd PERSON_2_NIVASH
pytest tests/test_paths_config.py -v
```

### Test Results:
```
tests/test_paths_config.py::test_project_root_exists PASSED              [ 25%]
tests/test_paths_config.py::test_data_subdirectories_exist PASSED        [ 50%]
tests/test_paths_config.py::test_ensure_dir PASSED                       [ 75%]
tests/test_paths_config.py::test_config_constants PASSED                 [100%]
============================== 4 passed in 0.01s ===============================
```

---

## 🛡️ Academic & Ethical Safety Rules (Non-Negotiable)
1. **Fictional Stand-ins**: All brand names (`PayLite`, `QuickPe`, `UniPay`) are fictional to prevent trademark violations.
2. **Synthetic Data Only**: All UTRs, account numbers, and transaction IDs are generated from mock distributions. No real banking ledgers or real customer PII are used.
3. **Mandatory Watermarking**: Every generated asset carries `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` in the footer.
4. **Detector Scope**: Assets exist solely to train and benchmark forensic detection algorithms, not to produce deceptive payment proof.

---
*Phase 1 is complete and verified. Standing by for Phase 2: Template Synthesis Engine.*
