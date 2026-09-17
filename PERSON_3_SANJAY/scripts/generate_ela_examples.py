"""Generate controlled ELA examples from the existing synthetic dataset."""

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from PERSON_3_SANJAY.src.forensics.ela import analyze_ela


def main() -> None:
    raw = ROOT / "PERSON_2_NIVASH" / "data" / "raw"
    output = ROOT / "PERSON_3_SANJAY" / "results" / "ela"
    output.mkdir(parents=True, exist_ok=True)
    recompressed = output / "recompressed_original.jpg"
    resized = output / "resized_original.png"
    with Image.open(raw / "img_049.png") as image:
        image.convert("RGB").save(recompressed, quality=85)
        image.resize((270, 400)).save(resized)
    examples = {
        "original": raw / "img_049.png",
        "amount_modified": raw / "img_050.png",
        "recompressed": recompressed,
        "resized": resized,
    }
    results = {name: analyze_ela(path, output_dir=output) for name, path in examples.items()}
    (output / "ela_examples.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote ELA examples to {output}")


if __name__ == "__main__":
    main()
