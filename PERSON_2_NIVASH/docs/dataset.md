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

## 5. Ground Truth & Binary Labeling Scheme

Every generated asset is tracked with dual labeling:

1. **Binary Class Label (`label`)**:
   - `original`: An untampered, cleanly synthesized receipt image.
   - `synthetic_fake`: A receipt exhibiting one or more controlled programmatic manipulations (Phase 3).

2. **Fine-Grained Manipulation Label (`edit_type`)**:
   - Explicitly records which transformation was applied (`none` for originals).

---

## 6. Planned Manipulation Categories (10 Edit Types)

| # | `edit_type` | Description & Forensic Impact |
|:---:|:---|:---|
| 1 | `none` | Clean unmanipulated baseline image (`label = original`). |
| 2 | `amount_change` | Numerical hero amount is replaced with a mismatched amount (e.g. `₹450.00` → `₹9,450.00`), causing pixel splice edges and font anti-aliasing mismatch. |
| 3 | `date_change` | Timestamp modified to a future date or irregular format, triggering logical rule violations and localized resave noise. |
| 4 | `transaction_id_change` | UTR modified to non-12-digit lengths or injected alphanumeric characters, triggering rule-based syntax errors. |
| 5 | `text_insert` | Artificial watermarks, fake bank reference stamps, or extra lines spliced into white space. |
| 6 | `text_remove` | Critical fields (e.g. UTR or Status) patched over with background color clones, leaving boundary noise. |
| 7 | `font_alter` | Targeted field rendered with a subtle mismatched font family or incorrect font weight. |
| 8 | `crop` | Asymmetric border cropping simulating careless merchant camera cropping, altering receipt proportions. |
| 9 | `resize` | Bi-linear/nearest-neighbor downsampling followed by upsampling, causing global high-frequency blur. |
| 10 | `recompress` | Selective JPEG recompression at quality 50–70, creating measurable ELA error deltas. |

---

## 7. Systematic Naming Convention & Leakage Prevention

$$\text{Image ID} = \texttt{tpl\{Family\}\_src\{SourceID\}\_\{EditType\}\_\{VariantID\}}$$

- `tpl{F}`: Template family index (`1` = PayLite, `2` = QuickPe, `3` = UniPay).
- `src{NNN}`: Master source generation index (`001` to `100`).
- `{EditType}`: Manipulation tag (`none` for originals).
- `{VariantID}`: Replication variation counter (`01`).

**Example Filename**: `tpl1_src001_none_01.png`

**Split Strategy**: When partitioning data into `train`, `val`, and `test` manifests in Phase 4, splits are grouped strictly by `src{NNN}`, preventing identical visual structures from leaking across splits.

---

## 8. Mandatory Watermark & Non-Interference Guarantee

Every generated image is programmatically watermarked at the canvas footer ($y \ge 770\text{px}$):

```
DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY
```

- **Coordinates**: Horizontally centered, 10–12pt sans-serif font, neutral gray.
- **Non-Interference**: Positioned at least 40px below the lowest transaction detail line to guarantee that OCR bounding boxes for transaction fields remain completely unoccluded.

---

## 9. Generation — Originals (Phase 2 Empirical Record)

The Phase 2 Template Synthesis Engine has been executed to generate the unmanipulated baseline dataset:

- **Total Originals Generated**: `60 images`
- **Family 1 (`PayLite`)**: `20 images` (`tpl1_src001_none_01.png` to `tpl1_src020_none_01.png`)
- **Family 2 (`QuickPe`)**: `20 images` (`tpl2_src021_none_01.png` to `tpl2_src040_none_01.png`)
- **Family 3 (`UniPay`)**: `20 images` (`tpl3_src041_none_01.png` to `tpl3_src060_none_01.png`)
- **Random Seed**: `42` (ensures 100% byte-identical reproducibility)
- **Reference Date Boundary**: `2026-03-15` (all generated transaction dates fall strictly in the past)
- **Reproduction Command**:
  ```bash
  python -m src.dataset.templates --count 60 --samples
  ```
- **Ground-Truth File**: [`data/ground_truth.csv`](file:///Users/nivash/elenxis/PERSON_2_NIVASH/data/ground_truth.csv) (60 ground-truth answer key rows with exact amount, date, time, and 12-digit UTR values).
- **Committed Sample Images**:
  - `docs/samples/sample_family1_paylite.png`
  - `docs/samples/sample_family2_quickpe.png`
  - `docs/samples/sample_family3_unipay.png`

---

## 10. Academic & Legal Safety Statement

> **Ethical & Safety Notice**: This synthetic dataset is constructed solely for academic research in document tamper detection and automated forensic verification. All templates are completely non-branded, all account information and UTRs are generated from random seeds, and no real-world banking ledgers, customer records, or payment gateways are accessed. The generator is restricted to producing detector training data and is expressly not designed or intended to produce usable payment evidence.
