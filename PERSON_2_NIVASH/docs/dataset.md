# Complete Dataset & Forensics Specification
**Person 2 — UPI Transaction Fraud Forensics Platform**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai*

---

## 1. Why Synthetic? Why Fictional? Ethics Statement

### Motivation & Privacy Imperative
In payment receipt forensics, **no publicly available, labeled ground-truth dataset** of real vs. manipulated UPI payment screenshots exists due to banking confidentiality, KYC compliance, and PII protection regulations (IT Act 2000, GDPR, RBI privacy mandates). Online receipts scraped from social media or search engines contain unknown manipulation histories, low-resolution artifacts, and personal data.

To overcome this constraint without violating user privacy, our platform introduces a **controlled, parametric synthetic dataset generator**. Synthesizing images from clean mathematical primitives allows exact, pixel-accurate ground-truth tracking for every text bounding box, amount, timestamp, and reference number.

### Fictional Standing & Trademark Ethics
To adhere strictly to academic integrity and trademark law:
- **Zero Real-World Trademarks**: We construct three fictional stand-in payment application identities: `PayLite`, `QuickPe`, and `UniPay`.
- **Fictional Data Only**: All transaction amounts, dates, timestamps, 12-digit UTRs, and recipient names are generated pseudo-randomly from controlled synthetic distributions.
- **Detector-Only Purpose**: Synthetic receipts are generated exclusively to train and benchmark forensic tamper detectors and rule engines. Every image embeds a visible footer watermark:
  ```
  DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY
  ```

---

## 2. Template Layout Families & Structural Variations

To ensure downstream CNN and OCR models do not overfit to a single visual layout, we designed **three structurally distinct layout families**:

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

### Structural Comparison Matrix

| Layout Dimension | Family 1: `PayLite` | Family 2: `QuickPe` | Family 3: `UniPay` |
|:---|:---|:---|:---|
| **Visual Architecture** | Top Primary Blue Banner (`#1A73E8`) | Elevated Floating Card on Dark BG (`#1E2738`) | Clean Minimalist Two-Tone Grid (`#FAFAFA`) |
| **Hero Amount Position** | Centered hero typography ($y \approx 215\text{px}$) | Inside top floating container ($y \approx 170\text{px}$) | Left-aligned bold subheader ($y \approx 105\text{px}$) |
| **Date & Time Syntax** | Textual month (`12 Mar 2026, 10:15 AM`) | Compact inline (`12-03-2026, 10:15 AM`) | ISO format (`2026-03-12, 10:15`) |
| **UTR / Reference Key** | `UPI Ref (UTR)` | `Reference ID (UTR)` | `Bank Ref (UTR)` |
| **Confirmation Badge** | Green circular checkmark glyph | Pill badge: `[✓ COMPLETED]` | Bordered badge: `[ SUCCESS ]` |
| **Canvas Dimensions** | 400 × 800 pixels | 400 × 800 pixels | 400 × 800 pixels |

---

## 3. Label Taxonomy & Tri-State Classification Semantics

Our metadata schema enforces a rigorous tri-state label taxonomy in `data/metadata.csv` and split manifests:

1. **`original`** ($N=60$):
   - Untouched, lossless PNG renders from the template synthesis engine. Represents ground-truth clean financial transactions.
2. **`original_transformed`** ($N=46$):
   - Screenshots subjected to benign transformations (`resize` down/upscaling or `recompress` JPEG degradation) **without content tampering**.
   - **Crucial Scientific Rationale**: Real-world payment receipts are routinely shared via WhatsApp, Telegram, or email, introducing compression artifacts. If benign channel transformations were labeled as `synthetic_fake`, machine learning models would overfit to high-frequency compression noise rather than semantic forgery. This label allows training models to distinguish benign channel noise from fraudulent tampering.
3. **`synthetic_fake`** ($N=194$):
   - Maliciously manipulated receipts exhibiting semantic, visual, or structural tampering (`amount_change`, `date_change`, `transaction_id_change`, `text_insert`, `text_remove`, `font_alter`, `crop`).

---

## 4. Manipulation Categories & Forensic Artifacts

| # | `edit_type` | Label Class | Forensic Mechanism & Visual Indicator |
|:---:|:---|:---:|:---|
| 1 | `none` | `original` | Clean pristine baseline image. |
| 2 | `amount_change` | `synthetic_fake` | Patches background over transaction value and overwrites with modified amount, creating edge splice discontinuities. |
| 3 | `date_change` | `synthetic_fake` | Overwrites timestamp (50% future dates), creating temporal rule violations and bounding box misalignments. |
| 4 | `transaction_id_change` | `synthetic_fake` | Overwrites 12-digit UTR with alphabetic prefixes or invalid lengths, violating NPCI format standards. |
| 5 | `text_insert` | `synthetic_fake` | Injects artificial validation stamps (e.g. `[ AUTHENTICATED BY BANK ]`) into empty canvas areas. |
| 6 | `text_remove` | `synthetic_fake` | Blanks out mandatory fields (e.g. recipient or UTR) using local background color infill. |
| 7 | `font_alter` | `synthetic_fake` | Re-renders legitimate field text using inconsistent font weights, point sizes, or vertical baselines. |
| 8 | `crop` | `synthetic_fake` | Crops canvas asymmetrically (10–30px) to simulate intentional UI framing mutilation. |
| 9 | `resize` | `original_transformed` | Downscales to 60–80% and bilinearly upscales back to 400×800 canvas (content unaltered). |
| 10 | `recompress` | `original_transformed` | Saves with JPEG quality factor 50–70 to test Error Level Analysis (ELA) sensitivity without content changes. |

