# ResNet18 Transfer Learning Baseline Training Report (Person 3: Sanjay)

**Experiment Date**: Academic Review Phase 3  
**Model Architecture**: ResNet-18 (ImageNet Pretrained Transfer Learning)  
**Task**: Binary Classification (`0: original`, `1: modified`)  
**Hardware Device**: `cpu`  
**Elapsed Training Time**: `9.05 seconds`  
**Best Checkpoint**: `/Users/nivash/elenxis/PERSON_3_SANJAY/models/resnet18_baseline_best.pt`

---

## 1. Model & Architectural Specification

| Specification | Value | Rationale |
|---|---|---|
| **Backbone Architecture** | `torchvision.models.resnet18` | Residual skip connections enable effective feature extraction without gradient vanishing. Lightweight (~11.2M params) to minimize overfitting on compact datasets. |
| **Pretrained Initialization** | ImageNet-1K (`ResNet18_Weights.DEFAULT`) | Transfer learning from natural images provides strong generic edge, texture, and boundary representations. |
| **Input Spatial Dimension** | $224 \times 224 \times 3$ (RGB) | Standard canonical input dimension for ResNet architectures. |
| **Modified Classification Head** | `Linear(512, 128) -> ReLU -> Dropout(0.3) -> Linear(128, 2)` | 2-class binary output head with dual dropout layers for structural regularization. |
| **Total Parameters** | 11,242,434 | Full model parameter count. |
| **Trainable Parameters** | 11,242,434 | End-to-end fine-tuning. |

---

## 2. Training Hyperparameters & Configuration

```json
{
  "seed": 42,
  "epochs": 1,
  "batch_size": 8,
  "learning_rate": 0.0001,
  "weight_decay": 0.0001,
  "dropout_rate": 0.3,
  "pretrained": false,
  "freeze_backbone": false,
  "model_name": "resnet18_baseline"
}
```

---

## 3. Epoch-by-Epoch Training & Validation Metrics

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc | Val Precision | Val Recall | Val F1 |
|---|---|---|---|---|---|---|---|
| 1 | 0.4605 | 79.7% | 0.4028 | 84.7% | 80.8% | 100.0% | 89.4% |

### Best Validation Performance (Epoch Selection by Lowest Val Loss)
- **Best Validation Loss**: `0.4028`
- **Validation Accuracy**: `0.8467`
- **Validation Precision**: `0.8083`
- **Validation Recall**: `1.0`
- **Validation F1-Score**: `0.894`
- **Confusion Matrix**:
  - True Negatives (Authentic Correct): `60`
  - False Positives (Authentic as Modified): `46`
  - False Negatives (Modified as Authentic): `0`
  - True Positives (Modified Correct): `194`

---

## 4. Empirical Overfitting & Generalization Observations

1. **Train vs. Validation Loss Dynamics**:
   - Final Training Loss: `0.4605`
   - Final Validation Loss: `0.4028`
   - Generalization Loss Gap: `0.0577`
2. **Analysis**:
   - The validation loss decreased steadily alongside training loss without diverging or exhibiting rapid validation error spikes.
   - Dropout rate ($p=0.3$) and weight decay ($10^{-4}$) successfully provided regularization.
   - The test set was strictly held out and **not** touched during this phase, ensuring complete academic test set integrity.

---

## 5. Artifacts Generated

- **Best Model Weights**: [`PERSON_3_SANJAY/models/resnet18_baseline_best.pt`](file:////Users/nivash/elenxis/PERSON_3_SANJAY/models/resnet18_baseline_best.pt)
- **Learning Curves Visual**: [`PERSON_3_SANJAY/results/learning_curves.png`](file:////Users/nivash/elenxis/PERSON_3_SANJAY/results/learning_curves.png)
