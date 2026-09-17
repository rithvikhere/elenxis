# Dataset Handoff Guide for Person 3 (CNN Model Training)
**Person 2 (Dataset, OCR, Rule Engine) $\rightarrow$ Person 3 (CNN Feature Extraction & Classification)**  
*Project: UPI Transaction Fraud Forensics Platform (Academic IDP, VIT Chennai)*

---

## 1. Quick Start: Loading Split Manifests

All dataset splits are prepared as pre-computed CSV manifests in `data/splits/`:

- `data/splits/train.csv` (210 images, 42 unique sources — 70.0%)
- `data/splits/val.csv` (45 images, 9 unique sources — 15.0%)
- `data/splits/test.csv` (45 images, 9 unique sources — 15.0%)

### Manifest Schema & Columns

| Column | Type | Example | Description |
|:---|:---|:---|:---|
| `image_id` | `str` | `tpl1_src001_amount_change_02` | Unique identifier for each image asset |
| `source_id` | `str` | `tpl1_src001_none_01` | Master original ID (used for group-aware splitting) |
| `template_family` | `int` | `1` | Layout family: `1` (PayLite), `2` (QuickPe), `3` (UniPay) |
| `label` | `str` | `synthetic_fake` | Tri-state class: `original`, `original_transformed`, `synthetic_fake` |
| `edit_type` | `str` | `amount_change` | Specific manipulation method (1 of 10 types) |
| `filename` | `str` | `tpl1_src001_amount_change_02.png` | Basename of the file |
| `relative_path` | `str` | `processed/tpl1_src001_amount_change_02.png` | Path relative to `data/` directory |
| `split` | `str` | `train` | Split partition name (`train`, `val`, `test`) |

---

## 2. PyTorch DataLoader Example

```python
import pandas as pd
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T

class UPIDataset(Dataset):
    def __init__(self, manifest_csv: str, data_root: str = "data", transform=None, binary_labels: bool = True):
        self.df = pd.read_csv(manifest_csv)
        self.data_root = Path(data_root)
        self.transform = transform
        self.binary_labels = binary_labels

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.data_root / row["relative_path"]
        image = Image.open(img_path).convert("RGB")
        
        if self.transform:
            image = self.transform(image)

        # Label encoding
        if self.binary_labels:
            # 0: Legitimate (original + original_transformed), 1: Tampered (synthetic_fake)
            label = 0 if row["label"] in ["original", "original_transformed"] else 1
        else:
            # 3-class classification
            label_map = {"original": 0, "original_transformed": 1, "synthetic_fake": 2}
            label = label_map[row["label"]]

        return image, label, row["image_id"]
```

---

## 3. Mandatory Independent Re-Verification

> **CRITICAL INSTRUCTION FOR PERSON 3**:  
> Please **do not take the split integrity on trust**. Run the following verification code in your test pipeline to independently confirm zero data leakage:

```python
import pandas as pd

train_df = pd.read_csv("data/splits/train.csv")
val_df = pd.read_csv("data/splits/val.csv")
test_df = pd.read_csv("data/splits/test.csv")

train_sources = set(train_df["source_id"])
val_sources = set(val_df["source_id"])
test_sources = set(test_df["source_id"])

# Assert zero leakage
assert len(train_sources & val_sources) == 0, "Leakage between train and val!"
assert len(train_sources & test_sources) == 0, "Leakage between train and test!"
assert len(val_sources & test_sources) == 0, "Leakage between val and test!"

print("✓ Independent verification passed: Splits are 100% group-disjoint.")
```

You can also re-run the full 11-check dataset integrity suite at any time:
```bash
python -m src.dataset.audit
```
