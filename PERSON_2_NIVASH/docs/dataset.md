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
| **Visual Theme** | Flat Header Banner (Primary Tint) | Elevated Central Card Container | Clean Minimalist Two-Tone Grid |
| **Hero Amount Placement** | Large centered hero typography (y ≈ 260px) | Inside top card container (y ≈ 240px) | Left-aligned bold sub-header (y ≈ 200px) |
| **Date / Time Formatting** | Textual month (`12 Mar 2026, 10:15 AM`) | Compact inline (`12-03-2026 | 10:15 AM`) | ISO format (`2026-03-12 10:15 AM`) |
| **UTR / Reference Label** | `UPI Ref No.` / `UTR` | `Transaction Reference ID` | `Bank Ref (UTR)` |
| **Status Indicator** | Central circle with success tick icon | Pill badge: `[✓ PAYMENT COMPLETED]` | Top-right label: `STATUS: SUCCESS` |

---

## 4. Standard Field Definitions & Coordinate Anchors

Every synthetic receipt guarantees the presence of eight core fields rendered at fixed or structurally bounded relative coordinates:

| Field Name | Description | Datatype | Example |
|:---|:---|:---:|:---|
| `app_template` | Fictional application brand | `str` | `PayLite`, `QuickPe`, `UniPay` |
| `status` | Confirmation status keyword | `str` | `Paid Successfully`, `Payment Completed` |
| `amount` | Monetary value with currency indicator | `str` / `float` | `₹450.00`, `₹1,250.00` |
| `recipient` | Payee business / contact name | `str` | `Metro Book Store`, `Apex Cafe` |
| `payer` | Sender account description | `str` | `Synthetic Student Account` |
| `date` | Transaction execution date | `str` | `12 Mar 2026`, `2026-03-12` |
| `time` | Transaction timestamp (12h or 24h) | `str` | `10:15 AM`, `14:30:00` |
| `transaction_id` | 12-digit standard UPI reference number | `str` | `425631219101` |

---

## 5. Ground Truth & Binary Labeling Scheme

Every generated asset is tracked with dual labeling:

1. **Binary Class Label (`label`)**:
   - `original`: An untampered, cleanly synthesized receipt image.
   - `synthetic_fake`: A receipt exhibiting one or more controlled programmatic manipulations.

2. **Fine-Grained Manipulation Label (`edit_type`)**:
   - Explicitly records which transformation was applied (see Section 6).

---

## 6. Planned Manipulation Categories (10 Edit Types)

To provide diverse forensic anomalies for both OCR/rules (semantic/logical anomalies) and CNN/ELA (pixel/compression anomalies), we plan 10 distinct edit types:

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

To ensure group-aware dataset partitioning (avoiding identical layout variants leaking across train and test splits):

$$\text{Image ID} = \texttt{tpl\{Family\}\_src\{SourceID\}\_\{EditType\}\_\{VariantID\}}$$

- `tpl{F}`: Template family index (`1` = PayLite, `2` = QuickPe, `3` = UniPay).
- `src{NNN}`: Master source generation index (`001` to `100`).
- `{EditType}`: Manipulation tag (e.g. `none`, `amount_change`, `recompress`).
- `{VariantID}`: Replication variation counter (`01`, `02`).

**Example Filename**: `tpl1_src042_amount_change_01.png`

**Split Strategy**: When partitioning data into `train`, `val`, and `test` manifests, splits are grouped strictly by `src{NNN}`. All derivative edits of source `src042` reside strictly within one partition.

---

## 8. Mandatory Watermark & Non-Interference Guarantee

Every generated image is programmatically watermarked at the canvas footer ($y \ge 770\text{px}$):

```
DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY
```

- **Coordinates**: Horizontally centered, 10–12pt sans-serif font, neutral gray (`#888888`).
- **Non-Interference**: Positioned at least 40px below the lowest transaction detail line to guarantee that OCR bounding boxes for transaction fields remain completely unoccluded.

---

## 9. Academic & Legal Safety Statement

> **Ethical & Safety Notice**: This synthetic dataset is constructed solely for academic research in document tamper detection and automated forensic verification. All templates are completely non-branded, all account information and UTRs are generated from random seeds, and no real-world banking ledgers, customer records, or payment gateways are accessed. The generator is restricted to producing detector training data and is expressly not designed or intended to produce usable payment evidence.

---

## 10. Planned Dataset Scale (Phase 3 Target)

| Split | Proportion | Planned Original Images | Planned Manipulated Images | Planned Total Images |
|:---|:---:|:---:|:---:|:---:|
| **Train** | 60% | 180 | 540 | 720 |
| **Validation** | 20% | 60 | 180 | 240 |
| **Test (Held-Out)** | 20% | 60 | 180 | 240 |
| **Total Target** | **100%** | **300** | **900** | **1,200** |

*(Note: Target counts will be updated with exact measured figures upon completion of Phase 3 generation).*
