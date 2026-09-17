"""Training and validation engine for the ResNet18 transfer learning baseline."""

import random
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional, Union
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .model import create_resnet18_model, save_model_checkpoint
from .dataset import create_group_aware_datasets, UPIScreenshotDataset
from .evaluate import compute_classification_metrics
from ..utils.device import get_device


def set_seed(seed: int = 42) -> None:
    """Set random seeds for reproducibility across random, numpy, and torch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device
) -> Tuple[float, float]:
    """Train model for a single epoch.

    Returns:
        Tuple of (average_loss, accuracy)
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total_samples = 0

    for batch in dataloader:
        images = batch["image"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1)
        correct += (preds == labels).sum().item()
        total_samples += images.size(0)

    avg_loss = total_loss / max(total_samples, 1)
    accuracy = correct / max(total_samples, 1)
    return avg_loss, accuracy


def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, Dict[str, Any]]:
    """Evaluate model on a validation dataset.

    Returns:
        Tuple of (average_loss, metrics_dict)
    """
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    all_probs = []
    total_samples = 0

    with torch.no_grad():
        for batch in dataloader:
            images = batch["image"].to(device)
            labels = batch["label"].to(device)

            logits = model(images)
            loss = criterion(logits, labels)

            total_loss += loss.item() * images.size(0)
            probs = torch.softmax(logits, dim=1)[:, 1]
            preds = torch.argmax(logits, dim=1)

            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(labels.cpu().tolist())
            all_probs.extend(probs.cpu().tolist())
            total_samples += images.size(0)

    avg_loss = total_loss / max(total_samples, 1)
    metrics = compute_classification_metrics(all_targets, all_preds, all_probs)
    return avg_loss, metrics


def train_baseline_pipeline(
    metadata_csv: Union[str, Path],
    images_dir: Union[str, Path],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    smoke_test: bool = False
) -> Dict[str, Any]:
    """Execute complete reproducible baseline training and validation pipeline.

    Args:
        metadata_csv: Path to metadata.csv.
        images_dir: Path to raw screenshot directory.
        output_dir: Path to save checkpoints and result logs.
        config: Training configuration overrides.
        smoke_test: If True, executes 1 quick epoch to verify end-to-end pipeline sanity.

    Returns:
        Dictionary containing training history, best validation metrics, and checkpoint paths.
    """
    # Default baseline configuration
    default_config = {
        "seed": 42,
        "image_size": 224,
        "batch_size": 8,
        "learning_rate": 1e-4,
        "weight_decay": 1e-4,
        "epochs": 1 if smoke_test else 10,
        "dropout_rate": 0.3,
        "pretrained": True,
        "freeze_backbone": False,
        "model_name": "resnet18_baseline"
    }
    if config:
        default_config.update(config)
    cfg = default_config

    set_seed(cfg["seed"])
    device = get_device()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Prepare Datasets (Train and Val only; test set remains untouched!)
    train_ds, val_ds, _ = create_group_aware_datasets(
        metadata_csv=metadata_csv,
        images_dir=images_dir,
        img_size=cfg["image_size"]
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg["batch_size"],
        shuffle=True,
        drop_last=False
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg["batch_size"],
        shuffle=False
    )

    # 2. Instantiate Model
    model = create_resnet18_model(
        pretrained=cfg["pretrained"],
        num_classes=2,
        dropout_rate=cfg["dropout_rate"],
        freeze_backbone=cfg["freeze_backbone"]
    )
    model.to(device)

    # 3. Loss & Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg["learning_rate"],
        weight_decay=cfg["weight_decay"]
    )

    # 4. Training Loop
    history: Dict[str, List[float]] = {
        "epoch": [],
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_precision": [],
        "val_recall": [],
        "val_f1": []
    }

    best_val_loss = float("inf")
    best_checkpoint_path = output_path / f"{cfg['model_name']}_best.pt"
    best_metrics = {}

    start_time = time.time()

    for epoch in range(1, cfg["epochs"] + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_metrics = evaluate_model(model, val_loader, criterion, device)

        history["epoch"].append(epoch)
        history["train_loss"].append(round(tr_loss, 4))
        history["train_acc"].append(round(tr_acc, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(val_metrics["accuracy"])
        history["val_precision"].append(val_metrics["precision"])
        history["val_recall"].append(val_metrics["recall"])
        history["val_f1"].append(val_metrics["f1_score"])

        # Checkpoint selection based on lowest validation loss
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_metrics = val_metrics
            save_model_checkpoint(
                model=model,
                checkpoint_path=best_checkpoint_path,
                config=cfg,
                metrics=val_metrics
            )

    elapsed = time.time() - start_time

    # Save final epoch checkpoint
    final_checkpoint_path = output_path / f"{cfg['model_name']}_final.pt"
    save_model_checkpoint(
        model=model,
        checkpoint_path=final_checkpoint_path,
        config=cfg,
        metrics=val_metrics
    )

    return {
        "config": cfg,
        "history": history,
        "best_val_loss": round(best_val_loss, 4),
        "best_val_metrics": best_metrics,
        "best_checkpoint_path": str(best_checkpoint_path),
        "final_checkpoint_path": str(final_checkpoint_path),
        "elapsed_seconds": round(elapsed, 2),
        "device_used": str(device)
    }
