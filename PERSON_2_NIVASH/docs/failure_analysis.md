# Empirical OCR & Forensics Failure Analysis
**Person 2 — UPI Transaction Fraud Forensics Platform**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai*

---

## 1. Overview & Forensic Motivation

In payment screenshot analysis, optical character recognition (OCR) and heuristic rule validation will occasionally fail or produce imperfect extractions due to lossy JPEG compression, non-standard fonts, layout collisions, and severe downscaling. 

Documenting these failure modes is essential for:
1. **Explainable AI**: Preventing false confidence in downstream classification decisions.
2. **Viva & Panel Defence**: Proactively explaining boundary conditions and structural trade-offs.
3. **Multi-Modal Ensemble Coordination**: Clarifying why Person 3's visual models (CNN and ELA) must compensate when text-based heuristics lack sufficient confidence.

---

## 2. Documented Failure Case Studies (10 Real Cases)

### Case 1: Currency Symbol OCR Transcription Misread
- **Input Image**: `tpl1_src001_none_01.png` (PayLite Original)
- **Input Problem**: High-DPI rendered Rupee symbol (`₹`) with fine horizontal stroke serifs.
- **Raw OCR Output**: `"%97.29"` (transcribing `₹` as `%`).
- **Correct Ground-Truth**: `₹97.29` (Numeric: `97.29`).
- **Root Cause**: Tesseract English LSTM model lacks native Unicode training weights for standard `₹` glyphs and maps them to ASCII `%` or `*`.
- **System Resolution & Improvement**: `src/ocr/field_parser.py` implements regex prefix normalization `([₹%*tF]|Rs\.?|INR)` to correctly recover the numeric float.

---

### Case 2: Dark-Theme Header Contrast Inversion
- **Input Image**: `tpl2_src021_none_01.png` (QuickPe Original)
- **Input Problem**: White branding text rendered over `#1E2738` dark-blue top container.
- **Raw OCR Output**: `"uciPe"` (missing initial `'Q'`).
- **Correct Ground-Truth**: `QuickPe`.
- **Root Cause**: Tesseract line-finding heuristic struggles with dark background bounding boxes when Otsu binarization inverts local contrast.
- **System Resolution & Improvement**: Fuzzy alias matcher in `field_parser.py` maps `"uciPe"` and `"uclpe"` to `QuickPe`.

---

### Case 3: Recompression Blur on Secondary Timestamps
- **Input Image**: `tpl3_src042_recompress_01.jpg` (UniPay Variant, JPEG Quality 55)
- **Input Problem**: JPEG blocking artifacts around small 11pt timestamps (`14:19`).
- **Raw OCR Output**: `"14:18"` or `None`.
- **Correct Ground-Truth**: `14:19`.
- **Root Cause**: $8\times 8$ discrete cosine transform (DCT) quantization blurs high-frequency vertical stroke lines on small digit fonts.
- **System Resolution & Improvement**: Rule `RULE-05` / `RULE-06` treats missing timestamps as a soft warning (`WARN`) rather than a hard fraud failure (`FAIL`).

---

### Case 4: Asymmetric Canvas Cropping Hiding Header Status
- **Input Image**: `tpl1_src004_crop_01.png` (PayLite Variant, 25px Top/Left Margin Crop)
- **Input Problem**: Top green checkmark and "Paid Successfully" cropped out.
- **Raw OCR Output**: `"Transaction Status: Unknown"`.
- **Correct Ground-Truth**: `Paid Successfully`.
- **Root Cause**: Cropping eliminates structural anchor points used by rule heuristics.
- **System Resolution & Improvement**: Rule `RULE-10` triggers `FAIL` ($w=0.05$), correctly flagging structural truncation as suspicious.

---

### Case 5: Background Splice Infill Color Discontinuity
- **Input Image**: `tpl1_src002_amount_change_01.png` (Tampered Amount)
- **Input Problem**: Background rectangle patched over original amount, overwriting ₹703.94 with ₹35,069.24.
- **Raw OCR Output**: `"₹35,069.24"`.
- **Correct Ground-Truth**: Manipulated value (`synthetic_fake`).
- **Root Cause (Rule Engine Blind Spot)**: The edited amount is syntactically valid ($₹35,069.24 \le ₹1,00,000$). The rule engine sees a clean amount and passes `RULE-01`, `RULE-02`, and `RULE-03`.
- **Ensemble Resolution**: This failure case proves why the Rule Engine alone is insufficient. Subsystem C (Error Level Analysis) detects the high-frequency edge splice boundary, and Subsystem D (CNN) classifies the visual texture.

