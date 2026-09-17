# UPI Fraud Forensics Platform — Architecture Document (Person 3: Sanjay)

## 1. Project Purpose & Academic Scope

The **UPI Fraud Forensics Platform** is an interdisciplinary research and investigation platform designed to analyze digital payment-success screenshots (e.g., Google Pay, PhonePe, Paytm) for potential indicators of image manipulation, digital tampering, or structural inconsistency.

### Critical Academic Stance & Disclaimers
In compliance with academic forensics standards:
- The system **does NOT verify whether an actual financial transaction occurred**.
- The system analyzes visual and structural characteristics of the digital image artifact.
- **Forbidden Claims**: Never claim *"Payment definitely occurred"*, *"Payment definitely did not happen"*, or *"This screenshot proves fraud"*.
- **Approved Cautious Terminology**:
  - *"The model predicts the image as modified / original with confidence score $X$."*
  - *"The image contains visual signals associated with the learned classes."*
  - *"Error Level Analysis (ELA) indicates compression rate differences that warrant inspection."*
  - *"Metadata information is unavailable / indicates editing software signature."*

---

## 2. Team Ownership & Responsibilities

| Team Member | Core Domain | Key Responsibilities |
|---|---|---|
| **Person 1 (Rithvik)** | System Integration & Frontend | Streamlit Web UI, Ensemble Decision Orchestration, API integration adapters, deployment. |
| **Person 2 (Nivash)** | Data & Textual Consistency | Synthetic/consented dataset creation, OCR text extraction pipeline, rule-based logical consistency engine. |
| **Person 3 (Sanjay - Current)** | Visual Forensics & Deep Learning | CNN model development, Transfer Learning, Error Level Analysis (ELA), EXIF/Metadata inspection, Model evaluation metrics, Error analysis, Future Grad-CAM, Clean Forensics APIs. |

### Relationships & Interfaces
- **Relationship with Person 2 (Data & OCR)**: Person 3 receives labeled image datasets (real/synthetic screenshot pairs) formatted by Person 2 to train and evaluate CNN models. Person 3's visual models operate independently of OCR text extraction to provide orthogonal, uncorrelated signals.
- **Relationship with Person 1 (Frontend & Integration)**: Person 3 exposes clean, resilient, standardized Python functions (`analyze_image(image)`, `predict(image)`) that Person 1's ensemble orchestration layer can invoke safely without fear of crashes or unhandled exceptions.

---

## 3. High-Level Architecture Overview

```text
                           +---------------------------+
                           |   Input Screenshot Image   |
                           +-------------+-------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
               v                                                   v
   +-----------------------+                           +-----------------------+
   |  Image Forensics      |                           |  CNN Visual Analysis  |
   |  Pipeline             |                           |  Pipeline             |
   +-----------+-----------+                           +-----------+-----------+
               |                                                   |
       +-------+-------+                                   +-------+-------+
       |               |                                   |               |
       v               v                                   v               v
+-------------+ +---------------+                  +---------------+ +---------------+
| ELA Module  | | Metadata/EXIF |                  | Preprocessing | | Transfer      |
| Computation | | Inspection    |                  | & Normalizing | | Learning CNN  |
+------+------+ +-------+-------+                  +-------+-------+ +-------+-------+
       |                |                                  |                 |
       +-------+--------+                                  +--------+--------+
               |                                                    |
               v                                                    v
      Forensic Indicators                                   Model Predictions
      (Artifacts & Signals)                                 (Class & Probability)
               |                                                    |
               +-------------------------+--------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Clean Person 3 API Boundary  |
                         |   - analyze_image()           |
                         |   - predict()                 |
                         +---------------+---------------+
                                         |
                                         v
                     +---------------------------------------+
                     |  Person 1: Ensemble & UI Presentation  |
                     +---------------------------------------+
```

---

## 4. CNN & Visual Classification Pipeline

### 4.1 Pipeline Stages
1. **Dataset Ingestion**: Pairs of real and synthetically manipulated screenshots loaded via standard PyTorch `Dataset` and `DataLoader` abstractions.
2. **Preprocessing & Augmentation**:
   - Resolution normalization (e.g., $224 \times 224$ or $256 \times 256$ RGB).
   - Standard ImageNet normalization: $\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$.
   - Orientation & color space consistency checks.
3. **Model Backbone**:
   - Baseline: Lightweight custom CNN or fine-tuned ResNet-18 / ResNet-50 / EfficientNet backbone.
   - Binary output head: Softmax / Sigmoid for class probability estimation (Original vs. Synthesized/Modified).
4. **Prediction Output Contract**:
   ```python
   {
       "label": "original" | "modified" | None,
       "probability": float | None,
       "model_version": "v1.0.0-baseline",
       "available": bool,
       "reasons": list[str]
   }
   ```
5. **Phase 1 Status**: Foundations and architecture skeleton built; training deferred until dataset curation and validation splits are finalized.

---

## 5. Image Forensics Pipeline

### 5.1 Error Level Analysis (ELA)
- **Principle**: When a lossy image (JPEG) is resaved at a known quality level (e.g., 90%), unmodified regions compress uniformly, whereas spliced, edited, or re-rendered text blocks exhibit distinct error level differentials.
- **Implementation**:
  $$\text{ELA Map} = |\text{Original Image} - \text{Resaved JPEG Image}| \times \text{Scale Factor}$$
- **Extracted Metrics**:
  - `mean_error`: Average compression differential across the canvas.
  - `max_error`: Peak localized deviation.
  - `anomaly_score`: Normalized metric $[0.0, 1.0]$ representing high-frequency anomaly density.

### 5.2 Metadata & EXIF Analysis
- **Principle**: Inspect header markers for signatures left by image manipulation tools (Photoshop, Canva, PicsArt, Pixelcut, etc.), mismatched software tags, missing standard camera/screenshot markers, or suspicious creation/modification timestamps.
- **Forensic Limitations**: Modern mobile screenshots frequently have stripped EXIF headers during transmission (e.g., WhatsApp, Telegram compression). Absence of EXIF is treated as *inconclusive*, not proof of fraud.

---

## 6. Future Explainability: Grad-CAM Roadmap

- **Target Phase**: Phase 3 (after CNN weights are fully trained and validated).
- **Mechanism**: Gradient-weighted Class Activation Mapping (Grad-CAM) computes gradients of the target class score with respect to feature activation maps of the final convolutional layer.
- **Output**: Visual localization heatmaps indicating spatial regions that most influenced the classification decision (e.g., amount bounding box, timestamp area).

---

## 7. Evaluation & Error Analysis Methodology

To ensure academic rigor, model evaluation will report:
- **Primary Metrics**: Accuracy, Precision, Recall, F1-Score, ROC-AUC.
- **Confusion Matrix Analysis**:
  - **False Positives (Type I Error)**: Authentic screenshots flagged as modified (investigating causes: double-compression, dark mode, social media forwarding).
  - **False Negatives (Type II Error)**: Tampered screenshots flagged as authentic (investigating causes: high-quality vector recreation, subtle single-digit edits).
- **Ablation Studies (Phase 3/4)**: Measuring marginal detection improvement of Forensics alone vs. CNN alone vs. Multi-signal Ensemble.

---

## 8. Integration Boundary & Contract Compliance

Person 3 provides self-contained, defensive modules under `PERSON_3_SANJAY/src/`:
- Never raises uncaught exceptions to the calling orchestrator.
- Gracefully returns `available: False` when weights or optional dependencies are uninitialized.
- Fully compatible with Python 3.10–3.13 on both CPU and CUDA-enabled environments.
