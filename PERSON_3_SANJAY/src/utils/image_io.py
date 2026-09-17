"""Image loading and normalization utilities."""

import io
from pathlib import Path
from typing import Union
import numpy as np
from PIL import Image

def load_image(image_input: Union[str, Path, bytes, Image.Image, np.ndarray]) -> Image.Image:
    """Safely convert various input types into a PIL RGB Image.
    
    Supports:
    - File path (str or Path)
    - Raw bytes or BytesIO
    - Existing PIL Image
    - NumPy array (HWC or HW)
    
    Returns:
        PIL.Image.Image in RGB mode.
    """
    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    
    if isinstance(image_input, (str, Path)):
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found at: {path}")
        img = Image.open(path)
        return img.convert("RGB")
    
    if isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
        return img.convert("RGB")
    
    if isinstance(image_input, io.BytesIO):
        img = Image.open(image_input)
        return img.convert("RGB")
        
    if isinstance(image_input, np.ndarray):
        # Check if BGR (OpenCV format) or RGB
        if image_input.ndim == 2:
            return Image.fromarray(image_input).convert("RGB")
        elif image_input.ndim == 3:
            return Image.fromarray(image_input).convert("RGB")
            
    raise TypeError(f"Unsupported image input type: {type(image_input)}")


def pil_to_numpy(image: Image.Image) -> np.ndarray:
    """Convert PIL RGB image to numpy uint8 array."""
    return np.array(image.convert("RGB"))
