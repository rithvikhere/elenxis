# Person 2 Subsystem Handoff & Interface Contracts
**UPI Transaction Fraud Forensics Platform (IDP)**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai*

---

## 1. Handoff to Person 1 (Lead, Frontend & Ensemble Layer)

### Public Python Contracts
Person 1 can import and execute both core pipelines without reading internal implementation details:

```python
from src.ocr.extractor import extract_transaction_fields
from src.rules.rule_engine import validate_transaction

# Step 1: Run OCR Extraction
ocr_result = extract_transaction_fields(image_input="path/to/screenshot.png", preprocess_mode="contrast")

# Step 2: Run Rule-Based Validation
rule_result = validate_transaction(ocr_result)
```

### Safety & Exception Guarantees:
- `extract_transaction_fields()` accepts: file path (`str` or `Path`), `PIL.Image.Image`, or byte streams.
- **Never raises exceptions**: Always returns structured dictionary with `"success": bool`, `"fields": dict`, and `"error": str | None`.
- `validate_transaction()` returns structured verdict: `"LIKELY_LEGITIMATE"`, `"SUSPICIOUS"`, or `"UNREADABLE"`.
- Missing fields default to `None` (never invented).

---

## 2. Handoff to Person 3 (CNN Training, ELA & Evaluation)

### Dataset Manifests:
Pre-computed split CSV manifests are located in `data/splits/`:
- `data/splits/train.csv` (210 images, 42 sources — 70.0%)
- `data/splits/val.csv` (45 images, 9 sources — 15.0%)
- `data/splits/test.csv` (45 images, 9 sources — 15.0%)

### Label Semantics & Taxonomy:
- `original` (60 images): Clean lossless renders.
- `original_transformed` (46 images): Benign resize / JPEG compression. Treat as legitimate in binary classification (`label=0`).
- `synthetic_fake` (194 images): Malicious tampering. Treat as tampered (`label=1`).

### Independent Split Verification Instruction:
Person 3 is instructed to **independently re-verify group disjointness** in their PyTorch training pipeline:
```python
import pandas as pd

train_df = pd.read_csv("data/splits/train.csv")
val_df = pd.read_csv("data/splits/val.csv")
test_df = pd.read_csv("data/splits/test.csv")

assert len(set(train_df["source_id"]) & set(test_df["source_id"])) == 0, "Data leakage detected!"
print("✓ Group disjointness verified: 0% data leakage.")
```
