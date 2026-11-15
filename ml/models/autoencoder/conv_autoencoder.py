"""Convolutional Autoencoder for Unsupervised Defect & Anomaly Detection.

Used when defect classes are novel or unlabelled. The autoencoder learns the manifold
of normal defect-free steel surfaces. Defective regions produce high reconstruction error (MSE).
"""

from __future__ import annotations

import logging
from typing import Tuple

import numpy as np

logger = logging.getLogger("ironory.ml.models.autoencoder")


def build_conv_autoencoder(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    latent_dim: int = 32,
    learning_rate: float = 1e-3,
):
    """Build and compile Convolutional Autoencoder."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    # Encoder
    inputs = layers.Input(shape=input_shape, name="surface_input")
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same", name="enc_conv1")(inputs)
    x = layers.MaxPooling2D((2, 2), padding="same", name="enc_pool1")(x)  # 112x112

    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same", name="enc_conv2")(x)
    x = layers.MaxPooling2D((2, 2), padding="same", name="enc_pool2")(x)  # 56x56

    x = layers.Conv2D(128, (3, 3), activation="relu", padding="same", name="enc_conv3")(x)
    x = layers.MaxPooling2D((2, 2), padding="same", name="enc_pool3")(x)  # 28x28

    encoded = layers.Conv2D(latent_dim, (3, 3), activation="relu", padding="same", name="latent_bottleneck")(x)

    # Decoder
    x = layers.Conv2DTranspose(128, (3, 3), strides=2, activation="relu", padding="same", name="dec_deconv1")(encoded)  # 56x56
    x = layers.Conv2DTranspose(64, (3, 3), strides=2, activation="relu", padding="same", name="dec_deconv2")(x)  # 112x112
    x = layers.Conv2DTranspose(32, (3, 3), strides=2, activation="relu", padding="same", name="dec_deconv3")(x)  # 224x224
    decoded = layers.Conv2D(input_shape[2], (3, 3), activation="sigmoid", padding="same", name="reconstructed_surface")(x)

    autoencoder = models.Model(inputs=inputs, outputs=decoded, name="Ironory_Autoencoder")
    encoder = models.Model(inputs=inputs, outputs=encoded, name="Ironory_Encoder")

    autoencoder.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mse",
        metrics=["mae"],
    )

    return autoencoder, encoder


def compute_anomaly_map(autoencoder, image_tensor: np.ndarray) -> Tuple[float, np.ndarray]:
    """Compute per-pixel difference map and scalar mean squared anomaly score.
    
    Args:
        autoencoder: Trained autoencoder model.
        image_tensor: Float32 image array with shape (1, 224, 224, 3) in [0, 1].
        
    Returns:
        (anomaly_score, diff_map_2d)
    """
    reconstructed = autoencoder.predict(image_tensor, verbose=0)
    diff = np.abs(image_tensor - reconstructed)  # Shape (1, 224, 224, 3)
    diff_map = np.mean(diff[0], axis=-1)  # Mean across color channels -> (224, 224)
    anomaly_score = float(np.mean(np.square(image_tensor - reconstructed)))
    return anomaly_score, diff_map
