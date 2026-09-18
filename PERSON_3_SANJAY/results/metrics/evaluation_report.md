# Held-out CNN Evaluation and Error Analysis

## Methodology

The fixed ResNet-18 checkpoint was evaluated once on the metadata rows explicitly assigned to the held-out `test` split. No training, threshold tuning, or label changes were performed. The evaluator verified that prediction count matched the test-set count and that test groups did not overlap non-test groups.

- Test samples: 12 (groups 12, 13, 14)
- Positive class: `modified` (class index 1)
- Class distribution: 3 original, 9 modified

## Metrics

| Accuracy | Precision | Recall | F1-score |
|---:|---:|---:|---:|
| 0.7500 | 0.7500 | 1.0000 | 0.8571 |

Precision, recall, and F1 treat `modified` as positive. Since this test split contains three times as many modified as original examples, accuracy alone can mask poor original-class performance.

## Confusion Matrix

| | Predicted original | Predicted modified |
|---|---:|---:|
| True original | 0 (TN) | 3 (FP) |
| True modified | 0 (FN) | 9 (TP) |

The corresponding figure is `confusion_matrix.png`.

## Error Analysis

| Image | True label | Prediction | Error type | Confidence | Possible reason |
|---|---|---|---|---:|---|
| img_049.png | original | modified | false_positive | 0.6614 | Possible reason: this original image may contain layout or compression features resembling signals learned for the modified class; this is a hypothesis. |
| img_053.png | original | modified | false_positive | 0.6434 | Possible reason: this original image may contain layout or compression features resembling signals learned for the modified class; this is a hypothesis. |
| img_057.png | original | modified | false_positive | 0.7403 | Possible reason: this original image may contain layout or compression features resembling signals learned for the modified class; this is a hypothesis. |

The possible reasons are hypotheses based on the observed samples, not demonstrated causes. This CNN prediction and the associated image-forensics indicators are not proof that a financial transaction occurred or that fraud occurred.

## Limitations

This is a small (12-image), synthetic, imbalanced held-out test set covering three templates and three edit categories. Results should be interpreted as a baseline measurement rather than evidence of real-world generalization.
