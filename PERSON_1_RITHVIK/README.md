# Person 1 (Rithvik) — Frontend, System Integration & Orchestration Subsystem
**UPI Transaction Fraud Forensics Platform (IDP)**  
*B.Tech CSE (AI & ML), SCOPE · VIT Chennai · Academic Project*

---

## 📌 Subsystem Overview

Person 1 owns the end-to-end frontend user interface, multi-modal integration pipeline, asynchronous orchestration, and unified forensic report generation for the UPI Fraud Forensics Platform. This subsystem integrates the OCR & Rule Validation Engine from **Person 2 (Nivash)** and the CNN Classifier, ELA, and Metadata Forensics from **Person 3 (Sanjay)** into an interactive, intuitive web dashboard.

---

## 🚀 Phase Progress Dashboard

| Phase | Title | Status | Description & Key Deliverables |
|:---:|:---|:---:|:---|
| **Phase 1** | Collaborative GitHub Repository Setup | **Completed (Skipped / Pre-existing)** | Initialized collaborative GitHub repository (`rithvikhere/elenxis`), standardized three-contributor workspace structure (`PERSON_1_RITHVIK`, `PERSON_2_NIVASH`, `PERSON_3_SANJAY`), established branching strategy and contribution guidelines. |
| **Phase 2** | Independent Environment & Teammate Module Verification | **Completed (100%)** | Verified Python 3.13 environment, installed project dependencies (`torch`, `torchvision`, `pytest`, `pytesseract`, `pillow`, `pandas`, `scikit-learn`, `matplotlib`), installed standalone Tesseract-OCR (v5.5.3) on system PATH, verified Person 2's OCR & Rule Engine, trained & evaluated Person 3's ResNet-18 baseline checkpoint (`resnet18_baseline_best.pt`), documented in verification reports. |
| **Phase 3** | Streamlit Web App Skeleton & Validation Pipeline | **Completed (100%)** | Built root `app.py` Streamlit web interface with wide layout, screenshot uploader (`.png`, `.jpg`, `.jpeg`), robust Pillow image integrity validation, preview render, local temp storage (`PERSON_1_RITHVIK/temp/`), "Analyze Screenshot" action button with placeholder triggers, neutral empty states, and automated 5-scenario test suite (`test_app.py`). |
| **Phase 4** | Person 2 Module Integration (OCR + Rule Engine) | **Completed (100%)** | Replaced placeholder button with live calls to `extract_transaction_fields` and `validate_transaction`. Rendered structured "OCR Extracted Fields" (with defensive "Not detected" formatting) and "Rule Validation" sections (verdict, anomaly score, and comprehensive 11-point heuristic explanations list), wrapped in resilient exception guards ("Not available yet"). |
| **Phase 5** | Forensic Dashboard UI & Unified Reporting (Person 3 Integration) | *Upcoming* | Wire Person 3's `analyze_image` / `predict` / Grad-CAM into an end-to-end execution flow. Render structured forensic cards (CNN prediction confidence, ELA heatmaps, Grad-CAM overlays, and metadata breakdown) with downloadable forensic summary reports. |

---

## 📂 Subsystem Directory Structure

```
PERSON_1_RITHVIK/
├── README.md                  # Subsystem documentation & phase progress tracker
├── test_app.py                # Automated Streamlit AppTest verification suite (pytest)
├── temp/                      # Local transient directory for uploaded screenshots
│   ├── .gitkeep               # Tracks temp folder in git
│   └── (transient images)     # Ignored by .gitignore to prevent repo pollution
└── (upcoming integration modules for Phase 5)
```

Root-level files owned/managed:
```
D:\elenxis/
├── app.py                     # Streamlit web application entry point
├── pytest.ini                 # Root pytest configuration
└── .gitignore                 # Configured for virtualenvs, checkpoints, and temp uploads
```

---

## 🛠️ Detailed Breakdown of Completed Phases

### Phase 1: Collaborative Repository Scaffolding
- Established remote repository at `https://github.com/rithvikhere/elenxis.git`.
- Enforced strict contributor boundary isolation: all frontend and integration work is strictly confined to `PERSON_1_RITHVIK/` and root `app.py`, leaving `PERSON_2_NIVASH/` and `PERSON_3_SANJAY/` completely untouched.

