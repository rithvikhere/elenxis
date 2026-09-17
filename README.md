# UPI Fraud Forensics Platform

## Project Overview

**Project title:** UPI Fraud Forensics Platform  
**Duration:** 12 months  
**Current stage:** 30% progress  
**Project type:** Image-based payment screenshot authenticity and fraud-forensics analysis platform

## Team

| Member | Responsibility |
|---|---|
| **Rithvik** | Project lead, Streamlit frontend, integration, ensemble orchestration, deployment, documentation, final demo |
| **Sanjay** | Dataset preparation, preprocessing, OCR, transaction-field extraction, rule engine |
| **Nivash** | CNN model, image forensics, evaluation, explainability |

---

# 1. Problem Statement

UPI payment screenshots are often shared as proof of payment. However, screenshots can be edited, recreated, or manipulated. Possible changes may involve the amount, transaction ID, UPI ID, date, time, payment status, names, font rendering, layout, compression, or image regions.

Manual inspection is unreliable, especially when the manipulation is subtle. This project aims to build a modular platform that analyzes screenshots for authenticity-related signals using OCR, rule-based validation, image forensics, CNN-based visual analysis, and an ensemble decision layer.

The platform is an investigation-support tool. It must not claim to verify that a real bank transaction occurred solely from an image.

# 2. Main Objectives

- Accept PNG, JPG, and JPEG screenshots.
- Extract visible transaction information using OCR.
- Validate extracted fields using logical rules.
- Detect suspicious image-level manipulation signals.
- Train and use a CNN for visual classification when sufficient data is available.
- Combine available module outputs through an explainable ensemble layer.
- Display individual results, reasons, missing evidence, and limitations.
- Handle incomplete or unavailable modules without crashing.
- Provide a clean Streamlit interface for demonstration.
- Maintain a reproducible and academically honest workflow.

# 3. Scope of the Current 30% Stage

The 30% milestone focuses on establishing the foundation of the complete system rather than completing every advanced model.

Expected progress:

- Repository organization and team ownership.
- Basic Streamlit frontend.
- Image upload and preview.
- Initial integration architecture.
- Defined module contracts.
- Initial OCR and rule-engine work by Sanjay.
- Initial image-forensics and CNN work by Nivash.
- Early result display by Rithvik.
- Initial ensemble design.
- Basic testing and documentation.
- Safe demonstration using synthetic or fictional data.

Unimplemented modules must be shown as `Not available yet` or `Insufficient evidence`. No fabricated outputs, accuracy values, or model claims may be added.

# 4. High-Level Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  v
Image Upload and Validation
  |
  +-------------------------+
  |                         |
  v                         v
OCR Module             Image Forensics Module
  |                         |
  v                         v
Extracted Fields       Forensic Signals
  |
  v
Rule Engine
  |
  +-------------+-----------+
                |
                v
            CNN Model
                |
                v
          Ensemble Layer
                |
                v
      Combined Assessment
                |
                v
       Reasons and Results
