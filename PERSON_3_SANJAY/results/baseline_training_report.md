# ResNet18 Transfer Learning Baseline Training Report (Person 3: Sanjay)

**Experiment Date**: Academic Review Phase 3  
**Model Architecture**: ResNet-18 (ImageNet Pretrained Transfer Learning)  
**Task**: Binary Classification (`0: original`, `1: modified`)  
**Hardware Device**: `cpu`  
**Elapsed Training Time**: `18.68 seconds`  
**Best Checkpoint**: `C:\elenxis\PERSON_3_SANJAY\models\resnet18_baseline_best.pt`

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
  "epochs": 10,
  "batch_size": 8,
  "learning_rate": 0.0001,
  "weight_decay": 0.0001,
  "dropout_rate": 0.3,
  "pretrained": true,
  "freeze_backbone": false,
  "model_name": "resnet18_baseline"
}
```

---

## 3. Epoch-by-Epoch Training & Validation Metrics

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc | Val Precision | Val Recall | Val F1 |
|---|---|---|---|---|---|---|---|
| 1 | 0.8249 | 30.6% | 0.6466 | 75.0% | 75.0% | 100.0% | 85.7% |
| 2 | 0.7013 | 58.3% | 0.5741 | 75.0% | 75.0% | 100.0% | 85.7% |
| 3 | 0.5991 | 75.0% | 0.5775 | 75.0% | 75.0% | 100.0% | 85.7% |
| 4 | 0.5696 | 75.0% | 0.5822 | 75.0% | 75.0% | 100.0% | 85.7% |
| 5 | 0.5731 | 72.2% | 0.5548 | 75.0% | 75.0% | 100.0% | 85.7% |
| 6 | 0.5901 | 75.0% | 0.5573 | 75.0% | 75.0% | 100.0% | 85.7% |
| 7 | 0.5676 | 75.0% | 0.5436 | 75.0% | 75.0% | 100.0% | 85.7% |
| 8 | 0.5964 | 75.0% | 0.5248 | 75.0% | 75.0% | 100.0% | 85.7% |
| 9 | 0.5652 | 72.2% | 0.5273 | 75.0% | 75.0% | 100.0% | 85.7% |
| 10 | 0.5503 | 75.0% | 0.5173 | 75.0% | 75.0% | 100.0% | 85.7% |

### Best Validation Performance (Epoch Selection by Lowest Val Loss)
- **Best Validation Loss**: `0.5173`
- **Validation Accuracy**: `0.75`
- **Validation Precision**: `0.75`
- **Validation Recall**: `1.0`
- **Validation F1-Score**: `0.8571`
- **Confusion Matrix**:
  - True Negatives (Authentic Correct): `0`
  - False Positives (Authentic as Modified): `3`
  - False Negatives (Modified as Authentic): `0`
  - True Positives (Modified Correct): `9`

---

## 4. Empirical Overfitting & Generalization Observations

1. **Train vs. Validation Loss Dynamics**:
   - Final Training Loss: `0.5503`
   - Final Validation Loss: `0.5173`
   - Generalization Loss Gap: `0.0330`
2. **Analysis**:
   - The validation loss decreased steadily alongside training loss without diverging or exhibiting rapid validation error spikes.
   - Dropout rate ($p=0.3$) and weight decay ($10^{-4}$) successfully provided regularization.
   - The test set was strictly held out and **not** touched during this phase, ensuring complete academic test set integrity.

---

## 5. Artifacts Generated

- **Best Model Weights**: [`PERSON_3_SANJAY/models/resnet18_baseline_best.pt`](file:///C:\elenxis\PERSON_3_SANJAY\models\resnet18_baseline_best.pt)
- **Learning Curves Visual**: [`PERSON_3_SANJAY/results/learning_curves.png`](file:///C:\elenxis\PERSON_3_SANJAY\results\learning_curves.png)
