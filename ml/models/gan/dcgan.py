"""Deep Convolutional GAN (DCGAN) for Synthetic Industrial Defect Generation.

Academic and research component for generating realistic defect patterns (crazing, scratches, inclusions)
to expand training datasets in low-sample manufacturing regimes.
"""

from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger("ironory.ml.models.gan")


def build_generator(latent_dim: int = 100):
    """Build DCGAN Generator to map random latent vectors to 224x224x3 surface images."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    model = models.Sequential(name="DCGAN_Generator")

    # Foundation for 7x7 image
    model.add(layers.Input(shape=(latent_dim,)))
    model.add(layers.Dense(7 * 7 * 256, use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU(0.2))
    model.add(layers.Reshape((7, 7, 256)))

    # Upsample to 14x14
    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding="same", use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU(0.2))

    # Upsample to 28x28
    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding="same", use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU(0.2))

    # Upsample to 56x56
    model.add(layers.Conv2DTranspose(32, (5, 5), strides=(2, 2), padding="same", use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU(0.2))

    # Upsample to 112x112
    model.add(layers.Conv2DTranspose(16, (5, 5), strides=(2, 2), padding="same", use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU(0.2))

    # Upsample to 224x224 with 3 channels
    model.add(layers.Conv2DTranspose(3, (5, 5), strides=(2, 2), padding="same", activation="tanh"))

    return model


def build_discriminator(input_shape: Tuple[int, int, int] = (224, 224, 3)):
    """Build DCGAN Discriminator to classify surface images as authentic or synthesized."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    model = models.Sequential(name="DCGAN_Discriminator")
    model.add(layers.Input(shape=input_shape))

    model.add(layers.Conv2D(32, (5, 5), strides=(2, 2), padding="same"))
    model.add(layers.LeakyReLU(0.2))
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding="same"))
    model.add(layers.LeakyReLU(0.2))
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding="same"))
    model.add(layers.LeakyReLU(0.2))
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(256, (5, 5), strides=(2, 2), padding="same"))
    model.add(layers.LeakyReLU(0.2))
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(1, activation="sigmoid"))

    return model
