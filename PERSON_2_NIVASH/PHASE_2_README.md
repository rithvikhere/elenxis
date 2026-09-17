# Phase 2: Template Synthesis Engine — Generating the Originals
**Person 2 Subsystem — UPI Transaction Fraud Forensics Platform**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic IDP Project*

---

## 📌 Phase Overview & Objectives

Phase 2 implements the **Template Synthesis Engine** (`src/dataset/templates.py`), capable of rendering reproducible, high-fidelity, unmanipulated payment receipts across 3 structurally distinct layout families (`PayLite`, `QuickPe`, `UniPay`). It generates the reference ground-truth answer key (`data/ground_truth.csv`) that future OCR extraction phases benchmark against.

### Key Goals Accomplished:
- [x] Implemented randomized fictional field generator with Indian Rupee currency formatting (`₹`), past timestamps, and valid 12-digit UTRs.
- [x] Created 3 structurally distinct PIL layout renderers (`PayLite`, `QuickPe`, `UniPay`).
- [x] Verified non-overlapping placement of the mandatory `DEMO / SYNTHETIC` watermark.
- [x] Implemented deterministic batch orchestrator (`generate_originals`) and CLI entry point.
- [x] Exported ground-truth reference dataset in `data/ground_truth.csv`.
- [x] Exported 3 committed visual samples into `docs/samples/`.
- [x] Created unit test suite in `tests/test_templates.py` (5/5 passing tests; 9/9 across all phases).

---

## 🎨 Layout Families Architecture

```
+---------------------------+  +---------------------------+  +---------------------------+
|    Family 1: PayLite      |  |    Family 2: QuickPe      |  |     Family 3: UniPay      |
| (Top Brand + Center Hero) |  | (Card Container + Stack)  |  | (Minimalist Clean Header) |
+---------------------------+  +---------------------------+  +---------------------------+
| [Header Banner - Blue]    |  | [Dark Theme Background]   |  | [White Clean Minimalist]  |
| App Name: PayLite         |  | App Name: QuickPe         |  | App Name: UniPay          |
|                           |  |                           |  |                           |
|       (Checkmark)         |  | +-----------------------+ |  |  Status: SUCCESS          |
|    Paid Successfully      |  | | Paid to: [Recipient]  | |  |  Amount: ₹[Hero Amount]  |
|                           |  | | Amount:  ₹[Amount]    | |  |                           |
|       ₹450.00             |  | +-----------------------+ |  |  Txn Details:             |
|    (Hero Text 36pt)       |  |                           |  |  • Paid To:  [Recipient]  |
|                           |  | Txn Details:              |  |  • Ref No:   [12-Digit]   |
| To: [Recipient]           |  | • Date:   12 Mar 2026     |  |  • Timestamp: 10:15 AM    |
| Date: 12 Mar 2026         |  | • Time:   10:15 AM        |  |  • Date:     2026-03-12   |
| Time: 10:15 AM            |  | • Ref No: 425631219101    |  |                           |
| Ref: 425631219101         |  |                           |  | [Footer Watermark]        |
|                           |  | [Footer Watermark]        |  |                           |
| [Footer Watermark]        |  +---------------------------+  +---------------------------+
+---------------------------+
```

| Dimension | Family 1 (`PayLite`) | Family 2 (`QuickPe`) | Family 3 (`UniPay`) |
|:---|:---|:---|:---|
| **Visual Palette** | Flat Primary Blue (`#1A73E8`) on Light | Deep Slate Dark Theme (`#121824` / `#1E2738`) | Minimalist Clean Off-White (`#FAFAFA`) |
| **Hero Amount** | Large centered hero typography (34pt) | Highlighted Cyan typography inside top card | Left-aligned bold sub-header typography |
| **Date Syntax** | Textual Month: `12 Mar 2026` | Hyphenated: `12-03-2026` | ISO 8601: `2026-03-12` |
| **UTR Label** | `UPI Ref (UTR)` | `Reference ID (UTR)` | `Bank Ref (UTR)` |
| **Status Badge** | Circular Green Checkmark Badge | Pill Badge `[✓ COMPLETED]` | Clean Rectangle `[ SUCCESS ]` |

---

## 📂 Phase 2 Artifacts & Deliverables

| Component | File Path | Description |
|:---|:---|:---|
| **Synthesis Engine** | [`src/dataset/templates.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/templates.py) | Full rendering engine with field generator, 3 layout functions, batch orchestrator, and CLI runner. |
| **Dataset Init** | [`src/dataset/__init__.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/dataset/__init__.py) | Exports `generate_originals`, `generate_fictional_record`, and `RENDERERS`. |
| **Ground-Truth CSV** | [`data/ground_truth.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/ground_truth.csv) | Reference answer key with 60 ground-truth records across all generated originals. |
| **Sample Images** | `docs/samples/` | 3 representative sample images: `sample_family1_paylite.png`, `sample_family2_quickpe.png`, `sample_family3_unipay.png`. |
| **Design Doc Update** | [`docs/dataset.md`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/docs/dataset.md) | Added Section 9 "Generation — Originals" documenting actual measured counts and reproduction parameters. |
| **Unit Test Suite** | [`tests/test_templates.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/tests/test_templates.py) | 5 unit tests verifying INR amount formatting, record fields, renderer output sizes, byte-level determinism, and ground-truth consistency. |

---

## 🚀 Execution & Verification Commands

### 1. Run Unit Tests (9 passing tests across Phase 1 & 2)
```bash
cd PERSON_2_NIVASH
pytest tests/ -v
```

### 2. Regenerate Originals CLI
```bash
python -m src.dataset.templates --count 60 --samples
```

---

## 📊 Empirical Generation Summary

- **Total Original Receipts Generated**: `60`
- **Family 1 (`PayLite`)**: `20 images` (`tpl1_src001_none_01.png` to `tpl1_src020_none_01.png`)
- **Family 2 (`QuickPe`)**: `20 images` (`tpl2_src021_none_01.png` to `tpl2_src040_none_01.png`)
- **Family 3 (`UniPay`)**: `20 images` (`tpl3_src041_none_01.png` to `tpl3_src060_none_01.png`)
- **Byte Determinism**: Seed 42 verified with byte-level matching across consecutive runs.

---
*Phase 2 is complete and verified. Standing by for Phase 3: Programmatic Manipulation Engine.*
