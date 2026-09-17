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
| **Phase 3** | Controlled Manipulation Engine & Labeled Metadata | **Completed (100%)** | [`PHASE_3_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_3_README.md) |
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
│   ├── processed/            # 240 controlled manipulated variants
│   ├── splits/               # Train, validation, and test split manifests (Phase 4)
│   ├── ground_truth.csv      # 300 reference ground-truth records (Phases 2 & 3)
│   └── metadata.csv          # 300 master labeled metadata index (Phase 3)
├── docs/
│   ├── dataset.md            # Complete 11-point Template Design & Generation Specification
│   ├── ocr.md                # Stub for Phases 5–6 (OCR Pipeline)
│   ├── rules.md              # Stub for Phase 7 (Rule-Based Validation Engine)
│   └── samples/              # Committed sample receipts (Originals + Manipulations)
│       ├── sample_family1_paylite.png
│       ├── sample_family2_quickpe.png
│       ├── sample_family3_unipay.png
│       ├── sample_amount_change_after.png
│       ├── sample_date_change_after.png
│       └── sample_recompress_after.png
├── src/
│   ├── dataset/
│   │   ├── __init__.py       # Package exports (templates, manipulators, auditor)
│   │   ├── config.py         # Central dataset constants & manipulation parameters
│   │   ├── templates.py      # Template synthesis engine for 3 layout families
│   │   ├── manipulate.py     # Controlled manipulation engine (9 edit types)
│   │   └── audit.py          # Dataset sanity auditor verifying CSV & disk integrity
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
│   ├── test_templates.py     # Template generator unit tests (Phase 2)
│   └── test_manipulate.py    # Manipulation engine & audit unit tests (Phase 3)
├── requirements.txt          # Pinned Person 2 dependencies with rationale
├── PHASE_1_README.md         # Phase 1 Summary & Documentation
├── PHASE_2_README.md         # Phase 2 Summary & Documentation
├── PHASE_3_README.md         # Phase 3 Summary & Documentation
└── README.md                 # This Person 2 Overview & Phase Progress Dashboard
```

---

## 🚀 Execution & Quickstart

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run Person 2 unit tests (12/12 passing)
cd PERSON_2_NIVASH
pytest tests/ -v

# 3. Run dataset sanity audit
python -m src.dataset.audit

# 4. Regenerate manipulated dataset (Seed: 42)
python -m src.dataset.manipulate --variants-per-original 4 --samples
```

---

## 🛡️ Academic & Legal Safety Rules
- **No Real Brand Names**: Uses purely fictional standalone template layouts (`PayLite`, `QuickPe`, `UniPay`).
- **Zero Sensitive Data**: No real bank accounts, real UTRs, phone numbers, or private financial ledgers.
- **Mandatory Watermark**: `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` on every generated asset.
- **Detector Purpose Only**: Designed solely to train and evaluate fraud forensics detectors; not intended to produce usable payment evidence.
