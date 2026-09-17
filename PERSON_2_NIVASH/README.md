# Person 2 — Dataset, OCR & Rule Engine Subsystem
**UPI Transaction Fraud Forensics Platform (IDP)**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · 12-Month Academic Project*

---

## 📌 Phase 1 Completed: Foundation, Scaffolding & Template Design Specification

In **Phase 1 of 8**, the foundational architecture, central path manager, configuration system, and comprehensive template design specifications were implemented for Person 2's subsystem.

### What Was Done in Phase 1:

1. **Self-Contained Scaffolding & Directory Layout**:
   - Structured the repository according to the master plan with clear module boundaries (`src/dataset/`, `src/ocr/`, `src/rules/`, `src/utils/`, `data/splits/`, `docs/`, `tests/`).
   - Every package contains appropriate `__init__.py` interface exports.

2. **Central Path Resolution (`src/utils/paths.py`)**:
   - Zero hard-coded absolute paths or fragile relative path concatenations (`../../`).
   - Exposes dynamic path constants (`PROJECT_ROOT`, `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `SPLITS_DIR`, `METADATA_CSV`, `DOCS_DIR`, `TESTS_DIR`, `SRC_DIR`).
   - Includes automatic directory provisioning utility `ensure_dir(path)`.

3. **Central Dataset Configuration (`src/dataset/config.py`)**:
   - Fixed reproducibility seed (`RANDOM_SEED = 42`).
   - Mobile canvas dimensions (`IMAGE_SIZE = (400, 800)`).
   - Fictional, non-branded template identities (`PayLite`, `QuickPe`, `UniPay`) acting as stand-ins for 3 layout families without trademark infringement.
   - 10 planned manipulation categories (`none`, `amount_change`, `date_change`, `transaction_id_change`, `text_insert`, `text_remove`, `font_alter`, `crop`, `resize`, `recompress`).
   - Standard 12-digit UPI reference ID regex constraints and mandatory academic watermark constant.

4. **Complete Template Design Specification (`docs/dataset.md`)**:
   - Comprehensive 10-point architectural specification authored before writing code.
   - Detailed structural comparison of the 3 template families (field order, visual hierarchy, status banners, card containers, date formats).
   - Standardized coordinate anchors and field datatypes for all 8 mandatory fields.
   - Dual-labeling scheme (`original` vs `synthetic_fake` + `edit_type`).
   - Source-grouped naming convention (`tpl{F}_src{NNN}_{edit}_{VV}`) to strictly prevent data leakage across train/val/test splits.
   - Ethical and academic safety statement.

5. **Dependency Management (`requirements.txt`)**:
   - Clean, pinned dependencies with 1-line rationale comments (`pillow`, `opencv-python`, `numpy`, `pandas`, `pytest`, `python-dateutil`).

6. **Documentation Stubs & Verification**:
   - `docs/ocr.md` and `docs/rules.md` stubs pointing to upcoming phases.
   - Unit test suite in `tests/test_paths_config.py` (4/4 passing tests).

---

## 📂 Phase 1 Directory Structure

```
PERSON_2_NIVASH/
├── data/
│   ├── raw/                  # Storage for generated original templates
│   ├── processed/            # Storage for manipulated variants
│   └── splits/               # Train, validation, and test split manifests
├── docs/
│   ├── dataset.md            # Complete 10-point Template Design Specification
│   ├── ocr.md                # Stub for Phases 5–6 (OCR Pipeline)
│   └── rules.md              # Stub for Phase 7 (Rule-Based Validation Engine)
├── src/
│   ├── dataset/
│   │   ├── __init__.py       # Dataset package exports
│   │   └── config.py         # Central dataset constants & manipulation parameters
│   ├── ocr/
│   │   └── __init__.py       # Stub for OCR package
│   ├── rules/
│   │   └── __init__.py       # Stub for Rules package
│   └── utils/
│       ├── __init__.py       # Utility package exports
│       └── paths.py          # Central path resolver & directory manager
├── tests/
│   ├── __init__.py           # Tests package initialization
│   └── test_paths_config.py  # Automated tests for paths & config constants
├── requirements.txt          # Pinned Person 2 dependencies with rationale
└── README.md                 # This Phase 1 Overview & Quickstart Guide
```

---

## 🚀 Verification & Quickstart

To verify the Phase 1 setup locally:

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run Phase 1 automated tests
cd PERSON_2_NIVASH
pytest tests/test_paths_config.py -v

# 3. Test path and configuration imports
python -c "from src.utils.paths import PROJECT_ROOT; print('Root:', PROJECT_ROOT)"
python -c "from src.dataset import config; print('Templates:', config.TEMPLATE_NAMES)"
```

---

## 🛡️ Academic & Legal Safety Rules
- **No Real Brand Names**: Uses purely fictional standalone template layouts (`PayLite`, `QuickPe`, `UniPay`).
- **Zero Sensitive Data**: No real bank accounts, real UTRs, phone numbers, or private financial ledgers.
- **Mandatory Watermark**: `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` on every generated asset.
- **Detector Purpose Only**: Designed solely to train and evaluate fraud forensics detectors; not intended to produce usable payment evidence.
