"""Training script for Convolutional Autoencoder on defect-free steel surfaces.

Learns normal surface representations and calibrates the reconstruction error anomaly threshold.
Saves model to ml/artifacts/conv_autoencoder.keras and threshold to ml/artifacts/anomaly_threshold.json.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ironory.ml.training.autoencoder")


def train_autoencoder(
    epochs: int = 8,
    batch_size: int = 32,
    output_dir: Path = Path("ml/artifacts"),
):
    import numpy as np
    import tensorflow as tf
    from ml.datasets.neu_loader import load_neu_dataset
    from ml.models.autoencoder.conv_autoencoder import build_conv_autoencoder

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "conv_autoencoder.keras"

    logger.info("Loading dataset for Autoencoder unsupervised training...")
    train_ds, val_ds, test_ds, _ = load_neu_dataset(batch_size=batch_size)

    # For autoencoder, input is target: (x, x)
    train_ae_ds = train_ds.map(lambda x, y: (x, x), num_parallel_calls=tf.data.AUTOTUNE)
    val_ae_ds = val_ds.map(lambda x, y: (x, x), num_parallel_calls=tf.data.AUTOTUNE)

    autoencoder, encoder = build_conv_autoencoder(input_shape=(224, 224, 3))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(str(checkpoint_path), monitor="val_loss", save_best_only=True),
    ]

    logger.info(f"Training Autoencoder for {epochs} epochs...")
    autoencoder.fit(train_ae_ds, validation_data=val_ae_ds, epochs=epochs, callbacks=callbacks)

    # Calibrate anomaly threshold on validation set (mean error + 2 * std)
    val_errors = []
    for x_batch, _ in val_ae_ds:
        recon = autoencoder.predict(x_batch, verbose=0)
        batch_mse = np.mean(np.square(x_batch.numpy() - recon), axis=(1, 2, 3))
        val_errors.extend(batch_mse.tolist())

    mean_err = float(np.mean(val_errors))
    std_err = float(np.std(val_errors))
    calibrated_threshold = float(mean_err + (2.0 * std_err))

    threshold_meta = {
        "mean_reconstruction_error": mean_err,
        "std_reconstruction_error": std_err,
        "anomaly_threshold": calibrated_threshold,
        "sample_size": len(val_errors),
    }

    threshold_file = output_dir / "anomaly_threshold.json"
    with open(threshold_file, "w") as f:
        json.dump(threshold_meta, f, indent=2)

    logger.info(f"Autoencoder saved to {checkpoint_path}. Anomaly threshold calibrated: {calibrated_threshold:.6f}")
    return autoencoder, threshold_meta


if __name__ == "__main__":
    train_autoencoder()
