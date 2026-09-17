"""
Central Dataset Configuration — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Defines all constants, dimensions, template specifications, label schemes,
and manipulation types. No downstream module may hard-code these parameters.
"""

from typing import Tuple, List, Dict, Any

# Reproducibility Seed
RANDOM_SEED: int = 42

# Canvas Dimensions (width, height) - Standard mobile screenshot aspect ratio (9:18 / 9:16)
IMAGE_SIZE: Tuple[int, int] = (400, 800)

# Fictional & Non-branded Template Names (Stand-ins for the 3 distinct layout families)
TEMPLATE_NAMES: List[str] = ["PayLite", "QuickPe", "UniPay"]

# Binary Classification Labels
LABELS: List[str] = ["original", "synthetic_fake"]

# Planned Manipulation Categories
EDIT_TYPES: List[str] = [
    "none",
    "amount_change",
    "date_change",
    "transaction_id_change",
    "text_insert",
    "text_remove",
    "font_alter",
    "crop",
    "resize",
    "recompress",
]

# Generation Bounds for Fictional Transaction Fields
AMOUNT_RANGE: Tuple[float, float] = (10.0, 50000.0)
DATE_RANGE: Tuple[str, str] = ("2025-01-01", "2026-03-31")

# Standard 12-Digit Numeric UPI Reference / Transaction ID Format
TXN_ID_FORMAT: str = r"^\d{12}$"
TXN_ID_LENGTH: int = 12

# Original Image Encoding Quality (High baseline to measure JPEG recompression delta)
JPEG_QUALITY_ORIGINAL: int = 95

# Mandatory Academic Safety Watermark
DEMO_WATERMARK_TEXT: str = "DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY"

# Target Split Proportions for Train / Validation / Test
SPLIT_RATIOS: Dict[str, float] = {
    "train": 0.60,
    "val": 0.20,
    "test": 0.20,
}

# Image ID Naming Convention Pattern: tpl{Family}_src{ID}_{EditType}_{Variant}
ID_PATTERN: str = "tpl{tpl_id}_src{src_id:03d}_{edit_type}_{var_id:02d}"