---

### Case 6: Tampered Alpha-Prefixed Reference Numbers
- **Input Image**: `tpl1_src001_transaction_id_change_04.png` (Manipulated UTR)
- **Input Problem**: Overwritten with `UTR8078673` (8 characters instead of 12 digits).
- **Raw OCR Output**: `"UTR Number: UTR8078673"`.
- **Correct Ground-Truth**: `synthetic_fake`.
- **Root Cause & Rule Detection**: `RULE-08` detects non-numeric characters (`FAIL`), and `RULE-09` detects length mismatch (`FAIL`), raising suspicion score by $+0.25$.
- **System Performance**: **Successful Detection** (True Positive).

---

### Case 7: Future Transaction Timestamps
- **Input Image**: `tpl1_src001_date_change_01.png` (Tampered Date)
- **Input Problem**: Timestamp modified to `28 Dec 2029`.
- **Raw OCR Output**: `"Payment Date: 28 Dec 2029"`, ISO: `2029-12-28`.
- **Correct Ground-Truth**: `synthetic_fake`.
- **Root Cause & Rule Detection**: `RULE-05` compares $T_{\text{txn}} > T_{\text{ref}}$ (17 Sep 2026), triggering maximum penalty ($w=0.25$) and immediate `SUSPICIOUS` verdict.
- **System Performance**: **Successful Detection** (True Positive).

---

### Case 8: Text Infill Overwrite Residual Characters
- **Input Image**: `tpl2_src023_text_insert_02.png` (Fake Stamp Injected)
- **Input Problem**: `"[ AUTHENTICATED BY BANK ]"` stamped across card boundary.
- **Raw OCR Output**: `"[ AUTHENTICATED BY BANK ]"` interleaved between Payee and Amount lines.
- **Correct Ground-Truth**: `synthetic_fake`.
- **Root Cause**: Text injection changes spatial layout flow.
- **System Performance**: Handed off to CNN and ELA for visual pattern anomaly detection.

---

### Case 9: Extreme Bilinear Downscaling (Resize 60%)
- **Input Image**: `tpl3_src045_resize_01.png` (Original Transformed)
- **Input Problem**: Downscaled to 60% and upscaled back to 400×800.
- **Raw OCR Output**: Mean confidence drops from $88.5\%$ to $58.2\%$.
- **Correct Ground-Truth**: `original_transformed` (Benign).
- **Root Cause**: Bilinear interpolation smooths out thin character stems.
- **System Resolution**: `confidence` metric is exported so Person 1's UI displays low OCR confidence rather than asserting absolute certainty.

---

### Case 10: Missing Recipient Field due to Color Infill
- **Input Image**: `tpl1_src005_text_remove_01.png` (Tampered Removal)
- **Input Problem**: Recipient line blanked out with white rectangle.
- **Raw OCR Output**: `recipient = None`.
- **Correct Ground-Truth**: `synthetic_fake`.
- **Root Cause & Rule Detection**: `RULE-11` flags missing recipient entity ($w=0.05$).
- **System Performance**: **Successful Detection** (True Positive).

---

## 3. Systematic Failure Patterns Summary

```
+-----------------------------------------------------------------------------------+
|                        SYSTEMATIC OCR FAILURE PATTERNS                            |
+-----------------------------------------------------------------------------------+
| Pattern 1: Symbol Ambiguity       | ₹ -> %, *, t due to lack of Unicode weights.  |
| Pattern 2: Contrast Inversion     | White text on dark cards inverted by Otsu.    |
| Pattern 3: Quantization Blur      | Low-quality JPEG blocks erasing 11pt time text|
| Pattern 4: Semantic Invariance    | Syntactically valid fake amounts pass rules.  |
| Pattern 5: Resolution Degradation | Bilinear resize lowering LSTM token conf.     |
+-----------------------------------------------------------------------------------+
```

These 5 systematic patterns justify the IDP's **multi-modal architecture**: rules handle syntactic/temporal logic, while ELA and CNN handle pixel and compression forensics.
