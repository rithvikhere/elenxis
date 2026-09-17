# Person 2 — Dataset, OCR & Rule Engine Subsystem
**UPI Transaction Fraud Forensics Platform (IDP)**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · 12-Month Academic Project*

---

## 📌 Subsystem Overview & Phase Progress

Person 2 is responsible for the foundational data generation, optical character recognition (OCR), and heuristic rule-based consistency validation modules.

### Phase Progress Dashboard

| Phase | Title | Status | Documentation |
|:---:|:---|:---:|:---|
| **Phase 1** | Foundation, Scaffolding & Template Design Spec | **Completed (100%)** | [`PHASE_1_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_1_README.md) |
| **Phase 2** | Template Synthesis Engine — Generating the Originals | **Completed (100%)** | [`PHASE_2_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_2_README.md) |
| **Phase 3** | Manipulation Engine & Ground-Truth Metadata Creation | *Pending* | `PHASE_3_README.md` |
| **Phase 4** | Leakage-Free Dataset Splitting & Verification | *Pending* | `PHASE_4_README.md` |
| **Phase 5** | Image Preprocessing & OCR Engine Selection | *Pending* | `PHASE_5_README.md` |
| **Phase 6** | Field Extraction & Parser Heuristics | *Pending* | `PHASE_6_README.md` |
| **Phase 7** | Rule-Based Validation Engine & Anomaly Formulation | *Pending* | `PHASE_7_README.md` |
| **Phase 8** | Empirical Benchmarking & Review Deliverables | *Pending* | `PHASE_8_README.md` |

---

## 📂 Subsystem Directory Structure

```
PERSON_2_NIVASH/
├── data/
│   ├── raw/                  # 60 synthesized original receipt images
│   ├── processed/            # Manipulated variants (Phase 3)
│   ├── splits/               # Train, validation, and test split manifests (Phase 4)
│   └── ground_truth.csv      # 60 reference ground-truth records (Phase 2)
├── docs/
│   ├── dataset.md            # Complete 10-point Template Design Specification
│   ├── ocr.md                # Stub for Phases 5–6 (OCR Pipeline)
│   ├── rules.md              # Stub for Phase 7 (Rule-Based Validation Engine)
│   └── samples/              # Committed sample receipts (1 per layout family)
│       ├── sample_family1_paylite.png
│       ├── sample_family2_quickpe.png
│       └── sample_family3_unipay.png
├── src/
│   ├── dataset/
│   │   ├── __init__.py       # Package exports (templates, generators)
│   │   ├── config.py         # Central dataset constants & manipulation parameters
│   │   └── templates.py      # Template synthesis engine for 3 layout families
│   ├── ocr/
│   │   └── __init__.py       # Stub for OCR package
│   ├── rules/
│   │   └── __init__.py       # Stub for Rules package
│   └── utils/
│       ├── __init__.py       # Utility package exports
│       └── paths.py          # Central path resolver & directory manager
├── tests/
│   ├── __init__.py           # Tests package initialization
│   ├── test_paths_config.py  # Path & configuration unit tests (Phase 1)
│   └── test_templates.py     # Template generator & renderer unit tests (Phase 2)
├── requirements.txt          # Pinned Person 2 dependencies with rationale
├── PHASE_1_README.md         # Phase 1 Summary & Documentation
├── PHASE_2_README.md         # Phase 2 Summary & Documentation
└── README.md                 # This Person 2 Overview & Phase Progress Dashboard
```

---

## 🚀 Execution & Quickstart

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run Person 2 unit tests (9/9 passing)
cd PERSON_2_NIVASH
pytest tests/ -v

# 3. Regenerate synthetic original receipts (Seed: 42)
python -m src.dataset.templates --count 60 --samples
```

---

## 🛡️ Academic & Legal Safety Rules
- **No Real Brand Names**: Uses purely fictional standalone template layouts (`PayLite`, `QuickPe`, `UniPay`).
- **Zero Sensitive Data**: No real bank accounts, real UTRs, phone numbers, or private financial ledgers.
- **Mandatory Watermark**: `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` on every generated asset.
- **Detector Purpose Only**: Designed solely to train and evaluate fraud forensics detectors; not intended to produce usable payment evidence.
