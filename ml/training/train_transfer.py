"""Training script for Transfer Learning models (MobileNetV2 and EfficientNetB0) on NEU dataset.

Demonstrates fine-tuning pre-trained ImageNet backbones for steel defect classification,
comparing convergence speeds, parameter efficiency, and accuracy against Baseline CNN.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ironory.ml.training.transfer")


def train_mobilenet(
    epochs_frozen: int = 8,
    epochs_finetune: int = 6,
    batch_size: int = 32,
    output_dir: Path = Path("ml/artifacts"),
):
    import tensorflow as tf
    from ml.datasets.neu_loader import load_neu_dataset, DEFECT_CLASSES
    from ml.models.transfer_learning.mobilenet import build_mobilenet_v2, fine_tune_mobilenet
    from ml.evaluation.metrics import evaluate_classifier

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "mobilenet_v2.keras"

    logger.info("Loading NEU dataset for MobileNetV2...")
    train_ds, val_ds, test_ds, _ = load_neu_dataset(batch_size=batch_size)

    logger.info("Constructing MobileNetV2 transfer model (frozen base)...")
    model, base_model = build_mobilenet_v2(
        input_shape=(224, 224, 3),
        num_classes=len(DEFECT_CLASSES),
        freeze_base=True,
        learning_rate=1e-4,
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(str(checkpoint_path), monitor="val_accuracy", save_best_only=True),
    ]

    logger.info(f"Phase 1: Training classification head for {epochs_frozen} epochs...")
    model.fit(train_ds, validation_data=val_ds, epochs=epochs_frozen, callbacks=callbacks)

    if epochs_finetune > 0:
        logger.info(f"Phase 2: Fine-tuning top layers of MobileNetV2 for {epochs_finetune} epochs...")
        model = fine_tune_mobilenet(model, base_model, fine_tune_at=100, fine_tune_lr=1e-5)
        model.fit(train_ds, validation_data=val_ds, epochs=epochs_finetune, callbacks=callbacks)

    logger.info("Evaluating MobileNetV2 on test split...")
    best_model = tf.keras.models.load_model(str(checkpoint_path))
    eval_dir = output_dir / "evaluation" / "mobilenet_v2"
    metrics = evaluate_classifier(best_model, test_ds, DEFECT_CLASSES, output_dir=eval_dir)
    logger.info(f"MobileNetV2 Test Accuracy: {metrics['accuracy']:.4f}")
    return best_model, metrics


def train_efficientnet(
    epochs: int = 10,
    batch_size: int = 32,
    output_dir: Path = Path("ml/artifacts"),
):
    import tensorflow as tf
    from ml.datasets.neu_loader import load_neu_dataset, DEFECT_CLASSES
    from ml.models.transfer_learning.efficientnet import build_efficientnet_b0
    from ml.evaluation.metrics import evaluate_classifier

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "efficientnet_b0.keras"

    logger.info("Loading NEU dataset for EfficientNetB0...")
    train_ds, val_ds, test_ds, _ = load_neu_dataset(batch_size=batch_size)

    logger.info("Constructing EfficientNetB0 transfer model...")
    model, _ = build_efficientnet_b0(
        input_shape=(224, 224, 3),
        num_classes=len(DEFECT_CLASSES),
        freeze_base=True,
        learning_rate=1e-4,
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(str(checkpoint_path), monitor="val_accuracy", save_best_only=True),
    ]

    logger.info(f"Training EfficientNetB0 for {epochs} epochs...")
    model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks)

    logger.info("Evaluating EfficientNetB0 on test split...")
    best_model = tf.keras.models.load_model(str(checkpoint_path))
    eval_dir = output_dir / "evaluation" / "efficientnet_b0"
    metrics = evaluate_classifier(best_model, test_ds, DEFECT_CLASSES, output_dir=eval_dir)
    logger.info(f"EfficientNetB0 Test Accuracy: {metrics['accuracy']:.4f}")
    return best_model, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Transfer Learning Models for Ironory")
    parser.add_argument("--model", choices=["mobilenet", "efficientnet", "all"], default="mobilenet")
    parser.add_argument("--epochs", type=int, default=8)
    args = parser.parse_args()

    if args.model in ("mobilenet", "all"):
        train_mobilenet(epochs_frozen=args.epochs, epochs_finetune=4)
    if args.model in ("efficientnet", "all"):
        train_efficientnet(epochs=args.epochs)
