"""Grad-CAM for the trained ResNet-18 screenshot classifier.

The heatmap highlights regions contributing to a selected model class. It is an
explanation of this model output, not localisation proof of image manipulation.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from matplotlib import colormaps
import numpy as np
import torch
import torch.nn.functional as functional
from PIL import Image

from ..model.model import CLASS_MAP, load_model_checkpoint
from ..model.preprocessing import preprocess_image_tensor
from ..utils.image_io import load_image

TARGET_LAYER = "resnet.layer4[-1].conv2"


def _target_layer(model: torch.nn.Module) -> torch.nn.Module:
    """Return ResNet-18's final convolutional layer, before global pooling."""
    try:
        return model.resnet.layer4[-1].conv2
    except (AttributeError, IndexError) as error:
        raise ValueError("Grad-CAM currently supports the ResNet18ForensicsClassifier architecture only.") from error


def generate_gradcam(
    image_input: Any,
    model_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    target_class: Optional[int] = None,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """Generate a Grad-CAM heatmap and overlay for a loaded ResNet-18 checkpoint.

    By default, explains the predicted class. When ``output_dir`` is supplied,
    original, heatmap, and overlay PNGs are persisted there.
    """
    input_path = str(image_input) if isinstance(image_input, (str, Path)) else None
    try:
        device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, checkpoint = load_model_checkpoint(model_path, device=device)
        layer = _target_layer(model)
        activations, gradients = [], []
        forward_hook = layer.register_forward_hook(lambda _, __, output: activations.append(output.detach()))
        backward_hook = layer.register_full_backward_hook(lambda _, __, output: gradients.append(output[0].detach()))
        try:
            original = load_image(image_input)
            tensor = preprocess_image_tensor(original, is_training=False, img_size=checkpoint.get("image_size", 224)).to(device)
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]
            prediction_index = int(torch.argmax(probabilities).item())
            class_index = prediction_index if target_class is None else int(target_class)
            if class_index not in (0, 1):
                raise ValueError("target_class must be 0 (original) or 1 (modified).")
            model.zero_grad(set_to_none=True)
            logits[0, class_index].backward()
            if not activations or not gradients:
                raise RuntimeError("Grad-CAM hooks did not capture the target layer output and gradients.")
            weights = gradients[0].mean(dim=(2, 3), keepdim=True)
            cam = torch.relu((weights * activations[0]).sum(dim=1, keepdim=True))
            cam = functional.interpolate(cam, size=original.size[::-1], mode="bilinear", align_corners=False)[0, 0]
            cam = cam.detach().cpu().numpy()
            maximum = float(cam.max())
            if maximum <= 0:
                raise RuntimeError("Grad-CAM produced an all-zero heatmap for this target class.")
            heatmap = cam / maximum
        finally:
            forward_hook.remove()
            backward_hook.remove()

        base = np.asarray(original.convert("RGB"), dtype=np.float32) / 255.0
        heatmap_rgb = colormaps["jet"](heatmap)[..., :3]
        overlay = np.clip(0.55 * base + 0.45 * heatmap_rgb, 0, 1)
        heatmap_image = Image.fromarray((heatmap_rgb * 255).astype(np.uint8), "RGB")
        overlay_image = Image.fromarray((overlay * 255).astype(np.uint8), "RGB")
        paths = {"original": None, "heatmap": None, "overlay": None}
        if output_dir is not None:
            destination = Path(output_dir)
            destination.mkdir(parents=True, exist_ok=True)
            stem = Path(input_path).stem if input_path else "in_memory_image"
            original_path, heatmap_path, overlay_path = (destination / f"{stem}_{suffix}.png" for suffix in ("original", "gradcam_heatmap", "gradcam_overlay"))
            original.save(original_path)
            heatmap_image.save(heatmap_path)
            overlay_image.save(overlay_path)
            paths = {"original": str(original_path), "heatmap": str(heatmap_path), "overlay": str(overlay_path)}
        class_map = checkpoint.get("class_map", CLASS_MAP)
        label = class_map.get(prediction_index, class_map.get(str(prediction_index), str(prediction_index)))
        explained_label = class_map.get(class_index, class_map.get(str(class_index), str(class_index)))
        return {
            "status": "available", "input_path": input_path, "architecture": checkpoint.get("architecture"),
            "target_layer": TARGET_LAYER, "prediction": {"class_index": prediction_index, "label": label,
            "probability": round(float(probabilities[prediction_index].item()), 6)},
            "explained_class": {"class_index": class_index, "label": explained_label},
            "output_paths": paths,
            "warnings": ["Grad-CAM highlights regions contributing to this model output; it does not prove a region was manipulated or that fraud occurred."],
        }
    except Exception as error:
        return {"status": "error", "input_path": input_path, "target_layer": TARGET_LAYER,
                "output_paths": {"original": None, "heatmap": None, "overlay": None},
                "error": str(error), "warnings": ["No Grad-CAM visualisation was produced for this input."]}


generate_gradcam_heatmap = generate_gradcam
