# Phase 6: Field Extraction & Parser Heuristics
**Person 2 Subsystem — UPI Transaction Fraud Forensics Platform**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic IDP Project*

---

## 📌 Phase Overview & Objectives

Phase 6 implements the **Transaction Field Parser & Semantic Normalizer** (`src/ocr/field_parser.py`). It converts raw, unstructured Tesseract character streams into clean, structured dictionaries with standardized datatypes, regex parsing heuristics, and noise-tolerant normalization.

### Key Deliverables Accomplished:
- [x] **Amount Extraction with OCR Artifact Recovery**: Recovers values with currency indicators (`₹`, `Rs.`, `INR`) and common Tesseract misreads (`%`, `*`, `t`, `F`). Supports comma-separated thousands (`₹12,967.28`) and float coercion.
- [x] **Multi-Syntax Date Parser**: Supports textual months (`12 Mar 2026`), ISO formats (`2026-03-12`), slash/dashed formats (`02-10-2025`), outputting standardized ISO `YYYY-MM-DD` strings.
- [x] **Timestamp Extraction**: Captures 12-hour AM/PM and 24-hour time expressions.
- [x] **UTR / Reference Key Parsing**: Extracts 12-digit standard NPCI references and captures tampered alphanumeric values (`UTR8078673`).
- [x] **Template Layout Recognition**: Accurately maps `PayLite`, `QuickPe`, and `UniPay` layouts from header tokens.
- [x] **Payee & Transaction Status Parsing**: Extracts recipient names and status keywords (`Paid Successfully`, `SUCCESS`, `Payment Completed`).
- [x] **Unit Tests**: Full unit test suite in `tests/test_field_parser.py` (27/27 tests passing).

---

## 🔬 Parser Heuristics & Schema Mapping

```
+---------------------------+
| Raw Tesseract OCR Stream  |
+---------------------------+
              |
              v
+-------------------------------------------------------------+
|               Field Parser Heuristic Pipeline               |
+-------------------------------------------------------------+
| • Amount Normalizer    : Regex ([₹%*tF]|Rs) + Comma Removal |
| • Date Standardizer    : Multi-Format Matcher -> ISO-8601   |
| • Timestamp Parser     : 12h (AM/PM) / 24h Extraction       |
| • UTR / Ref Parser     : 12-Digit & Alphanumeric Sieve      |
| • Template Classifier  : Layout Keyword Signature Detector  |
| • Payee & Status Sieve : Entity Dictionary & Prefix Matcher |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
| Structured Output Dictionary (Consumable by Rule Engine)    |
+-------------------------------------------------------------+
```

---

## 📂 Phase 6 Artifacts & Deliverables

| Component | File Path | Description |
|:---|:---|:---|
| **Field Parser** | [`src/ocr/field_parser.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/ocr/field_parser.py) | Complete regex parsing and normalization heuristics. |
| **OCR Pipeline Init** | [`src/ocr/__init__.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/src/ocr/__init__.py) | Exports `extract_transaction_fields`, `parse_all_fields`. |
| **Unit Tests** | [`tests/test_field_parser.py`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/tests/test_field_parser.py) | Comprehensive test suite for all field parsers and edge cases. |

---

## 🚀 Verification Commands

```bash
cd PERSON_2_NIVASH
pytest tests/test_field_parser.py -v
```
