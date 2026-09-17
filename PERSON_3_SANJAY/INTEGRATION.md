# Person 3 Integration Contract

## Imports

```python
from PERSON_3_SANJAY.src.api import analyze_image, predict, get_person3_status
```

## CNN Prediction

`predict(image, weights_path=None)` accepts a filesystem path, Pillow image,
bytes, or NumPy array. Without `weights_path`, it loads
`PERSON_3_SANJAY/models/resnet18_baseline_best.pt`.

Successful response:

```python
{
  "status": "success",
  "class": "original" | "modified",
  "probability": 0.0,
  "probabilities": {"original": 0.0, "modified": 0.0},
  "model": "ResNet18",
  "available": True,
  "explanation": "..."
}
```

If the selected checkpoint does not exist, it returns `status: "unavailable"`,
`class: None`, and no prediction. Invalid images or load failures return
`status: "error"` and no prediction. `modified` means the CNN assigned that
learned image class; it does not verify a payment, manipulation, or fraud.

## Image Forensics

`analyze_image(image, ela_output_dir=None, quality=90)` returns separate
evidence sections:

```python
{
  "status": "available" | "error",
  "ela": {"status": "...", "output_visualization_path": "...", "summary_statistics": {}},
  "metadata": {"status": "...", "file_format": "...", "dimensions": {}, "has_exif": False},
  "warnings": ["..."],
  "explanation": "..."
}
```

Give `ela_output_dir` (for example `PERSON_3_SANJAY/results/ela`) to persist
the ELA visualization. No forensic score is emitted. ELA and absent EXIF are
indicators/availability facts only, not proof of manipulation or fraud.

## Runtime Status

`get_person3_status()` reports checkpoint availability, device information, and
module readiness. Person 1 can use it to disable unavailable UI actions rather
than assuming a model is loaded.

## Checkpoint Requirement

The supplied model is the compatible ResNet-18 checkpoint in `models/`. Do not
replace it with a different architecture under the same filename. The input is
preprocessed deterministically to 224×224 RGB with ImageNet normalization.
