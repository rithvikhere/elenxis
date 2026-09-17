# Final Person 3 Report

## 1. Objective and Scope

Person 3 implemented visual CNN classification, image-forensics evidence, held-out evaluation, Grad-CAM, and integration-ready APIs. The subsystem analyses screenshots; it does not verify a payment or prove fraud.

## 2. Dataset, Split, and Leakage Prevention

The synthetic dataset contains 60 RGB PNG screenshots: 15 original and 45 modified. Each receipt group contains one original and three controlled edits. Groups 0–8 (36 images) are training, 9–11 (12) validation, and 12–14 (12) held-out test. Group overlap checks found zero train/validation/test overlap.

## 3. Preprocessing, CNN, and Training

Inputs are RGB, resized to 224×224, and ImageNet-normalized. Training used only subtle brightness/contrast jitter; validation/test were deterministic. The model is ImageNet-pretrained ResNet-18 with a dropout/linear two-class head (`original=0`, `modified=1`), fully fine-tuned with AdamW, cross-entropy, batch size 8, learning rate 0.0001, weight decay 0.0001, seed 42, and 10 epochs on CPU. Final train loss was 0.5503 and validation loss 0.5173; this small synthetic setup remains at high overfitting risk.

## 4. Held-out Evaluation and Error Analysis

The fixed best checkpoint was evaluated once on the 12 held-out images without retraining or tuning. Positive class: modified.

| Accuracy | Precision | Recall | F1 | TN | FP | FN | TP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.7500 | 0.7500 | 1.0000 | 0.8571 | 0 | 3 | 0 | 9 |

False positives were `img_049.png`, `img_053.png`, and `img_057.png`; each original was predicted modified. Possible layout/compression similarity is a hypothesis, not demonstrated cause. The confusion matrix is `results/metrics/confusion_matrix.png`.

## 5. ELA and Metadata/EXIF

ELA uses controlled JPEG quality-90 recompression and reports descriptive difference statistics with a visualization. In controlled examples, original/amount-edited means were 0.8172/0.8241, while a resized original was 1.0708, demonstrating false-positive risk. Metadata reports available headers only. Missing EXIF is common for screenshots and is not manipulation evidence.

## 6. Grad-CAM

Grad-CAM uses `resnet.layer4[-1].conv2`, ResNet-18's final convolution before pooling. Outputs for the false-positive original `img_049` and correctly predicted modified `img_050` are in `results/gradcam/`. It shows model-contributing regions, not manipulated regions or fraud proof.

## 7. Ablation

**Incomplete.** Person 1 has no integration or ensemble outputs in the repository, so CNN-only/rules-only/forensics-only and combined-system measurements cannot be computed under a common protocol. No ablation metrics were fabricated. `results/metrics/ablation_results.csv` and `ablation_report.md` are intentionally not created until these inputs exist.

## 8. Integration and Validation

Use `PERSON_3_SANJAY.src.api.predict` and `analyze_image`; exact contracts are in `INTEGRATION.md`. The API returns unavailable/error states without fabricating predictions. Person 1's app launch was not testable because its directory contains no application files.

## 9. Limitations and Future Work

The test set is tiny, synthetic, and imbalanced (3 originals, 9 modified), with no correctly classified originals. Use a larger consented dataset, external templates, calibrated evaluation, and a measured common-protocol ablation after Person 1 integration is available. CNN predictions and forensic indicators must remain cautious supporting evidence.
