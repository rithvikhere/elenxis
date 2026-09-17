# OCR Pipeline Documentation
**Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP)**

---

## 1. Executive Summary & Architectural Scope

The Optical Character Recognition (OCR) pipeline is responsible for transcribing unstructured UPI payment receipt images into clean, structured key-value transaction metadata (`amount`, `date`, `time`, `transaction_id` / UTR, `app_template`, `recipient`).

```
+------------------+     +-------------------+     +-------------------------+
| Raw Receipt      | --> | Preprocessing     | --> | Tesseract OCR (PSM 3)   |
| (PNG / JPEG)     |     | (Contrast/Binar.) |     | TSV Character / Box Map |
+------------------+     +-------------------+     +-------------------------+
                                                                |
                                                                v
+------------------+     +-------------------+     +-------------------------+
| Structured Dict  | <-- | Field Parser      | <-- | Raw Text & Word-Level   |
| & Mean Conf.     |     | (Regex + Heur.)   |     | Confidence Extraction   |
+------------------+     +-------------------+     +-------------------------+
```

---

## 2. OCR Engine Selection: Tesseract OCR

| Dimension | Tesseract OCR (v5.5+) | EasyOCR / TrOCR / PaddleOCR | Decision Rationale |
|:---|:---|:---|:---|
| **Inference Latency** | **~60–110 ms** per receipt on CPU | 800–2500 ms (CPU) / requires GPU | Tesseract enables sub-second real-time verification without GPU dependencies. |
| **Footprint / Dependencies** | Lightweight native C++ binary + `pytesseract` binding | Heavy PyTorch / CUDA runtime (~2.5 GB) | Standardized deployment across consumer laptops for project evaluation. |
| **Page Segmentation Flexibility** | Fine-grained PSM control (PSM 3, PSM 6, PSM 11) | Bounding box clustering only | PSM 3 auto-detects variable font hierarchies (large centered amount vs small reference text). |
| **Deterministic Behavior** | Completely deterministic across environments | Minor floating point variation across PyTorch backends | Essential for reproducible academic evaluation and unit testing. |

---

## 3. Preprocessing Pipeline

UPI receipts captured via mobile screenshots or camera exports suffer from low-contrast background gradients, anti-aliased font edges, and compression noise.

Four preprocessing modes are implemented in `src/ocr/preprocess.py`:

```python
from src.ocr.preprocess import preprocess_image

# 1. Contrast Enhancement (Default)
img_enhanced = preprocess_image(raw_img, mode="contrast")

# 2. Adaptive Binarization (Otsu-style Gaussian Thresholding)
img_binary = preprocess_image(raw_img, mode="adaptive_thresh")

# 3. Grayscale Only
img_gray = preprocess_image(raw_img, mode="grayscale")

# 4. Median Denoise
img_denoised = preprocess_image(raw_img, mode="denoise")
```

### Preprocessing Comparison Matrix

| Preprocessing Mode | Mean OCR Confidence | Best Used For |
|:---|:---|:---|
| `contrast` (**Default**) | **89.4%** | General clean mobile screenshots, light gradient backgrounds |
| `adaptive_thresh` | **86.1%** | Receipts with complex background patterns or uneven lighting |
| `grayscale` | **83.7%** | Fast baseline processing with minimal CPU overhead |
| `denoise` | **85.2%** | Compressed JPEG images with high-frequency quantization artifacts |

---

## 4. Page Segmentation Modes (PSM) Optimization

Early baseline implementations using **PSM 6** (Assume a single uniform block of text) frequently missed the large, centered amount header (e.g., `₹450.00`) because Tesseract assumed single-column text flow.

Switching to **PSM 3** (Fully automatic page segmentation without OSD) enables the layout engine to split the image into independent logical regions:
1. Top branding header (`ApexPay`, `ZenithUPI`, `NovaPay`)
2. Centered large hero amount
3. Multi-line transaction details block (Date, Time, Recipient, UTR)

---

## 5. Field Parser Logic & Resilience Strategies

The parser (`src/ocr/field_parser.py`) applies resilient regular expressions and post-OCR correction heuristics:

| Target Field | Common OCR Artifacts / Misreads | Normalization & Parsing Strategy |
|:---|:---|:---|
| **Amount** | `₹` misread as `%`, `t`, `*`, `z`, `Rs` | Strips currency prefixes, standardizes comma separators (`1,200.00` -> `1200.00`), extracts positive floats. |
| **Date** | `O` instead of `0`, missing spaces | Dual parsing: Named months (`12 Mar 2026`) and ISO format (`2026-03-12`), converts to `YYYY-MM-DD`. |
| **Time** | `AM`/`PM` spacing or omitted colon | Supports both 12-hour (`10:15 AM`) and 24-hour (`14:30`) timestamp formats. |
| **UTR / Txn ID** | `O` vs `0`, `I` vs `1`, `UTR` prefix attached | Extracts 12-digit numeric sequences following labels like `UPI Ref`, `UTR`, `Txn ID`. |
| **Template** | Lowercase or slightly blurred logo text | Fuzzy token matching against supported template identifiers (`ApexPay`, `ZenithUPI`, `NovaPay`). |

---

## 6. Empirical Evaluation Results (Measured on Ground Truth)

Evaluation run across all 60 synthetic receipts and the held-out test split (12 images) via `scripts/evaluate_ocr_rules.py`:

### Field Extraction Accuracy

| Dataset Split | Sample Count | OCR Extraction Rate | Amount Accuracy | Date Accuracy | UTR / Txn ID Accuracy |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Test Split (Held-out)** | **12** | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Validation Split** | **12** | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Train Split** | **36** | **100.0%** | **80.6%** | **100.0%** | **94.4%** |
| **Full Dataset** | **60** | **100.0%** | **88.3%** | **100.0%** | **96.7%** |

---

## 7. Documented Failure Modes & Mitigations

| Failure Mode ID | Observed Failure Symptom | Underlying Root Cause | Implemented Mitigation |
|:---:|:---|:---|:---|
| **FM-01** | Currency symbol `₹` read as `%` or `t` | Font glyph anti-aliasing on custom typography | Prefix normalization regex matches `[₹%t*]`, stripping leading artifact before decimal validation. |
| **FM-02** | 12-digit UTR truncated if line wrapped | Tight bounding box margins in template rendering | Lookaround regex capturing numeric runs of 12 digits across adjacent lines. |
| **FM-03** | Amount parsed as integer instead of 2 decimals | Zeroes merged during binarization | Field parser standardizes amount string with `.00` formatting if decimal point is absent. |
| **FM-04** | OCR confidence drop on small footer fonts | Font size < 10pt with sub-pixel blurring | Dynamic image upscale factor (1.5x) applied in preprocessing for small dimensions. |

---

## 8. Integration Contract (Public API)

```python
from src.ocr import extract_transaction_fields

result = extract_transaction_fields("data/raw/img_001.png", preprocess_mode="contrast")

# Output Schema:
# {
#     "success": True,
#     "mean_confidence": 92.4,
#     "fields": {
#         "amount": "450.00",
#         "amount_val": 450.0,
#         "date": "2026-03-12",
#         "time": "10:15 AM",
#         "transaction_id": "425631219101",
#         "app_template": "ApexPay",
#         "recipient": "Apex Mart"
#     },
#     "raw_text": "...",
#     "word_confidences": [...]
# }
```
