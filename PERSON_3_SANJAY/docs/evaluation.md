# CNN Held-out Evaluation (Phase 4)

## Methodology

The fixed `resnet18_baseline_best.pt` checkpoint was evaluated on the 12 metadata
records explicitly assigned to `split=test` (`img_049.png` through `img_060.png`).
The evaluator verified the exact test-file membership, prediction-count equality,
and group isolation: test groups 12–14 do not overlap the train or validation
groups. No training, threshold tuning, or label changes were performed.

Class index `1` (`modified`) is the positive class. The held-out split has 3
original and 9 modified images, so accuracy on its own can conceal poor performance
on original images.

## Measured Results

| Accuracy | Precision | Recall | F1-score |
|---:|---:|---:|---:|
| 0.7500 | 0.7500 | 1.0000 | 0.8571 |

| | Predicted original | Predicted modified |
|---|---:|---:|
| True original | 0 (TN) | 3 (FP) |
| True modified | 0 (FN) | 9 (TP) |

All three held-out originals (`img_049.png`, `img_053.png`, and `img_057.png`)
were false positives. No false negatives were observed. A possible, unverified
explanation is that layout or compression features in these originals resembled
signals learned for the modified class.

Measured artifacts are under `PERSON_3_SANJAY/results/metrics/`:

- `metrics.json`
- `predictions.csv`
- `error_analysis.csv`
- `confusion_matrix.png`
- `evaluation_report.md`

## Limitations

The test set is small, synthetic, and imbalanced, with only three original
examples. These are baseline measurements, not evidence of real-world
generalization. Model outputs and image-forensics signals are indicators for
inspection, not proof that a transaction occurred or that fraud occurred.

## Reproducing the Evaluation

```powershell
.\.venv\Scripts\python.exe PERSON_3_SANJAY\scripts\evaluate_test_set.py
```
