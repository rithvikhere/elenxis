# Person 2 — Dataset, OCR & Rule Engine Subsystem
**UPI Transaction Fraud Forensics Platform (IDP)**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · 12-Month Academic Project*

---

## 📌 Subsystem Overview & Phase Progress

Person 2 owns and delivers the complete foundational data generation, leakage-safe dataset partitioning, optical character recognition (OCR), transaction field extraction, and heuristic rule-based consistency validation modules.

### Phase Progress Dashboard (All 8 Phases Complete)

| Phase | Title | Status | Documentation |
|:---:|:---|:---:|:---|
| **Phase 1** | Foundation, Scaffolding & Template Design Spec | **Completed (100%)** | [`PHASE_1_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_1_README.md) |
| **Phase 2** | Template Synthesis Engine — Generating the Originals | **Completed (100%)** | [`PHASE_2_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_2_README.md) |
| **Phase 3** | Controlled Manipulation Engine & Labeled Metadata | **Completed (100%)** | [`PHASE_3_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_3_README.md) |
| **Phase 4** | Leakage-Safe Splitting, Integrity Audit & Dataset Docs | **Completed (100%)** | [`PHASE_4_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_4_README.md) |
| **Phase 5** | Image Preprocessing & OCR Engine Selection | **Completed (100%)** | [`PHASE_5_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_5_README.md) |
| **Phase 6** | Field Extraction & Parser Heuristics | **Completed (100%)** | [`PHASE_6_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_6_README.md) |
| **Phase 7** | Rule-Based Validation Engine & Anomaly Formulation | **Completed (100%)** | [`PHASE_7_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_7_README.md) |
| **Phase 8** | Empirical Benchmarking & Review Deliverables | **Completed (100%)** | [`PHASE_8_README.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/PHASE_8_README.md) |

---

## 📂 Subsystem Directory Structure

```
PERSON_2_NIVASH/
├── data/
│   ├── raw/                  # 60 synthesized original receipt images
│   ├── processed/            # 240 controlled manipulated variants
│   ├── splits/               # Train, validation, and test split manifests (Phase 4)
│   │   ├── train.csv         # 210 images (42 sources, 70.0%)
│   │   ├── val.csv           # 45 images (9 sources, 15.0%)
│   │   └── test.csv          # 45 images (9 sources, 15.0%)
│   ├── ground_truth.csv      # 300 reference ground-truth records (Phases 2 & 3)
│   └── metadata.csv          # 300 master labeled metadata index (Phase 3)
├── docs/
│   ├── dataset.md            # Complete 12-section Dataset & Forensic Design Specification
│   ├── handoff_dataset.md    # Dedicated dataset handoff guide for Person 3 (CNN models)
│   ├── ocr.md                # Complete OCR engine selection, preprocessing & benchmarks
│   ├── rules.md              # Complete Rule-based validation catalogue & anomaly math
│   └── samples/              # Committed sample receipts (Originals + Manipulations)
│       ├── sample_family1_paylite.png
│       ├── sample_family2_quickpe.png
│       ├── sample_family3_unipay.png
│       ├── sample_amount_change_after.png
│       ├── sample_date_change_after.png
│       ├── sample_recompress_after.png
│       └── preprocessing_comparison.png
├── results/
│   └── metrics/
│       ├── dataset_audit.txt              # 11-point leakage audit verification report
│       ├── ocr_preprocessing_benchmark.txt # 6-mode OCR preprocessing benchmark report
│       ├── rule_engine_benchmark.txt      # 300-image rule validation benchmark report
│       └── person2_master_summary.txt      # Consolidated executive review summary
├── src/
│   ├── dataset/
│   │   ├── __init__.py       # Package exports (templates, manipulators, splitter, auditor)
│   │   ├── config.py         # Central dataset constants & manipulation parameters
│   │   ├── templates.py      # Template synthesis engine for 3 layout families
│   │   ├── manipulate.py     # Controlled manipulation engine (9 edit types)
│   │   ├── split.py          # Group-aware dataset splitter stratified by template_family
│   │   └── audit.py          # 11-point dataset integrity & leakage auditor (dHash)
│   ├── ocr/
│   │   ├── __init__.py       # OCR package exports (extractor, preprocessor, parser)
│   │   ├── preprocess.py     # 6 image preprocessing filters (contrast boost, etc.)
│   │   ├── extractor.py      # Master OCR transaction field extraction pipeline
│   │   ├── field_parser.py   # Regex parsing and normalization heuristics
│   │   └── benchmark.py      # Preprocessing benchmark runner across ground truth
│   ├── rules/
│   │   ├── __init__.py       # Rules package exports (validators, rule engine)
│   │   ├── validators.py     # 11 atomic consistency validators (dates, amounts, UTRs)
│   │   ├── rule_engine.py    # Weighted suspicion scoring and tri-state verdict engine
│   │   └── benchmark.py      # Rule engine benchmark runner on 300-image dataset
│   ├── utils/
│   │   ├── __init__.py       # Utility package exports
│   │   └── paths.py          # Central path resolver & directory manager
│   └── benchmark_master.py   # Master executive benchmark runner across all subsystems
├── tests/
│   ├── __init__.py           # Tests package initialization
│   ├── test_paths_config.py  # Path & configuration unit tests (4 tests)
│   ├── test_templates.py     # Template generator unit tests (5 tests)
│   ├── test_manipulate.py    # Manipulation engine & audit unit tests (3 tests)
│   ├── test_dataset.py       # Dataset 300-image integrity & schema unit tests (7 tests)
│   ├── test_split.py         # Group disjointness, stratification & reproducibility (7 tests)
│   ├── test_preprocess.py    # Image loader & 6 preprocessing filters unit tests (17 tests)
│   ├── test_ocr_extractor.py # OCR extraction on 3 layouts & edge cases (7 tests)
│   ├── test_field_parser.py  # Field parsing heuristics & currency normalizers (27 tests)
│   └── test_rules.py         # 11 validators & rule engine integration unit tests (22 tests)
├── requirements.txt          # Pinned Person 2 dependencies with rationale
├── PHASE_1_README.md         # Phase 1 Summary & Documentation
├── PHASE_2_README.md         # Phase 2 Summary & Documentation
├── PHASE_3_README.md         # Phase 3 Summary & Documentation
├── PHASE_4_README.md         # Phase 4 Summary & Documentation
├── PHASE_5_README.md         # Phase 5 Summary & Documentation
├── PHASE_6_README.md         # Phase 6 Summary & Documentation
├── PHASE_7_README.md         # Phase 7 Summary & Documentation
├── PHASE_8_README.md         # Phase 8 Summary & Documentation
└── README.md                 # Master Person 2 Overview & Phase Progress Dashboard
```

---

## 🚀 Execution & Quickstart

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run Person 2 unit tests (99/99 passing across all modules)
cd PERSON_2_NIVASH
pytest tests/ -v

# 3. Run master executive benchmark suite
python -m src.benchmark_master
```

---

## 🛡️ Academic & Legal Safety Rules
- **No Real Brand Names**: Uses purely fictional standalone template layouts (`PayLite`, `QuickPe`, `UniPay`).
- **Zero Sensitive Data**: No real bank accounts, real UTRs, phone numbers, or private financial ledgers.
- **Mandatory Watermark**: `DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` on every generated asset.
- **Detector Purpose Only**: Designed solely to train and evaluate fraud forensics detectors; not intended to produce usable payment evidence.
