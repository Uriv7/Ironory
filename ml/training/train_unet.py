"""Training script for U-Net Defect Segmentation on industrial surfaces.

Generates paired surface images and defect ground-truth masks, trains the contracting-expanding
U-Net network with skip connections, and saves to ml/artifacts/unet.keras.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ironory.ml.training.unet")


def train_unet(
    epochs: int = 6,
    batch_size: int = 16,
    output_dir: Path = Path("ml/artifacts"),
):
    import numpy as np
    import tensorflow as tf
    from ml.datasets.neu_loader import ensure_dataset
    from ml.models.segmentation.unet import build_unet

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "unet.keras"

    data_dir = ensure_dataset()

    # Create synthetic defect segmentation pairs (image, binary_mask)
    logger.info("Preparing defect segmentation datasets...")
    def _create_dataset():
        images = []
        masks = []
        rng = np.random.RandomState(42)

        for img_path in sorted(list(data_dir.glob("*/*.jpg")))[:300]:
            img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
            arr = np.array(img, dtype=np.float32) / 255.0
            images.append(arr)

            # Synthesize realistic ground truth mask based on low-luminance defect pixels
            gray = np.mean(arr, axis=-1)
            thresh = np.percentile(gray, 18)  # Bottom 18% darkest defect pixels
            mask = (gray < thresh).astype(np.float32)
            masks.append(np.expand_dims(mask, axis=-1))

        x = np.array(images, dtype=np.float32)
        y = np.array(masks, dtype=np.float32)

        # 80/20 train/val
        n_train = int(len(x) * 0.8)
        return (x[:n_train], y[:n_train]), (x[n_train:], y[n_train:])

    (x_train, y_train), (x_val, y_val) = _create_dataset()

    logger.info(f"Training U-Net on {len(x_train)} samples, validating on {len(x_val)} samples...")
    model = build_unet(input_shape=(224, 224, 3), num_classes=1, learning_rate=1e-4)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(str(checkpoint_path), monitor="val_dice_coefficient", mode="max", save_best_only=True),
    ]

    model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        batch_size=batch_size,
        epochs=epochs,
        callbacks=callbacks,
    )

    logger.info(f"U-Net training finished. Model saved to: {checkpoint_path}")
    return model


if __name__ == "__main__":
    train_unet()
