"""Generate Grad-CAM examples from observed held-out evaluation categories."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from PERSON_3_SANJAY.src.explainability.gradcam import generate_gradcam


def main() -> None:
    output = ROOT / "PERSON_3_SANJAY" / "results" / "gradcam"
    checkpoint = ROOT / "PERSON_3_SANJAY" / "models" / "resnet18_baseline_best.pt"
    raw = ROOT / "PERSON_2_NIVASH" / "data" / "raw"
    examples = {
        "false_positive_original_img_049": raw / "img_049.png",
        "correct_modified_img_050": raw / "img_050.png",
    }
    results = {name: generate_gradcam(path, checkpoint, output) for name, path in examples.items()}
    results["unavailable_categories"] = {
        "correct_original": "None observed in the Phase 4 held-out evaluation.",
        "false_negative": "None observed in the Phase 4 held-out evaluation.",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "gradcam_examples.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote Grad-CAM examples to {output}")


if __name__ == "__main__":
    main()
