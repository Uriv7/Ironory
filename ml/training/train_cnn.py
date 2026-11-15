"""Training script for Baseline CNN on NEU Surface Defect Database.

Runs complete model training lifecycle:
- Dataset generation / loading (70% train, 15% val, 15% test).
- Data augmentation.
- Callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard.
- Test evaluation and confusion matrix generation.
- Model serialization to .keras format.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ironory.ml.training.cnn")


def train_baseline_cnn(
    epochs: int = 15,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    output_dir: Path = Path("ml/artifacts"),
):
    import tensorflow as tf
    import matplotlib.pyplot as plt
    from ml.datasets.neu_loader import load_neu_dataset, DEFECT_CLASSES
    from ml.models.cnn.baseline_cnn import build_baseline_cnn
    from ml.evaluation.metrics import evaluate_classifier

    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = output_dir / "logs" / "baseline_cnn"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading NEU-DET surface defect dataset...")
    train_ds, val_ds, test_ds, splits = load_neu_dataset(batch_size=batch_size)
    logger.info(f"Dataset split sizes: Train={len(splits['train'])}, Val={len(splits['val'])}, Test={len(splits['test'])}")

    logger.info("Constructing Baseline CNN...")
    model = build_baseline_cnn(
        input_shape=(224, 224, 3),
        num_classes=len(DEFECT_CLASSES),
        learning_rate=learning_rate,
    )
    model.summary(print_fn=logger.info)

    checkpoint_path = output_dir / "baseline_cnn.keras"

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir=str(log_dir),
            histogram_freq=1,
        ),
    ]

    logger.info(f"Starting training for {epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
    )

    # Plot training curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.plot(history.history["accuracy"], label="Train Accuracy", lw=2)
    ax1.plot(history.history["val_accuracy"], label="Val Accuracy", lw=2)
    ax1.set_title("Baseline CNN — Accuracy Curve")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(history.history["loss"], label="Train Loss", lw=2)
    ax2.plot(history.history["val_loss"], label="Val Loss", lw=2)
    ax2.set_title("Baseline CNN — Loss Curve")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Cross-Entropy Loss")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    history_plot = output_dir / "baseline_cnn_training_curves.png"
    fig.savefig(history_plot, dpi=180)
    plt.close(fig)
    logger.info(f"Saved training history curves to: {history_plot}")

    # Evaluate on held-out test split
    logger.info("Evaluating Baseline CNN on held-out test set...")
    best_model = tf.keras.models.load_model(str(checkpoint_path))
    eval_dir = output_dir / "evaluation" / "baseline_cnn"
    eval_metrics = evaluate_classifier(best_model, test_ds, DEFECT_CLASSES, output_dir=eval_dir)

    logger.info(f"Test Accuracy: {eval_metrics['accuracy']:.4f}")
    return best_model, eval_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Baseline CNN for Ironory")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train_baseline_cnn(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr)