---

## 5. Dataset Statistics & Actual Realized Counts

### Overall Dataset Distribution ($N = 300$)
- **Total Images**: **300**
- **Original Source Templates**: **60**
- **Manipulated Variants**: **240** (exactly 4 variants per original source)

### Actual Counts by Split Manifest

| Manifest Split | Total Images | Total Sources | `original` | `original_transformed` | `synthetic_fake` | Realized Ratio |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **TRAIN** (`train.csv`) | 210 | 42 | 42 (20.0%) | 30 (14.3%) | 138 (65.7%) | **70.0%** |
| **VAL** (`val.csv`) | 45 | 9 | 9 (20.0%) | 13 (28.9%) | 23 (51.1%) | **15.0%** |
| **TEST** (`test.csv`) | 45 | 9 | 9 (20.0%) | 3 (6.7%) | 33 (73.3%) | **15.0%** |
| **TOTAL** | **300** | **60** | **60 (20.0%)** | **46 (15.3%)** | **194 (64.7%)** | **100.0%** |

### Actual Counts by Template Family

| Template Family | Name | Train Images | Val Images | Test Images | Total Images |
|:---|:---|:---:|:---:|:---:|:---:|
| **Family 1** | `PayLite` | 70 | 15 | 15 | **100** |
| **Family 2** | `QuickPe` | 70 | 15 | 15 | **100** |
| **Family 3** | `UniPay` | 70 | 15 | 15 | **100** |
| **Total** | | **210** | **45** | **45** | **300** |

### Actual Counts by Edit Type

| Edit Type | Label Class | Train Count | Val Count | Test Count | Total Count |
|:---|:---|:---:|:---:|:---:|:---:|
| `none` | `original` | 42 | 9 | 9 | **60** |
| `amount_change` | `synthetic_fake` | 19 | 1 | 4 | **24** |
| `date_change` | `synthetic_fake` | 20 | 5 | 4 | **29** |
| `transaction_id_change` | `synthetic_fake` | 20 | 4 | 4 | **28** |
| `text_insert` | `synthetic_fake` | 20 | 2 | 5 | **27** |
| `text_remove` | `synthetic_fake` | 19 | 2 | 4 | **25** |
| `font_alter` | `synthetic_fake` | 19 | 5 | 7 | **31** |
| `crop` | `synthetic_fake` | 21 | 4 | 5 | **30** |
| `resize` | `original_transformed` | 15 | 6 | 1 | **22** |
| `recompress` | `original_transformed` | 15 | 7 | 2 | **24** |
| **Total** | | **210** | **45** | **45** | **300** |

---

## 6. Naming Convention & Traceability

Every asset follows a strict hierarchical naming convention:
$$\text{image\_id} = \texttt{tpl\{Family\}\_src\{SourceID\}\_\{EditType\}\_\{VariantID\}}$$

- `tpl{F}`: Template layout index (`1` = PayLite, `2` = QuickPe, `3` = UniPay).
- `src{NNN}`: Master source generation ID (`001` through `060`).
- `{EditType}`: Specific perturbation tag.
- `{VariantID}`: Replication index (`01` through `04`).

**Example**: `tpl1_src001_amount_change_02.png` is the 2nd variant derived from source `tpl1_src001_none_01`.

---

## 7. The Splitting Strategy: Plain Language & Leakage Prevention

### What is Data Leakage?
Data leakage occurs when information from outside the training dataset is inadvertently used to train the machine learning model. In our dataset, each original receipt has 4 derived manipulated variants that share the exact same background geometry, recipient name, initial styling, and layout structure.

### What Would Go Wrong with Naive Random Splitting?
If we split randomly by `image_id`:
1. `tpl1_src001_none_01.png` could be placed in `train.csv`.
2. `tpl1_src001_amount_change_02.png` could be placed in `test.csv`.
Because the CNN model has already seen the identical template layout, colors, and fonts during training, it would simply memorize the source receipt visual fingerprint rather than learning generalizable tamper indicators. This produces artificially inflated 99%+ test accuracy that fails completely in real-world deployment.

### How We Prevent Leakage
We enforce **Group-Aware Splitting by `source_id`**:
- All 5 images belonging to source `tpl1_src001` (1 original + 4 variants) are assigned to the **same split together, always**.
- Split assignment is stratified by `template_family` at the group level to ensure equal layout representation.
- Cross-split verification via 256-bit perceptual difference hashing (dHash) formally proves **0% source overlap and 0 cross-split visual duplicates**.

