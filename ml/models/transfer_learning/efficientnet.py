"""EfficientNetB0 Transfer Learning model for Industrial Defect Classification."""

from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger("ironory.ml.models.efficientnet")


def build_efficientnet_b0(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 6,
    weights: str = "imagenet",
    freeze_base: bool = True,
    dropout_rate: float = 0.4,
    learning_rate: float = 1e-4,
):
    """Build EfficientNetB0 with custom classification head for industrial defect detection."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=input_shape,
        include_top=False,
        weights=weights,
    )
    base_model.trainable = not freeze_base

    inputs = layers.Input(shape=input_shape, name="input_image")
    # EfficientNet has internal rescaling from [0, 255], pass scaled [0, 255] or [0, 1] * 255
    x = layers.Lambda(lambda img: img * 255.0, name="efficientnet_rescaling")(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_bn")(x)
    x = layers.Dense(256, activation="relu", name="head_dense")(x)
    x = layers.Dropout(dropout_rate, name="head_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="defect_probabilities")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Ironory_EfficientNetB0")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model, base_model
