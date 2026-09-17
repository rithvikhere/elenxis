# Dataset & Template Design Specification
**Person 2 — UPI Transaction Fraud Forensics Platform**
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai*

---

## 1. Why a Synthetic Dataset?

In payment receipt fraud analysis, **no publicly available, labeled ground-truth dataset** of real vs. manipulated UPI payment screenshots exists due to banking privacy laws, KYC regulations, and PII protection constraints. Scraped online receipts carry unknown editing histories and privacy violations. 

To bridge this data-availability gap, our project creates a **controlled, reproducible synthetic dataset generator**. Building this controlled dataset generator and ground-truth metadata schema is a foundational academic research contribution of this project.

---

## 2. Why Fictional, Non-Branded Templates?

To adhere strictly to academic integrity, ethical research principles, and trademark safety:
- **No Real Brand Names or Logos**: We invent fictional stand-in payment application identities (`PayLite`, `QuickPe`, `UniPay`).
- **No Real Financial Data**: All account numbers, virtual payment addresses (VPAs), UTRs, and names are generated from purely fictional mock registries.
- **Detector-Only Purpose**: Assets exist strictly to train and evaluate detection algorithms, never to produce deceptive payment instruments for real-world use.

---

## 3. Template Layout Families (3 Distinct Structures)

To prevent the OCR and CNN pipelines from overfitting to a single rigid visual structure, we define **three structurally distinct layout families**:

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

| Design Dimension | Family 1: `PayLite` | Family 2: `QuickPe` | Family 3: `UniPay` |
|:---|:---|:---|:---|
| **Visual Theme** | Flat Header Banner (Primary Blue `#1A73E8`) | Elevated Floating Card (`#1E2738` on `#121824`) | Clean Minimalist Two-Tone Grid (`#FAFAFA`) |
| **Hero Amount Placement** | Large centered hero typography ($y \approx 215\text{px}$) | Inside top elevated card ($y \approx 170\text{px}$) | Left-aligned bold sub-header ($y \approx 105\text{px}$) |
| **Date / Time Formatting** | Textual month (`12 Mar 2026, 10:15 AM`) | Compact inline (`12-03-2026, 10:15 AM`) | ISO format (`2026-03-12, 10:15`) |
| **UTR / Reference Label** | `UPI Ref (UTR)` | `Reference ID (UTR)` | `Bank Ref (UTR)` |
| **Status Indicator** | Central circle with success tick icon | Top-right pill badge: `[✓ COMPLETED]` | Top-right rectangular badge: `[ SUCCESS ]` |

---

## 4. Standard Field Definitions & Coordinate Anchors

Every synthetic receipt guarantees the presence of eight core fields rendered at structurally bounded coordinates:

| Field Name | Description | Datatype | Example |
|:---|:---|:---:|:---|
| `app_name` | Fictional application brand | `str` | `PayLite`, `QuickPe`, `UniPay` |
| `status` | Confirmation status keyword | `str` | `Paid Successfully`, `Payment Completed`, `SUCCESS` |
| `amount` | Monetary value with currency indicator | `str` / `float` | `₹450.00`, `₹1,250.50`, `₹29,873.87` |
| `payee` | Recipient business / contact name | `str` | `Metro Book Store`, `Apex Mart`, `Sunrise Cafe` |
| `payer` | Sender account description | `str` | `Synthetic Student Account`, `Demo Academic User` |
| `date` | Transaction execution date | `str` | `12 Mar 2026`, `12-03-2026`, `2026-03-12` |
| `time` | Transaction timestamp (12h or 24h) | `str` | `10:15 AM`, `02:45 PM`, `14:30` |
| `transaction_id` | 12-digit standard UPI reference number | `str` | `425631219101`, `637940265423` |

---

## 5. Label Semantics: Tri-State Classification & Rationale

We establish a clear, scientifically rigorous tri-state label taxonomy in `data/metadata.csv`:

1. **`original`** (Untouched Render):
   - Pixel-perfect, lossless PNG render from the template generator with untouched layout and values.

2. **`original_transformed`** (Benign Real-World Channel Degradation):
   - Screenshots that underwent benign distribution transformations (e.g. `resize` downscale/upscale or `recompress` JPEG quality degradation) **without content alteration**.
   - **Critical Rationale**: In real life, users frequently forward genuine payment receipts through WhatsApp or messaging apps, which compresses or resizes the image. If benign compression were labeled `synthetic_fake`, the CNN detector would learn to classify compression noise rather than semantic forgery. This label allows training models to distinguish compression from malicious editing.

3. **`synthetic_fake`** (Malicious / Manipulated Forgery):
   - Receipts exhibiting deliberate content tampering (`amount_change`, `date_change`, `transaction_id_change`, `text_insert`, `text_remove`, `font_alter`, `crop`).

---

## 6. Manipulation Categories & Forensic Impact

