"""Evaluate the completed CNN checkpoint on the isolated held-out test split.

This script intentionally has no training or tuning options.  It creates the
Phase 4 evaluation artifacts from a fixed checkpoint and the existing test split.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PERSON_3_SANJAY.src.model.evaluate import (
    evaluate_checkpoint_on_test_set,
    write_evaluation_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the held-out UPI screenshot test split.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO_ROOT / "PERSON_3_SANJAY" / "models" / "resnet18_baseline_best.pt",
        help="Previously trained checkpoint to evaluate.",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    evaluation = evaluate_checkpoint_on_test_set(
        checkpoint_path=args.checkpoint,
        metadata_csv=REPO_ROOT / "PERSON_2_NIVASH" / "data" / "metadata.csv",
        images_dir=REPO_ROOT / "PERSON_2_NIVASH" / "data" / "raw",
        batch_size=args.batch_size,
    )
    paths = write_evaluation_artifacts(
        evaluation,
        REPO_ROOT / "PERSON_3_SANJAY" / "results" / "metrics",
    )
    metrics = evaluation["metrics"]
    print(f"Evaluated {evaluation['test_count']} held-out test images.")
    print(f"Accuracy={metrics['accuracy']:.4f}, Precision={metrics['precision']:.4f}, "
          f"Recall={metrics['recall']:.4f}, F1={metrics['f1_score']:.4f}")
    print(f"Artifacts written to: {paths['report'].parent}")


if __name__ == "__main__":
    main()
