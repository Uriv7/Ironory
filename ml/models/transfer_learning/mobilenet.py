"""MobileNetV2 Transfer Learning model for Industrial Defect Classification."""

from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger("ironory.ml.models.mobilenet")


def build_mobilenet_v2(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 6,
    weights: str = "imagenet",
    freeze_base: bool = True,
    dropout_rate: float = 0.4,
    learning_rate: float = 1e-4,
):
    """Build MobileNetV2 with custom classification head for industrial defect detection."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    # Base feature extractor
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights=weights,
    )
    base_model.trainable = not freeze_base

    inputs = layers.Input(shape=input_shape, name="input_image")
    # MobileNet expects inputs in [-1, 1], our data is in [0, 1]
    x = layers.Lambda(lambda img: (img * 2.0) - 1.0, name="mobilenet_preprocessor")(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_bn")(x)
    x = layers.Dense(128, activation="relu", name="head_dense")(x)
    x = layers.Dropout(dropout_rate, name="head_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="defect_probabilities")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Ironory_MobileNetV2")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model, base_model


def fine_tune_mobilenet(
    model,
    base_model,
    fine_tune_at: int = 100,
    fine_tune_lr: float = 1e-5,
):
    """Unfreeze top layers of MobileNetV2 for domain-specific fine tuning."""
    import tensorflow as tf

    base_model.trainable = True
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    optimizer = tf.keras.optimizers.Adam(learning_rate=fine_tune_lr)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