### Phase 2: Independent Environment & Subsystem Verification
- **Python Runtime**: Python 3.13.0rc2 executed via Windows `py` launcher.
- **OCR Engine**: Installed standalone Tesseract-OCR v5.5.3 binary to `C:\Program Files\Tesseract-OCR\tesseract.exe` and added to system PATH.
- **Deep Learning Baseline**: Executed training for Person 3's ResNet-18 classifier baseline (10 epochs, CPU):
  - Achieved Validation Loss: `0.5208`, F1-score: `0.8571`, Recall: `1.0000`.
  - Generated `PERSON_3_SANJAY/models/resnet18_baseline_best.pt` (preserved locally, gitignored under `*.pt`).
  - Confirmed both teammate test suites and empirical benchmarks were fully functional.

### Phase 3: Streamlit Web App Skeleton
- **Application Core (`app.py`)**:
  1. **Page Config**: Configured with `st.set_page_config(page_title="UPI Fraud Forensics", layout="wide")`.
  2. **Header & Subtitle**: Clear project branding with `st.title` and `st.caption` explaining the platform scope.
  3. **File Uploader**: `st.file_uploader` restricted strictly to `["png", "jpg", "jpeg"]`.
  4. **Defensive Validation**: Two-stage Pillow validation (`Image.verify()` + `Image.load()`) to catch corrupted files, invalid file headers, and truncated bitstreams gracefully via `st.error` without causing application crashes.
  5. **Preview Component**: Displays the uploaded receipt image at a fixed width (`450px`) with caption.
  6. **Disk Persistence for Downstream Modules**: Uploaded files are written to `PERSON_1_RITHVIK/temp/uploaded_screenshot<ext>` to provide stable file path strings for Person 2 & Person 3 modules in Phase 4/5.
  7. **Action Button & Empty States**: "Analyze Screenshot" button appears only upon valid upload, showing a placeholder notice. If no file is selected, a neutral `st.info` guide is displayed.

### Phase 4: Person 2 Integration (OCR + Rule Engine)
- **Live Pipeline Execution**:
  1. **OCR Ingestion**: Calls `extract_transaction_fields(temp_image_path)` to extract raw text, confidence score, and structured transaction dictionary.
  2. **Rule Evaluation**: Passes OCR extraction into `validate_transaction(ocr_output)` to evaluate against 11 format, range, and temporal heuristic rules.
  3. **OCR Extracted Fields Display**: Cleanly renders extracted transaction data: Amount, Date, Time, UTR (`transaction_id`), Template (`template_type`), and Recipient. Any missing or empty field strictly displays the literal string `"Not detected"`.
  4. **Rule Validation Display**: Renders rule engine outcome:
     - Verdict (`LIKELY_LEGITIMATE` / `SUSPICIOUS` / `UNREADABLE`)
     - Anomaly/Suspicion Score (formatted to 2 decimal places, e.g. `0.27`)
     - Heuristic Audit Explanations List (comprehensive itemized checklist of rule violations, warnings, and passed checks).
  5. **Fault Isolation**: Both module calls are wrapped in robust exception handling logging tracebacks to `sys.stderr` while cleanly rendering `"Not available yet"` in the UI without crashing.

---

## 🧪 Testing & Verification

A dedicated automated test suite was implemented in `PERSON_1_RITHVIK/test_app.py` utilizing Streamlit's official `AppTest` framework (`streamlit.testing.v1.AppTest`) and executed via `pytest`:

```powershell
py -m pytest PERSON_1_RITHVIK\test_app.py -v
```

### Verification Matrix

| Test Case | Scenario | Expected Behavior | Result |
|---|---|---|:---:|
| `test_initial_state` | Fresh page load (no file) | Neutral info message, file uploader visible, 0 buttons, 0 errors | **PASSED** |
| `test_valid_png_upload_and_analysis` | Uploading valid `.png` & clicking Analyze | Executes Person 2 OCR + Rules; renders all fields, score, and rule explanations | **PASSED** |
| `test_valid_jpg_upload` | Uploading valid `.jpg` image | Image preview rendered, button visible | **PASSED** |
| `test_corrupted_file_upload` | Uploading non-image/corrupted file | `st.error` displayed, no preview, no button, no crash | **PASSED** |
| `test_file_removal` | Uploading then clicking remove (`✕`) | Clean reset to empty neutral state without errors | **PASSED** |
| `test_exception_fallback` | Simulated module error/exception | Displays "Not available yet" cleanly in UI; zero unhandled crashes | **PASSED** |

---

## 🏃 How to Run Locally

### 1. Launch the Web Application
From the repository root (`D:\elenxis`):
```powershell
py -m streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.

### 2. Run Subsystem Unit Tests
```powershell
py -m pytest PERSON_1_RITHVIK\test_app.py -v
```
