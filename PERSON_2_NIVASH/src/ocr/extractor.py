"""
Main OCR Extraction Pipeline.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Public API: extract_transaction_fields()

Key fix: uses PSM 3 (auto page segmentation) instead of PSM 6 so that
large centred bold amount text (e.g. ApexPay, NovaPay templates) is not
silently dropped by Tesseract's column-layout heuristic.
"""

from pathlib import Path
from typing import Any, Dict, Union

from PIL import Image
import pytesseract

from .preprocess import preprocess_image, load_image
from .field_parser import parse_all_fields


# Use PSM 3 (fully automatic page segmentation, no OSD) — captures bold
# centred amounts that PSM 6 misses on the tested receipt templates.
_DEFAULT_CONFIG = "--oem 3 --psm 3"


def _mean_confidence(tsv: dict) -> float:
    confs = [c for c in tsv.get("conf", []) if isinstance(c, (int, float)) and int(c) > -1]
    return round(sum(confs) / len(confs), 2) if confs else 0.0


def extract_transaction_fields(
    image_input: Union[str, Path, "Image.Image"],
    preprocess_mode: str = "contrast",
    tesseract_config: str = _DEFAULT_CONFIG,
) -> Dict[str, Any]:
    """
    Full pipeline: load → preprocess → OCR → parse fields.

    Args:
        image_input     : Path to receipt image or PIL Image object.
        preprocess_mode : 'raw' | 'grayscale' | 'contrast' (default) |
                          'otsu' | 'threshold' | 'denoise'
        tesseract_config: Tesseract CLI config string.

    Returns dict with:
        'fields'          — amount, amount_value, date, date_iso, time,
                            transaction_id, template_type, recipient, status
        'raw_text'        — full Tesseract output string
        'mean_confidence' — float 0–100
        'preprocess_mode' — str
        'image_path'      — str
        'success'         — bool (True if amount OR date was extracted)
        'error'           — str | None
    """
    path_str = str(image_input) if not isinstance(image_input, Image.Image) else "PIL Image"

    try:
        # Prefer raw mode first to avoid contrast-induced symbol distortion
        # (e.g. 2x contrast merging circular icons next to digits, turning ₹100 into 1000)
        if preprocess_mode == "contrast":
            raw_img = preprocess_image(image_input, method="raw")
            raw_text_try = pytesseract.image_to_string(raw_img, config=tesseract_config)
            raw_fields = parse_all_fields(raw_text_try)
            if raw_fields.get("amount") and raw_fields.get("date"):
                preprocessed = raw_img
                raw_text = raw_text_try
                fields = raw_fields
                preprocess_mode_used = "raw"
            else:
                preprocessed = preprocess_image(image_input, method="contrast")
                raw_text = pytesseract.image_to_string(preprocessed, config=tesseract_config)
                fields = parse_all_fields(raw_text)
                preprocess_mode_used = "contrast"
        else:
            preprocessed = preprocess_image(image_input, method=preprocess_mode)
            raw_text = pytesseract.image_to_string(preprocessed, config=tesseract_config)
            fields = parse_all_fields(raw_text)
            preprocess_mode_used = preprocess_mode

        tsv = pytesseract.image_to_data(
            preprocessed, config=tesseract_config,
            output_type=pytesseract.Output.DICT,
        )
        confidence = _mean_confidence(tsv)

        raw_text_out = fields.pop("raw_text", raw_text)

        return {
            "fields": fields,
            "raw_text": raw_text_out,
            "mean_confidence": confidence,
            "preprocess_mode": preprocess_mode_used,
            "image_path": path_str,
            "success": bool(fields.get("amount") or fields.get("date")),
            "error": None,
        }

    except (FileNotFoundError, ValueError) as exc:
        return {"fields": {}, "raw_text": "", "mean_confidence": 0.0,
                "preprocess_mode": preprocess_mode, "image_path": path_str,
                "success": False, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"fields": {}, "raw_text": "", "mean_confidence": 0.0,
                "preprocess_mode": preprocess_mode, "image_path": path_str,
                "success": False, "error": f"Unexpected error: {exc}"}
