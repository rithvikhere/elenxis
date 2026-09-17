# Person 3 (Sanjay) — UPI Fraud Forensics Subsystem

Welcome to the **Person 3** subsystem of the **UPI Transaction Fraud Forensics Platform**.

## Responsibilities Overview
- **CNN / Visual Classification**: Transfer learning & custom neural network architectures for visual tampering detection.
- **Image Forensics**: Error Level Analysis (ELA) and EXIF/metadata inspection.
- **Evaluation & Error Analysis**: Standard metrics (accuracy, precision, recall, F1, confusion matrix) and systematic False Positive / False Negative failure mode tracking.
- **Explainability (Roadmap)**: Grad-CAM heatmap visualization (scheduled for Phase 3).
- **Public API**: Stable, defensive API contracts for integration by Person 1 (Rithvik).

---

## Directory Structure

```text
PERSON_3_SANJAY/
├── docs/
│   └── sanjay_architecture.md   # Architectural design and scientific disclaimers
├── models/                      # Saved model weights (.pt / .pth checkpoints)
├── results/                     # Experiment metrics, evaluation reports, confusion matrices
├── src/
│   ├── api.py                   # Clean public integration entry points
│   ├── explainability/          # Grad-CAM roadmap & explainability modules
│   │   └── gradcam.py
│   ├── forensics/               # Error Level Analysis & EXIF inspection
│   │   ├── ela.py
│   │   ├── metadata.py
│   │   └── forensics_engine.py
│   ├── model/                   # CNN architectures, dataset loaders, evaluation
│   │   ├── cnn_model.py
│   │   ├── dataset.py
│   │   └── evaluate.py
│   └── utils/                   # Device detection, safe image I/O
│       ├── device.py
│       └── image_io.py
├── tests/                       # Pytest test suite
│   ├── test_api.py
│   ├── test_forensics.py
│   └── test_model.py
├── requirements.txt             # Person 3 dependencies
└── README.md                    # Subsystem documentation
```

---

## Integration Contracts (For Person 1)

Person 1 can import and run the following stable functions:

```python
from PERSON_3_SANJAY.src.api import analyze_image, predict, get_person3_status

# 1. Run Image Forensics (ELA + EXIF)
forensics_result = analyze_image("path/to/screenshot.jpg")

# 2. Run CNN Visual Prediction
cnn_result = predict("path/to/screenshot.jpg")

# 3. Check Subsystem Readiness
status = get_person3_status()
```

---

## Testing

Run unit tests via `pytest`:

```bash
pytest PERSON_3_SANJAY/tests -v
```
