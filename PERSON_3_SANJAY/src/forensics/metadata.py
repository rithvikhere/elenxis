"""Conservative image-header, metadata, and EXIF inspection."""

from pathlib import Path
from typing import Any, Dict

from PIL import ExifTags, Image


def inspect_metadata(image_input: Any) -> Dict[str, Any]:
    """Inspect only fields actually present; missing EXIF is not manipulation evidence."""
    input_path = str(image_input) if isinstance(image_input, (str, Path)) else None
    try:
        if isinstance(image_input, (str, Path)):
            path = Path(image_input)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            source, file_size = path, path.stat().st_size
        else:
            source, file_size = image_input, None
        with Image.open(source) as image:
            image.load()
            exif_tags = {ExifTags.TAGS.get(key, str(key)): str(value) for key, value in image.getexif().items()}
            info_fields = {str(key): str(value) for key, value in image.info.items()}
            timestamps = {key: exif_tags[key] for key in ("DateTime", "DateTimeOriginal", "DateTimeDigitized") if key in exif_tags}
            warnings = []
            if not exif_tags:
                warnings.append("No EXIF metadata is available; screenshots and shared images commonly have no EXIF.")
            return {
                "status": "available", "input_path": input_path, "file_format": image.format,
                "dimensions": {"width": image.width, "height": image.height}, "file_size_bytes": file_size,
                "metadata_present": bool(exif_tags or info_fields), "has_exif": bool(exif_tags),
                "exif_fields": exif_tags, "image_info_fields": info_fields,
                "software": exif_tags.get("Software") or info_fields.get("Software"),
                "timestamps": timestamps, "warnings": warnings,
                "explanation": "Metadata availability is descriptive only; missing EXIF is not evidence of manipulation.",
            }
    except Exception as error:
        return {
            "status": "error", "input_path": input_path, "file_format": None, "dimensions": None,
            "file_size_bytes": None, "metadata_present": False, "has_exif": False,
            "exif_fields": {}, "image_info_fields": {}, "software": None, "timestamps": {},
            "warnings": ["Metadata could not be read from this input."],
            "explanation": "Metadata inspection is unavailable for this input.", "error": str(error),
        }
