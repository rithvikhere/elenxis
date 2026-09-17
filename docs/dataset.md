# Dataset Documentation
**Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP)**

---

## Overview

The dataset consists of **60 synthetic UPI payment receipt images** generated
programmatically using `scripts/generate_dataset.py`. Every image carries a
`DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY` watermark and uses
fictional, non-branded payment app names to prevent real-world misuse.

---

## Design Rationale

Real UPI receipts cannot be collected for academic use due to privacy regulations
(PAN, account number, real NPCI UTR exposure). Fictional receipt templates provide
full ground-truth labels and controlled tamper variants without ethical or legal risk.

---

## Receipt Templates

| Template   | App Name            | Colour Scheme      |
|------------|---------------------|--------------------|
| `apex`     | ApexPay UPI         | Blue & White       |
| `zenith`   | ZenithUPI           | Purple Modern      |
| `nova`     | NovaPay             | Green Minimalist   |

---

## Tamper Variant Types

| `edit_type`             | Description                                                                |
|-------------------------|----------------------------------------------------------------------------|
| `none` (original)       | Clean, unaltered receipt                                                   |
| `amount_change`         | Amount replaced with a large random value; font size/weight also changed   |
| `date_change`           | Date set to a future date (`28 Dec 2029`) — impossible for a completed UPI |
| `transaction_id_change` | UTR replaced with a short alphanumeric string (`UTR<7 digits>`)            |

---

## Dataset Statistics

| Attribute         | Value            |
|-------------------|------------------|
| Total images      | 60               |
| Unique templates  | 3                |
| Scenarios         | 15 (5 per template) |
| Variants/scenario | 4 (1 original + 3 tampered) |
| Image format      | PNG (RGB, ~540×800 px) |

### Split Strategy

| Split | Scenarios | Images | Purpose         |
|-------|-----------|--------|-----------------|
| Train | 0–8       | 36     | Model training  |
| Val   | 9–11      | 12     | Hyper-tuning    |
| Test  | 12–14     | 12     | Final evaluation |

**Zero data leakage** is guaranteed because the split is scenario-level (not
image-level) — no template scenario appears in more than one split.

---

## Metadata Schema (`data/metadata.csv`)

| Column                    | Type    | Description                              |
|---------------------------|---------|------------------------------------------|
| `image_id`                | str     | e.g. `img_001`                           |
| `filename`                | str     | e.g. `img_001.png`                       |
| `label`                   | str     | `original` or `synthetic_fake`           |
| `edit_type`               | str     | `none`, `amount_change`, etc.            |
| `amount_changed`          | yes/no  | Whether the amount was tampered          |
| `date_changed`            | yes/no  | Whether the date was tampered            |
| `transaction_id_changed`  | yes/no  | Whether the UTR was tampered             |
| `template_type`           | str     | `apex`, `zenith`, `nova`                 |
| `split`                   | str     | `train`, `val`, `test`                   |
| `ground_truth_amount`     | str     | Displayed amount string                  |
| `ground_truth_date`       | str     | Displayed date string                    |
| `ground_truth_time`       | str     | Displayed time string                    |
| `ground_truth_utr`        | str     | UTR / Transaction ID string              |
| `ground_truth_recipient`  | str     | Recipient merchant name                  |

---

## Reproducibility

The generator uses `random.seed(42)` for deterministic output.
Re-running `python scripts/generate_dataset.py` from the `PERSON_2_NIVASH/`
directory will recreate an identical dataset.