```

The modules should remain independent. Each module should have a predictable input and output so that improvements can be made without rewriting the entire application.

# 5. Work of Rithvik

## Role

Rithvik is responsible for project leadership, frontend development, integration, ensemble orchestration, deployment preparation, documentation, and the final demonstration.

## 30% Responsibilities

### Streamlit Frontend

- Create the main Streamlit application.
- Add project title and description.
- Add PNG/JPG/JPEG upload control.
- Validate uploaded files.
- Display the uploaded screenshot.
- Add an Analyze button.
- Create result sections for OCR, rules, forensics, CNN, and ensemble output.
- Display module availability clearly.
- Add error messages without exposing confusing technical traces to users.
- Include the project disclaimer.

### Integration

- Connect Sanjay's OCR and rule-engine modules.
- Connect Nivash's forensics and CNN modules.
- Normalize different output formats through adapters.
- Ensure the application continues working if one module is unavailable.
- Keep individual module outputs visible before showing the combined assessment.

### Ensemble Orchestration

- Define the combined result schema.
- Keep component scores/signals separate.
- Use configurable weights only when justified.
- Avoid treating missing evidence as fraud evidence.
- Avoid simple OR logic.
- Generate reasons and limitations.
- Use cautious assessment labels rather than absolute claims.

### Documentation and Deployment

- Maintain the main README.
- Document architecture and data flow.
- Document setup and run commands.
- Maintain progress tracking.
- Prepare local deployment and later hosting instructions.
- Test the complete workflow before the review.

## Suggested Rithvik Output

```python
{
    "ocr": {},
    "rules": {},
    "forensics": {},
    "cnn": {},
    "ensemble": {},
    "errors": [],
    "limitations": []
}
```

# 6. Work of Sanjay

## Role

Sanjay owns dataset preparation, image preprocessing, OCR, transaction-field extraction, and rule-based validation.

## 30% Responsibilities

### Dataset Preparation

- Create or organize a safe dataset.
- Use synthetic, fictional, public, or properly consented screenshots.
- Define labels and folder conventions.
- Record image sources and limitations.
- Separate training, validation, and test data when experiments begin.

### Preprocessing

Possible preprocessing steps include:

- Resizing when appropriate.
- Grayscale conversion.
- Contrast enhancement.
- Noise reduction.
- Cropping or region selection.
- Thresholding for OCR experiments.
- Preserving an original copy for forensics.

Preprocessing should be documented because aggressive processing may remove evidence of manipulation.

### OCR

The OCR module should attempt to extract visible fields such as:

- Amount
- Transaction ID
- UPI ID
- Sender name
- Receiver name
- Date
- Time
- Payment status
- Reference number
- Raw text

Missing fields must be returned as missing. They must not be guessed.

### Suggested OCR Contract

```python
def extract_transaction_fields(image) -> dict:
    """Extract visible transaction fields and OCR metadata."""
```

Suggested output:

```python
{
    "amount": None,
    "transaction_id": None,
    "upi_id": None,
    "sender": None,
    "receiver": None,
    "date": None,
    "time": None,
    "status": None,
    "raw_text": "",
    "confidence": None,
    "missing_fields": []
}
```

### Rule Engine

The rule engine may check:

- Amount format.
- Transaction ID pattern.
- UPI ID structure.
- Date and time format.
- Presence of payment status.
- Missing required fields.
- Conflicting or inconsistent extracted values.
- Suspicious text patterns.

Rules produce warnings and signals. They do not prove that a screenshot is fraudulent.

Suggested contract:

```python
def validate_transaction(data: dict) -> dict:
    """Validate OCR-extracted fields and return checks and reasons."""
```

Suggested output:

```python
{
    "status": "review",
    "risk_score": None,
    "checks": [],
    "warnings": [],
    "reasons": [],
    "missing_fields": []
}
```

Possible statuses:

- `pass`
- `review`
- `unavailable`

# 7. Work of Nivash

## Role

Nivash owns CNN development, image-forensics analysis, evaluation, and explainability.

## 30% Responsibilities

### CNN Development

- Define the image dataset format.
- Define labels and class meanings.
- Implement image preprocessing for the CNN.
- Select an initial CNN architecture.
- Create a basic training pipeline.
- Save model configuration and version information.
- Prepare an evaluation script.

The CNN should not be presented as reliable until it has been trained and evaluated on appropriate data.

### Image Forensics

Initial analysis may investigate:

- Error Level Analysis.
- Local compression inconsistencies.
- Text-region irregularities.
- Noise-pattern differences.
- Copy-paste-like regions.
- Edge or boundary inconsistencies.
- Differences in image quality across regions.
- Suspicious layout or rendering artifacts.

These are only signals. Legitimate screenshots can also show artifacts because of resizing, messaging-app compression, screenshots of screenshots, or image conversion.

Suggested contract:

```python
def analyze_image(image) -> dict:
    """Return image-forensics signals and explanations."""
```

### CNN Contract

```python
def predict(image) -> dict:
    """Return CNN prediction information when a trained model is available."""
```

Suggested output:

```python
{
    "label": None,
    "probability": None,
    "model_version": None,
    "available": False,
    "reasons": []
}
```

### Evaluation

Future evaluation should include:

- Train/validation/test split.
- Accuracy.
- Precision.
- Recall.
- F1-score.
- Confusion matrix.
- Class distribution.
- False-positive analysis.
- False-negative analysis.
- Testing on unseen images.
- Dataset and generalization limitations.

Only experimentally obtained results may be included in the report.

# 8. Module Contracts and Adapters

The integration layer should expect stable functions:

```python
def extract_transaction_fields(image) -> dict:
    pass

