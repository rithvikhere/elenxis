"""CNN Model Architecture and Inference Contract for UPI Screenshot Authenticity Analysis.

Defines:
- UPIForensicsCNN: PyTorch neural network module supporting custom baseline or transfer learning backbones (ResNet18 / ResNet50 / EfficientNet).
- predict(image): Standardized integration contract returning prediction information.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

from ..utils.device import get_device
from ..utils.image_io import load_image


class UPIForensicsCNN(nn.Module):
    """Convolutional Neural Network for UPI screenshot forgery detection."""

    def __init__(
        self,
        backbone: str = "custom_baseline",
        num_classes: int = 2,
        pretrained: bool = False,
        dropout_rate: float = 0.3
    ):
        """Initialize the CNN model.

        Args:
            backbone: 'custom_baseline', 'resnet18', 'resnet50', or 'efficientnet_b0'.
            num_classes: Number of output classes (default 2: [0=original, 1=modified]).
            pretrained: Whether to load ImageNet pre-trained weights for transfer learning.
            dropout_rate: Dropout probability before the classification head.
        """
        super().__init__()
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        if backbone == "resnet18":
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            base = models.resnet18(weights=weights)
            in_features = base.fc.in_features
            base.fc = nn.Identity()
            self.feature_extractor = base
            self.classifier = nn.Sequential(
                nn.Dropout(dropout_rate),
                nn.Linear(in_features, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(128, num_classes)
            )
        elif backbone == "resnet50":
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            base = models.resnet50(weights=weights)
            in_features = base.fc.in_features
            base.fc = nn.Identity()
            self.feature_extractor = base
            self.classifier = nn.Sequential(
                nn.Dropout(dropout_rate),
                nn.Linear(in_features, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(256, num_classes)
            )
        else:
            # Lightweight custom convolutional baseline
            self.feature_extractor = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),  # 112x112
                
                nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),  # 56x56
                
                nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((4, 4))            # 128 x 4 x 4
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Dropout(dropout_rate),
                nn.Linear(128 * 4 * 4, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(128, num_classes)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning unnormalized class logits."""
        features = self.feature_extractor(x)
        logits = self.classifier(features)
        return logits


def get_default_transform(img_size: int = 224) -> transforms.Compose:
    """Standard image evaluation transform."""
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def predict(
    image_input,
    model: Optional[UPIForensicsCNN] = None,
    weights_path: Optional[Union[str, Path]] = None,
    device: Optional[torch.device] = None
) -> Dict[str, Any]:
    """Execute model prediction on input image.

    Conforms to the team contract:
    {
        "label": None | "original" | "modified",
        "probability": None | float,
        "model_version": str,
        "available": bool,
        "reasons": list[str]
    }

    Args:
        image_input: Path, bytes, PIL Image, or numpy array.
        model: Pre-instantiated UPIForensicsCNN model (optional).
        weights_path: Path to .pt / .pth checkpoint weights (optional).
        device: Torch device (optional, defaults to detected hardware).

    Returns:
        Dict conforming to team contract.
    """
    # 30% Review Safeguard: If no trained model weights exist, return safe uninitialized contract
    if model is None and (weights_path is None or not Path(weights_path).exists()):
        return {
            "label": None,
            "probability": None,
            "model_version": "v1.0.0-uninitialized",
            "available": False,
            "reasons": [
                "Trained CNN weights are not loaded yet (Phase 1 foundational milestone).",
                "Model architecture is initialized and ready for training once dataset splits are finalized."
            ]
        }

    try:
        if device is None:
            device = get_device()

        if model is None:
            model = UPIForensicsCNN(backbone="resnet18", num_classes=2, pretrained=False)
            checkpoint = torch.load(weights_path, map_location=device)
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                model.load_state_dict(checkpoint["state_dict"])
            else:
                model.load_state_dict(checkpoint)
        
        model.to(device)
        model.eval()

        pil_img = load_image(image_input)
        transform = get_default_transform(img_size=224)
        input_tensor = transform(pil_img).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = model(input_tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

        # Class indices: 0 = Original, 1 = Modified
        orig_prob = float(probs[0])
        mod_prob = float(probs[1])

        if mod_prob >= 0.50:
            predicted_label = "modified"
            confidence = mod_prob
            reason = f"Model visual features indicate characteristics associated with learned modified patterns (p={confidence:.2f})."
        else:
            predicted_label = "original"
            confidence = orig_prob
            reason = f"Model visual features align with authentic reference patterns (p={confidence:.2f})."

        return {
            "label": predicted_label,
            "probability": round(confidence, 4),
            "probabilities": {
                "original": round(orig_prob, 4),
                "modified": round(mod_prob, 4)
            },
            "model_version": "v1.0.0-baseline",
            "available": True,
            "reasons": [reason]
        }
    except Exception as err:
        return {
            "label": None,
            "probability": None,
            "model_version": "v1.0.0-error",
            "available": False,
            "reasons": [f"Inference error encountered: {str(err)}"]
        }
