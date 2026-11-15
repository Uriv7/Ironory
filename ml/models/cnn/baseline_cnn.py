"""Baseline Convolutional Neural Network for Industrial Surface Defect Classification.

Architecture:
- 4 Convolutional blocks with Batch Normalization, ReLU activation, and Max Pooling.
- Global Average Pooling to reduce parameter count and mitigate overfitting.
- Fully connected classification head with Dropout.
- Target dataset: NEU Surface Defect Database (6 classes).
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

logger = logging.getLogger("ironory.ml.models.cnn")


def build_baseline_cnn(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 6,
    dropout_rate: float = 0.5,
    learning_rate: float = 1e-3,
):
    """Build and compile the Baseline CNN model."""
    import tensorflow as tf
    from tensorflow.keras import layers, models, regularizers

    inputs = layers.Input(shape=input_shape, name="input_image")

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding="same", name="conv1_1")(inputs)
    x = layers.BatchNormalization(name="bn1_1")(x)
    x = layers.ReLU(name="relu1_1")(x)
    x = layers.Conv2D(32, (3, 3), padding="same", name="conv1_2")(x)
    x = layers.BatchNormalization(name="bn1_2")(x)
    x = layers.ReLU(name="relu1_2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding="same", name="conv2_1")(x)
    x = layers.BatchNormalization(name="bn2_1")(x)
    x = layers.ReLU(name="relu2_1")(x)
    x = layers.Conv2D(64, (3, 3), padding="same", name="conv2_2")(x)
    x = layers.BatchNormalization(name="bn2_2")(x)
    x = layers.ReLU(name="relu2_2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding="same", name="conv3_1")(x)
    x = layers.BatchNormalization(name="bn3_1")(x)
    x = layers.ReLU(name="relu3_1")(x)
    x = layers.MaxPooling2D((2, 2), name="pool3")(x)

    # Block 4 - Target layer for Grad-CAM
    x = layers.Conv2D(256, (3, 3), padding="same", name="conv4_1")(x)
    x = layers.BatchNormalization(name="bn4_1")(x)
    x = layers.ReLU(name="relu4_1")(x)
    x = layers.MaxPooling2D((2, 2), name="pool4")(x)

    # Classification Head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.Dense(256, kernel_regularizer=regularizers.l2(1e-4), name="dense_features")(x)
    x = layers.BatchNormalization(name="bn_features")(x)
    x = layers.ReLU(name="relu_features")(x)
    x = layers.Dropout(dropout_rate, name="dropout")(x)

    outputs = layers.Dense(num_classes, activation="softmax", name="defect_probabilities")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Ironory_Baseline_CNN")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model