def validate_transaction(data: dict) -> dict:
    pass

def analyze_image(image) -> dict:
    pass

def predict(image) -> dict:
    pass
```

If a member uses a different function name or return format, Rithvik should create an adapter rather than forcing major rewrites.

Example:

```python
def run_ocr_adapter(image):
    result = extract_transaction_fields(image)
    return normalize_ocr_result(result)
```

# 9. Ensemble and Final Decision Layer

## Purpose

The ensemble layer combines available outputs from:

- OCR and rule validation.
- Image forensics.
- CNN prediction.

It should first display individual outputs and then provide a cautious combined assessment.

## Required Behavior

- Show each module's result separately.
- Show available and missing modules.
- Normalize scores only when necessary and document the method.
- Use configurable weights.
- Do not claim unsupported optimal weights.
- Do not use a simple OR rule.
- Do not treat missing modules as suspicious evidence.
- Do not hide uncertainty.
- Include reasons and limitations.
- Return `unavailable` or `insufficient evidence` when meaningful evidence is absent.

## Suggested Output

```python
{
    "ocr_rule_score": None,
    "forensics_score": None,
    "cnn_score": None,
    "available_modules": [],
    "missing_modules": [],
    "weights": {},
    "combined_score": None,
    "assessment": "unavailable",
    "reasons": [],
    "limitations": []
}
```

## Suggested Assessment Labels

- `No strong suspicious signal`
- `Needs review`
- `Suspicious signals detected`
- `Insufficient evidence`
- `Module unavailable`

Avoid absolute labels such as `Definitely fake`, `Definitely genuine`, `Confirmed fraud`, or `Verified payment`.

## Future Ensemble Work

After real outputs and evaluation data exist, the team may investigate:

- Score normalization.
- Probability calibration.
- Data-driven weights.
- Threshold selection.
- Validation-set tuning.
- Ablation studies.
- Comparison of individual modules against the ensemble.
- False-positive and false-negative analysis.

These should be marked as future work unless actually completed.

# 10. Repository Organization

The current repository is organized around three ownership folders:

```text
PERSON_1_RITHVIK/
PERSON_2_NIVASH/
PERSON_3_SANJAY/
```

Each member should mainly push work into their assigned folder. Any later restructuring into a common production structure should be discussed before implementation.

# 11. Data Safety and Ethics

Use only:

- Synthetic screenshots.
- Fictional transaction details.
- Publicly usable datasets.
- Properly consented examples.
- Clearly marked artificial test images.

Do not use real private financial information, personal bank statements, real UPI IDs, private transaction IDs, phone numbers, passwords, API keys, or authentication data.

The application must display:

> This platform analyzes screenshot authenticity signals and does not verify whether a bank transaction actually occurred. Results are for research and investigation support only.

The project must not create screenshots intended to be used as proof of payment.

# 12. Error Handling

The application should safely handle:

- Unsupported file types.
- Corrupt images.
- Empty uploads.
- OCR failure.
- Missing OCR fields.
- Rule-engine failure.
- Missing CNN model.
- Untrained CNN model.
- Forensics failure.
- Invalid module output.
- Missing dependencies.
- Unexpected exceptions.

A missing module must not crash the application or automatically increase the fraud assessment.

# 13. Testing Plan for 30%

## Frontend

- Streamlit launches.
- Supported images upload correctly.
- Unsupported files are rejected safely.
- Uploaded image is displayed.
- Analyze button works.
- Result sections render.
- Missing modules are clearly indicated.

## Sanjay's Modules

- OCR accepts an image.
- Raw text is returned.
- Visible fields are extracted when possible.
- Missing fields are handled.
- Rule checks return warnings and reasons.
- Invalid input does not crash the app.

## Nivash's Modules

- Forensics accepts different image sizes.
- ELA or other methods return structured output.
- CNN loading failure is handled.
- Prediction schema is consistent.
- Evaluation metrics are generated only from real experiments.

## Integration

- All available modules can be called.
- Outputs are normalized.
- Ensemble receives valid outputs.
- Missing modules are handled correctly.
- Individual results remain visible.
- Final assessment includes reasons and limitations.

# 14. Documentation Requirements

The project should maintain:

- Main README.
- Architecture document.
- Methodology document.
- Setup and run instructions.
- Progress tracker.
- Testing notes.
- Known limitations.
- Dataset documentation.
- Model and evaluation documentation.

Progress tracking should record:

- Task.
- Owner.
- Status.
- Files changed.
- Tests performed.
- Limitations.
- Next step.

A task should not be marked complete only because code was generated. It should be tested and reviewed first.

# 15. 30% Demonstration Flow

1. Introduce the problem of manipulated payment screenshots.
2. Explain the system architecture.
3. Explain the three team members' responsibilities.
4. Open the Streamlit application.
5. Upload a synthetic or fictional screenshot.
6. Display OCR output.
7. Display rule-engine checks.
8. Display image-forensics signals.
9. Display CNN status or prediction if available.
10. Display the ensemble assessment.
11. Explain the reasons and limitations.
12. Demonstrate safe handling of unavailable modules.
13. Show the disclaimer.
14. Explain current limitations and next steps.

# 16. Current Limitations

At 30%, the project may have:

- A small dataset.
- OCR errors on low-quality images.
- Missing or incorrect extracted fields.
- False positives from rule checks.
- Forensics signals affected by compression.
- An untrained or preliminary CNN.
- Uncalibrated model probabilities.
- Preliminary ensemble weights.
- Limited generalization across UPI applications.
- No access to bank-side transaction records.

A screenshot alone cannot conclusively establish fraud.

# 17. Future Roadmap

## Phase 1 — Foundation and 30% Review

- Repository setup.
- Team ownership.
- Basic Streamlit frontend.
- Initial OCR and rules.
- Forensics prototype.
- CNN setup.
- Module contracts.
- Ensemble design.
- Basic integration.
- Documentation and safe demo.

## Phase 2 — Functional Development

- Improve OCR accuracy.
- Expand field extraction.
- Add validation rules.
- Improve preprocessing.
- Strengthen forensics.
- Train initial CNN.
- Connect real outputs.

## Phase 3 — Integration and Explainability

- Normalize scores.
- Improve ensemble logic.
- Add explanations.
- Add Grad-CAM or similar methods.
- Add automated tests.
- Compare module performance.

## Phase 4 — Evaluation and Calibration

- Expand dataset.
- Use proper data splits.
- Tune thresholds using validation data.
- Calibrate probabilities where appropriate.
- Run ablation studies.
- Analyze false positives and false negatives.
- Benchmark individual modules and ensemble.

## Phase 5 — Deployment and Final Demonstration

- Improve UI.
- Prepare deployment.
- Finalize documentation.
- Perform end-to-end testing.
- Prepare demonstration data.
- Prepare presentation.
- Explain limitations and ethical considerations.

# 18. Features Outside the Current Scope

Do not add these unless specifically requested:

- GAN-based screenshot generation.
- Chatbot functionality.
- Banking API integration.
- Live UPI transaction verification.
- Access to bank accounts.
- Unnecessary cloud infrastructure.
- Unrelated payment-processing features.
- Features that create deceptive proof-of-payment screenshots.

# 19. Definition of Done for 30%

The project is ready for the 30% review when:

- The three team folders exist.
- Responsibilities are clearly assigned.
- Streamlit launches locally.
- An image can be uploaded and displayed.
- An analyze workflow exists.
- OCR and rule-engine interfaces are defined.
- Forensics and CNN interfaces are defined.
- Available outputs are displayed.
- Missing modules do not crash the app.
- Ensemble behavior is documented.
- Individual signals remain visible.
- The final assessment is cautious and explainable.
- No fabricated results are shown.
- Synthetic or fictional data is used.
- The disclaimer is visible.
- Basic tests have been performed.
- Setup instructions are documented.
- Limitations are recorded.
- Each member can explain their contribution.

# 20. Final Project Statement

The UPI Fraud Forensics Platform is a modular research-oriented system for analyzing authenticity-related signals in payment screenshots. It combines text extraction, rule-based validation, image forensics, CNN-based visual analysis, and ensemble reasoning.

At the current 30% stage, the priority is to establish a clean and understandable foundation, connect the three members' work, and demonstrate a safe end-to-end workflow without overstating the reliability of incomplete models.

The final system should support human investigation by presenting evidence, signals, explanations, and limitations rather than claiming to independently verify a real financial transaction.

