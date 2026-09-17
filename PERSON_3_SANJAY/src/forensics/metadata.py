"""Metadata and EXIF inspection for digital payment screenshot forensics.

Inspects available image headers for:
- Known editing software signatures (Photoshop, Canva, PicsArt, GIMP, Pixelcut, etc.)
- Metadata presence / stripping characteristics
- Camera vs. screenshot header markers
- Timestamp metadata discrepancies

Note on Limitations:
Modern screenshots shared over messaging platforms (WhatsApp, Telegram) frequently
have EXIF metadata completely stripped by compression algorithms.
The absence of metadata is not proof of fraud, but an inconclusive state.
"""

from typing import Dict, Any, List
from PIL import Image, ExifTags
from pathlib import Path

from ..utils.image_io import load_image

# Known image editing / manipulation software keywords
SUSPICIOUS_SOFTWARE_KEYWORDS = [
    "photoshop", "adobe", "canva", "picsart", "gimp", "pixelcut", "lightroom",
    "snapseed", "affinity", "coreldraw", "photopea", "sketch", "figma", "paint.net"
]


def inspect_metadata(image_input) -> Dict[str, Any]:
    """Inspect image metadata, EXIF tags, and software markers.

    Args:
        image_input: Path, bytes, PIL Image, or numpy array.

    Returns:
        Dict with extracted metadata, suspicious signatures, and cautious diagnostic notes.
    """
    raw_img = load_image(image_input)
    
    metadata_info = {
        "has_exif": False,
        "format": raw_img.format if hasattr(raw_img, "format") and raw_img.format else "Unknown",
        "software": None,
        "make": None,
        "model": None,
        "datetime": None,
        "editing_software_detected": False,
        "detected_software_tags": [],
        "exif_tags": {},
        "indicators": [],
        "limitations": []
    }
    
    # Extract EXIF if available
    try:
        exif_data = raw_img.getexif()
        if exif_data and len(exif_data) > 0:
            metadata_info["has_exif"] = True
            
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_str = str(value)
                metadata_info["exif_tags"][tag_name] = val_str
                
                # Check Software tag
                if tag_name.lower() in ("software", "processingsoftware"):
                    metadata_info["software"] = val_str
                    for keyword in SUSPICIOUS_SOFTWARE_KEYWORDS:
                        if keyword in val_str.lower():
                            metadata_info["editing_software_detected"] = True
                            metadata_info["detected_software_tags"].append(val_str)
                            
                # Check Device / Make / Model
                if tag_name.lower() == "make":
                    metadata_info["make"] = val_str
                elif tag_name.lower() == "model":
                    metadata_info["model"] = val_str
                elif tag_name.lower() in ("datetime", "datetimeoriginal", "datetimedigitized"):
                    metadata_info["datetime"] = val_str
    except Exception as err:
        metadata_info["limitations"].append(f"EXIF parsing encountered: {str(err)}")
        
    # Check PIL Image info dictionary (e.g. PNG text chunks)
    if hasattr(raw_img, "info") and isinstance(raw_img.info, dict):
        for key, val in raw_img.info.items():
            val_str = str(val)
            for keyword in SUSPICIOUS_SOFTWARE_KEYWORDS:
                if keyword in val_str.lower():
                    metadata_info["editing_software_detected"] = True
                    if val_str not in metadata_info["detected_software_tags"]:
                        metadata_info["detected_software_tags"].append(f"{key}: {val_str}")

    # Generate cautious indicator statements
    if metadata_info["editing_software_detected"]:
        metadata_info["indicators"].append(
            f"Image header contains software signature associated with editing tools: {metadata_info['detected_software_tags']}."
        )
    elif metadata_info["has_exif"]:
        metadata_info["indicators"].append(
            "EXIF metadata structure present without obvious desktop editing signatures."
        )
    else:
        metadata_info["indicators"].append(
            "No EXIF metadata found (typical for standard mobile screenshots and messaging app re-compression)."
        )
        metadata_info["limitations"].append(
            "Metadata is absent or stripped; forensic judgment must rely on visual and structural analysis."
        )
        
    return metadata_info
