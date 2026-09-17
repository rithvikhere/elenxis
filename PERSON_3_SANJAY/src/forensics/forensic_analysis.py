"""Unified, evidence-only image-forensics wrapper."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .ela import analyze_ela
from .metadata import inspect_metadata


def analyze_image(image_input: Any, ela_output_dir: Optional[Union[str, Path]] = None,
                  quality: int = 90) -> Dict[str, Any]:
    """Collect raw ELA and metadata evidence without producing a fraud decision."""
    ela = analyze_ela(image_input, quality=quality, output_dir=ela_output_dir)
    metadata = inspect_metadata(image_input)
    available = ela["status"] == "available" or metadata["status"] == "available"
    return {
        "status": "available" if available else "error", "available": available,
        "ela": ela, "metadata": metadata,
        "warnings": [*ela.get("warnings", []), *metadata.get("warnings", [])],
        "explanation": (
            "These are image-level indicators for inspection. They do not determine whether a financial transaction occurred, "
            "whether an image was manipulated, or whether fraud occurred."
        ),
    }