| # | `edit_type` | Label | Implementation & Forensic Impact |
|:---:|:---|:---:|:---|
| 1 | `none` | `original` | Clean unmanipulated baseline image. |
| 2 | `amount_change` | `synthetic_fake` | Original amount patched over and overwritten with new value, creating localized edge splice boundaries. |
| 3 | `date_change` | `synthetic_fake` | Timestamp modified (including 50% future dates) to trigger temporal rule engine violations. |
| 4 | `transaction_id_change` | `synthetic_fake` | UTR overwritten with alpha prefixes, non-12 digit lengths, or mutated values to test format validators. |
| 5 | `text_insert` | `synthetic_fake` | Spliced artificial verification stamps (e.g. `[ AUTHENTICATED BY BANK ]`) into white space. |
| 6 | `text_remove` | `synthetic_fake` | Required fields (e.g. UTR or Recipient) blanked out with background color patches. |
| 7 | `font_alter` | `synthetic_fake` | Field re-rendered with mismatched font weight, size, or baseline alignment. |
| 8 | `crop` | `synthetic_fake` | Asymmetric margin cropping simulating merchant framing error. |
| 9 | `resize` | `original_transformed` | Bilinear downscaling and upscaling (content identical). |
| 10 | `recompress` | `original_transformed` | JPEG recompression at quality 50–70 to benchmark ELA sensitivity without altering transaction content. |

---

## 7. Systematic Naming Convention & Leakage Prevention

$$\text{Image ID} = \texttt{tpl\{Family\}\_src\{SourceID\}\_\{EditType\}\_\{VariantID\}}$$

- `tpl{F}`: Template family index (`1` = PayLite, `2` = QuickPe, `3` = UniPay).
- `src{NNN}`: Master source generation index (`001` to `060`).
- `{EditType}`: Manipulation tag (e.g. `none`, `amount_change`, `recompress`).
- `{VariantID}`: Replication variation counter (`01` to `04`).

**Example**: `tpl1_src004_amount_change_01.png`

**Leakage Prevention**: All splits are grouped strictly on `source_id` (`tpl{F}_src{NNN}`). All variants deriving from source `004` are partitioned strictly into one split manifest.

---

## 8. Mandatory Watermark & Non-Interference Guarantee

Every generated asset carries the footer watermark at $y = 770\text{px}$:

```
DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY
```

- **Coordinates**: Horizontally centered, 11pt font, neutral gray.
- **Non-Interference**: Positioned at least 40px below the lowest transaction detail line to guarantee that OCR bounding boxes for transaction fields remain completely unoccluded.

---

## 9. Generation — Originals (Phase 2 Empirical Record)

- **Total Originals Generated**: `60 images`
- **Family 1 (`PayLite`)**: `20 images` (`tpl1_src001_none_01.png` to `tpl1_src020_none_01.png`)
- **Family 2 (`QuickPe`)**: `20 images` (`tpl2_src021_none_01.png` to `tpl2_src040_none_01.png`)
- **Family 3 (`UniPay`)**: `20 images` (`tpl3_src041_none_01.png` to `tpl3_src060_none_01.png`)
- **Random Seed**: `42`
- **Reproduction Command**: `python -m src.dataset.templates --count 60 --samples`

---

## 10. Generation — Manipulations (Phase 3 Empirical Record)

- **Total Images in Full Dataset**: **`300 images`** (60 Originals + 240 Manipulated Variants)
- **Variants per Original**: Exactly **4 variants** generated per source original.
- **Random Seed**: `42`
- **Reproduction Command**:
  ```bash
  python -m src.dataset.manipulate --variants-per-original 4 --samples
  ```

### Label Distribution (Class Balance)
| Class Label | Count | Proportion | Semantic Meaning |
|:---|:---:|:---:|:---|
| `original` | 60 | 20.0% | Clean untouched synthetic originals |
| `original_transformed` | 46 | 15.3% | Benign transformations (resize, recompress) |
| `synthetic_fake` | 194 | 64.7% | Malicious content manipulations |
| **Total** | **300** | **100.0%** | Comprehensive forensic dataset |

*Note on Class Balance*: In a standard binary classification setup, `original` + `original_transformed` comprise **106 images (35.3%)** vs. `synthetic_fake` **194 images (64.7%)**. This intentional ratio reflects real-world anomaly detection tasks where anomalies occur across diverse edit classes while preserving substantial benign baselines.

### Edit Type Breakdown
| Edit Type | Label Class | Count |
|:---|:---|:---:|
| `none` | `original` | 60 |
| `amount_change` | `synthetic_fake` | 24 |
| `date_change` | `synthetic_fake` | 29 |
| `transaction_id_change` | `synthetic_fake` | 28 |
| `text_insert` | `synthetic_fake` | 27 |
| `text_remove` | `synthetic_fake` | 25 |
| `font_alter` | `synthetic_fake` | 31 |
| `crop` | `synthetic_fake` | 30 |
| `resize` | `original_transformed` | 22 |
| `recompress` | `original_transformed` | 24 |
| **Total** | | **300** |

### Template Family Breakdown
- **Family 1 (`PayLite`)**: `100 images`
- **Family 2 (`QuickPe`)**: `100 images`
- **Family 3 (`UniPay`)**: `100 images`

---

## 11. Academic & Legal Safety Statement

> **Ethical & Safety Notice**: This synthetic dataset is constructed solely for academic research in document tamper detection and automated forensic verification. All templates are completely non-branded, all account information and UTRs are generated from random seeds, and no real-world banking ledgers, customer records, or payment gateways are accessed. The generator is restricted to producing detector training data and is expressly not designed or intended to produce usable payment evidence.
