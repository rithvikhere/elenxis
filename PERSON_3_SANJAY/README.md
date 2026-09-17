# Person 3 (Sanjay) — UPI Fraud Forensics Subsystem

Person 3 owns the CNN visual-classification baseline, held-out evaluation, and
image-forensics evidence (ELA and metadata/EXIF) for the UPI Fraud Forensics
Platform.

## Scope and Interpretation Boundary

This subsystem analyzes **UPI-style payment screenshots** for learned visual
classes and image-level indicators. It does not verify whether a financial
transaction occurred and does not prove fraud. CNN outputs are predictions; ELA
and metadata outputs are evidence for inspection only.

## Completed Work

### Phases 1–3: Dataset and CNN Baseline

- Validated 60 synthetic PNG screenshots from Person 2.
- Used group-aware receipt splits: 36 train, 12 validation, and 12 held-out test
  images. Variants from the same receipt remain in one split.
- Implemented deterministic 224×224 evaluation preprocessing and conservative
  training augmentation.
- Trained an ImageNet-pretrained, end-to-end fine-tuned ResNet-18 classifier.
- Class mapping: `0 = original`, `1 = modified`.
- Checkpoints: `models/resnet18_baseline_best.pt` and
  `models/resnet18_baseline_final.pt`.

### Phase 4: Held-out Evaluation

The fixed best checkpoint was evaluated once on the isolated 12-image test set.
The positive class is `modified`.

| Accuracy | Precision | Recall | F1-score |
|---:|---:|---:|---:|
| 0.7500 | 0.7500 | 1.0000 | 0.8571 |

Confusion matrix: TN 0, FP 3, FN 0, TP 9. All three held-out originals were
predicted as modified. Since the small synthetic test set is 3:1 modified versus
original, this result is a baseline measurement rather than real-world evidence.
See `docs/evaluation.md` and `results/metrics/`.

### Phase 5: Image-Forensics Prototype

- `analyze_ela()` uses controlled JPEG recompression and returns an amplified
  ELA visualisation plus descriptive difference statistics.
- `inspect_metadata()` reports actual format, dimensions, file size, image-info
  fields, EXIF fields, software, and timestamps when present.
- `analyze_image()` keeps ELA and metadata evidence separate and returns no
  forensic score or final decision.
- Missing EXIF is not evidence of manipulation; screenshots and shared images
  commonly have no EXIF.

Controlled examples in `results/ela/` show that ELA is not universal: the
original and amount-edited PNGs had very similar mean differences (0.8172 and
0.8241), while merely resizing the original produced 1.0708. See
`docs/forensics.md` for limits and interpretation.

## Integration API

```python
from PERSON_3_SANJAY.src.api import analyze_image, predict, get_person3_status

# Evidence-only forensics result: separate `ela`, `metadata`, `warnings`.
forensics_result = analyze_image("path/to/screenshot.png")

# CNN prediction result: model output, not transaction or fraud verification.
cnn_result = predict("path/to/screenshot.png")

status = get_person3_status()
```

For direct forensic use:

```python
from PERSON_3_SANJAY.src.forensics.ela import analyze_ela
from PERSON_3_SANJAY.src.forensics.metadata import inspect_metadata
from PERSON_3_SANJAY.src.forensics.forensic_analysis import analyze_image
```

## Structure

```text
PERSON_3_SANJAY/
├── docs/                 # Architecture, evaluation, and forensics documentation
├── models/               # Trained ResNet-18 checkpoints
├── results/
│   ├── metrics/          # Held-out metrics, predictions, error analysis, matrix
│   └── ela/              # Controlled ELA example outputs
├── scripts/
│   ├── train_model.py
│   ├── evaluate_test_set.py
│   └── generate_ela_examples.py
├── src/
│   ├── forensics/        # ELA, metadata, unified evidence wrapper
│   ├── model/            # Dataset, preprocessing, model, training, evaluation
│   └── api.py            # Integration entry points
└── tests/                # Pytest suite
```

## Commands

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest PERSON_3_SANJAY\tests -v
.\.venv\Scripts\python.exe PERSON_3_SANJAY\scripts\evaluate_test_set.py
.\.venv\Scripts\python.exe PERSON_3_SANJAY\scripts\generate_ela_examples.py
```

The current test suite contains 19 passing tests.