---

## 8. Realized Split Ratios

The splitting algorithm achieved exactly the target group proportions:
- **Train Set**: 42 sources $\rightarrow$ **210 images (70.0%)**
- **Validation Set**: 9 sources $\rightarrow$ **45 images (15.0%)**
- **Test Set**: 9 sources $\rightarrow$ **45 images (15.0%)**

---

## 9. Class Balance & Honest Evaluation of Skew

- In a binary forensic framing (Legitimate vs. Manipulated):
  - **Legitimate / Benign** (`original` + `original_transformed`): **106 images (35.3%)**
  - **Manipulated / Tampered** (`synthetic_fake`): **194 images (64.7%)**
- **Distribution across splits**:
  - `original` is exactly 20.0% in Train, Val, and Test.
  - `original_transformed` has slight variance (Train: 14.3%, Val: 28.9%, Test: 6.7%) because variants are sampled pseudo-randomly per source.
- Downstream models must evaluate with **Precision, Recall, F1-Score, and ROC-AUC** in addition to raw accuracy to account for class balance.

---

## 10. Dataset Integrity Audit Results & Reproduction

Our automated audit script `src/dataset/audit.py` executes 11 comprehensive verification checks:

```
======================================================================
DATASET INTEGRITY & DATA LEAKAGE AUDIT REPORT — PERSON 2
======================================================================
Total Images Audited    : 300
Train Split Manifest    : 210 images (42 unique sources, 70.0%)
Val Split Manifest      : 45 images (9 unique sources, 15.0%)
Test Split Manifest     : 45 images (9 unique sources, 15.0%)
----------------------------------------------------------------------
[VERIFICATION CHECKS BREAKDOWN]
  [✓ PASS] 1. Group Disjointness (Zero Source Leakage)
  [✓ PASS] 2. File Existence on Disk
  [✓ PASS] 3. Zero Orphan Disk Files
  [✓ PASS] 4. Zero Duplicate Image IDs
  [✓ PASS] 5. Template Family Coverage across all splits
  [✓ PASS] 6. Label Class Coverage across all splits
  [✓ PASS] 7. Class Balance Consistency Reporting
  [✓ PASS] 8. Cross-Split Perceptual Near-Duplicate Hash Check (256-bit dHash)
  [✓ PASS] 9. Image Header & Pixel Decoding Check
  [✓ PASS] 10. Dimension Outlier & Canvas Constraint Check
  [✓ PASS] 11. Ground-Truth Answer Key Coverage
----------------------------------------------------------------------
🎉 OVERALL VERDICT: 100% AUDIT PASSED. DATASET IS LEAKAGE-FREE.
======================================================================
```

### How to Re-Run the Audit
```bash
python -m src.dataset.audit
```

---

## 11. Deterministic Reproduction Guide

The complete dataset pipeline can be regenerated identically from scratch using the global random seed `42`:

```bash
# Step 1: Generate 60 Clean Originals (Phase 2)
python -m src.dataset.templates --count 60 --samples

# Step 2: Generate 240 Manipulated Variants & metadata.csv (Phase 3)
python -m src.dataset.manipulate --variants-per-original 4 --samples

# Step 3: Generate Leakage-Safe Splits & Manifests (Phase 4)
python -m src.dataset.split --train 0.70 --val 0.15 --test 0.15 --seed 42

# Step 4: Run Full Dataset Integrity & Leakage Audit
python -m src.dataset.audit
```

---

## 12. Dataset Limitations & Academic Scope

To ensure intellectual honesty and academic rigour:
1. **Synthetic-Only Representation**: The dataset is entirely generated by Pillow drawing scripts. It does not contain camera optical distortions, screen glare, moiré patterns, or physical camera sensor noise.
2. **Fictionalized Brand Stylings**: Templates are designed around fictional apps (`PayLite`, `QuickPe`, `UniPay`) to avoid trademark infringements. They approximate real UPI layout conventions but do not replicate proprietary third-party UIs.
3. **Controlled Manipulation Types**: The 9 manipulation types represent systematic digital alterations. Real-world forgers may employ complex Photoshop layer masking or generative AI inpainting not fully captured here.
4. **Scale & Generalization**: With 300 total images, this dataset serves as a benchmark for proof-of-concept IDP evaluation. Results demonstrate algorithmic feasibility but do not directly guarantee production performance on arbitrary wild screenshots.

---

## 13. Handoff Note for Person 3 (CNN Model Training)

> **ATTENTION PERSON 3**:
> - Manifests are available in `data/splits/train.csv`, `data/splits/val.csv`, and `data/splits/test.csv`.
> - **Schema**: `image_id`, `source_id`, `template_family`, `label`, `edit_type`, `filename`, `relative_path`, `split`.
> - Image paths are relative to `data/` directory (e.g. `data/raw/...` and `data/processed/...`).
> - **Mandatory Verification**: Do not take this split on trust. Run `python -m src.dataset.audit` or independently verify group disjointness by checking `set(train_df['source_id']) & set(test_df['source_id']) == set()` in your PyTorch dataloader.
