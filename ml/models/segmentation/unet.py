"""U-Net Architecture for Precise Industrial Defect Segmentation.

Produces a pixel-level binary or multi-class mask pinpointing defective areas,
enabling exact area calculation, defect perimeter measurement, and severity grading.
"""

from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger("ironory.ml.models.segmentation")


def _conv_block(inputs, num_filters: int, name_prefix: str):
    import tensorflow as tf
    from tensorflow.keras import layers

    x = layers.Conv2D(num_filters, (3, 3), padding="same", name=f"{name_prefix}_conv1")(inputs)
    x = layers.BatchNormalization(name=f"{name_prefix}_bn1")(x)
    x = layers.ReLU(name=f"{name_prefix}_relu1")(x)

    x = layers.Conv2D(num_filters, (3, 3), padding="same", name=f"{name_prefix}_conv2")(x)
    x = layers.BatchNormalization(name=f"{name_prefix}_bn2")(x)
    x = layers.ReLU(name=f"{name_prefix}_relu2")(x)
    return x


def dice_coefficient(y_true, y_pred, smooth: float = 1e-6):
    import tensorflow as tf

    y_true_f = tf.cast(tf.reshape(y_true, [-1]), tf.float32)
    y_pred_f = tf.cast(tf.reshape(y_pred, [-1]), tf.float32)
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2.0 * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)


def dice_loss(y_true, y_pred):
    return 1.0 - dice_coefficient(y_true, y_pred)


def build_unet(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 1,
    learning_rate: float = 1e-4,
):
    """Build and compile U-Net segmentation network with skip connections."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    inputs = layers.Input(shape=input_shape, name="surface_image")

    # Encoder (Contracting Path)
    c1 = _conv_block(inputs, 32, "enc1")
    p1 = layers.MaxPooling2D((2, 2), name="pool1")(c1)  # 112x112

    c2 = _conv_block(p1, 64, "enc2")
    p2 = layers.MaxPooling2D((2, 2), name="pool2")(c2)  # 56x56

    c3 = _conv_block(p2, 128, "enc3")
    p3 = layers.MaxPooling2D((2, 2), name="pool3")(c3)  # 28x28

    c4 = _conv_block(p3, 256, "enc4")
    p4 = layers.MaxPooling2D((2, 2), name="pool4")(c4)  # 14x14

    # Bottleneck
    bn = _conv_block(p4, 512, "bottleneck")

    # Decoder (Expansive Path with Skip Connections)
    u4 = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding="same", name="up4")(bn)
    u4 = layers.Concatenate(name="concat4")([u4, c4])
    d4 = _conv_block(u4, 256, "dec4")

    u3 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding="same", name="up3")(d4)
    u3 = layers.Concatenate(name="concat3")([u3, c3])
    d3 = _conv_block(u3, 128, "dec3")

    u2 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding="same", name="up2")(d3)
    u2 = layers.Concatenate(name="concat2")([u2, c2])
    d2 = _conv_block(u2, 64, "dec2")

    u1 = layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding="same", name="up1")(d2)
    u1 = layers.Concatenate(name="concat1")([u1, c1])
    d1 = _conv_block(u1, 32, "dec1")

    # Final mask prediction
    activation = "sigmoid" if num_classes == 1 else "softmax"
    outputs = layers.Conv2D(num_classes, (1, 1), activation=activation, name="defect_mask")(d1)

    model = models.Model(inputs=inputs, outputs=outputs, name="Ironory_UNet")

    loss = dice_loss if num_classes == 1 else "sparse_categorical_crossentropy"
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss=loss,
        metrics=[dice_coefficient, "accuracy"],
    )

    return model
