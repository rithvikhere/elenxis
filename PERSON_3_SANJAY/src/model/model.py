"""ResNet18 Transfer Learning Model for UPI Screenshot Authenticity Classification.

Academic & Architectural Rationale:
-----------------------------------
1. Why ResNet18?
   - ResNet18 is a robust, well-studied residual network architecture with ~11.2 million
     parameters. Its residual skip connections mitigate vanishing gradients and provide
     hierarchical low-, mid-, and high-level edge and texture representations.
   - For our 30% baseline with 60 labeled screenshots, ResNet18 is sufficiently expressive
     to capture layout structures without the severe overfitting risk and computational
     overhead of heavier architectures (such as ResNet-50 or ViT).

2. Pretrained ImageNet Weights:
   - Utilizes `torchvision.models.ResNet18_Weights.DEFAULT` (IMAGENET1K_V1) for transfer
     learning, leveraging rich edge and spatial filter primitives learned from 1.2M natural images.

3. Final Classification Layer:
   - The original 1000-class fully connected layer (`model.fc`) is replaced with a 2-class
     classification head (`0: original`, `1: modified`) regularized with Dropout (p=0.3).
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import torch
import torch.nn as nn
import torchvision.models as models

# Canonical class index to name mapping
CLASS_MAP = {
    0: "original",
    1: "modified"
}


class ResNet18ForensicsClassifier(nn.Module):
    """ResNet-18 Transfer Learning Classifier for UPI screenshot forensics."""

    def __init__(
        self,
        num_classes: int = 2,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        freeze_backbone: bool = False
    ):
        """Initialize the ResNet-18 model.

        Args:
            num_classes: Output class count (default: 2 -> [original, modified]).
            pretrained: Whether to load ImageNet pre-trained weights.
            dropout_rate: Dropout regularization rate before classification head.
            freeze_backbone: If True, freezes backbone convolutional layers during training.
        """
        super().__init__()
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.architecture_name = "resnet18_transfer_learning"

        # Load backbone
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        self.resnet = models.resnet18(weights=weights)

        # Optional backbone parameter freezing
        if freeze_backbone:
            for param in self.resnet.parameters():
                param.requires_grad = False

        # Replace classification head (in_features = 512 for ResNet18)
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Execute forward pass returning unnormalized class logits [batch_size, num_classes]."""
        return self.resnet(x)

    def get_trainable_param_counts(self) -> Dict[str, int]:
        """Return total and trainable parameter counts."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "frozen_parameters": total_params - trainable_params
        }


def create_resnet18_model(
    pretrained: bool = True,
    num_classes: int = 2,
    dropout_rate: float = 0.3,
    freeze_backbone: bool = False
) -> ResNet18ForensicsClassifier:
    """Factory function to instantiate ResNet18ForensicsClassifier."""
    return ResNet18ForensicsClassifier(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
        freeze_backbone=freeze_backbone
    )


def save_model_checkpoint(
    model: nn.Module,
    checkpoint_path: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None
) -> Path:
    """Save model checkpoint with full reproducibility metadata.

    Args:
        model: PyTorch model instance.
        checkpoint_path: Destination path for .pt file.
        config: Training configuration dictionary.
        metrics: Final validation metrics dictionary.

    Returns:
        Resolved Path to saved checkpoint.
    """
    path = Path(checkpoint_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "architecture": "resnet18_transfer_learning",
        "state_dict": model.state_dict(),
        "num_classes": 2,
        "class_map": CLASS_MAP,
        "image_size": 224,
        "config": config or {},
        "metrics": metrics or {}
    }

    torch.save(checkpoint, path)
    return path


def load_model_checkpoint(
    checkpoint_path: Union[str, Path],
    device: Optional[torch.device] = None
) -> Tuple[ResNet18ForensicsClassifier, Dict[str, Any]]:
    """Load model checkpoint and restore architecture state.

    Args:
        checkpoint_path: Path to .pt checkpoint.
        device: Device to map tensors onto.

    Returns:
        Tuple of (model, checkpoint_dict)
    """
    path = Path(checkpoint_path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {path}")

    device = device or torch.device("cpu")
    checkpoint = torch.load(path, map_location=device)

    model = create_resnet18_model(
        pretrained=False,
        num_classes=checkpoint.get("num_classes", 2)
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()

    return model, checkpoint
