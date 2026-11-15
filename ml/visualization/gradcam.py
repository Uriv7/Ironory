"""Grad-CAM: Gradient-Weighted Class Activation Mapping for Explainable AI (XAI).

Generates visual explanations for decisions made by CNN models, highlighting
the exact spatial regions on the steel surface that contributed to the defect classification.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger("ironory.ml.visualization.gradcam")


def generate_gradcam_heatmap(
    model,
    image_tensor: np.ndarray,
    target_layer_name: Optional[str] = None,
    pred_index: Optional[int] = None,
) -> np.ndarray:
    """Generate Grad-CAM heatmap for a given input image tensor and target convolutional layer.

    Args:
        model: Trained tf.keras.Model.
        image_tensor: Normalized numpy array of shape (1, H, W, C) in [0, 1].
        target_layer_name: Name of target convolutional layer. If None, automatically searches
            for the last 4D convolutional layer.
        pred_index: Target class index. If None, uses top predicted class.

    Returns:
        2D numpy array of shape (H, W) with heatmap values in [0, 1].
    """
    import tensorflow as tf

    # Find target conv layer if not provided
    if target_layer_name is None:
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D) or "conv" in layer.name.lower():
                target_layer_name = layer.name
                break

    if target_layer_name is None:
        raise ValueError("Could not automatically locate a convolutional layer for Grad-CAM.")

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(target_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image_tensor)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # Gradients of predicted class with respect to the feature map activations
    grads = tape.gradient(class_channel, conv_outputs)
    # Global average pooling of gradients (importance weights)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weighted combination of feature maps
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Apply ReLU to focus only on features that have a positive influence on the class
    heatmap = tf.maximum(heatmap, 0.0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val != 0:
        heatmap = heatmap / max_val

    heatmap_np = heatmap.numpy()

    # Resize heatmap to match input image resolution (H, W)
    h, w = image_tensor.shape[1], image_tensor.shape[2]
    heatmap_img = Image.fromarray(np.uint8(255 * heatmap_np)).resize((w, h), Image.Resampling.BICUBIC)
    return np.array(heatmap_img, dtype=np.float32) / 255.0


def overlay_gradcam(
    original_image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.45,
    colormap_name: str = "jet",
) -> Tuple[Image.Image, np.ndarray]:
    """Superimpose Grad-CAM heatmap over original RGB surface image.

    Args:
        original_image: PIL Image of the inspected surface.
        heatmap: 2D numpy array of shape (H, W) in [0, 1].
        alpha: Blend ratio between 0.0 (original only) and 1.0 (heatmap only).
        colormap_name: Matplotlib colormap (default 'jet').

    Returns:
        (blended_pil_image, blended_numpy_array)
    """
    import matplotlib.cm as cm

    # Convert heatmap to RGB using colormap
    cmap = cm.get_cmap(colormap_name)
    colored_heatmap = cmap(heatmap)  # RGBA in [0, 1]
    colored_heatmap = np.uint8(255 * colored_heatmap[..., :3])  # RGB uint8

    orig_rgb = np.array(original_image.convert("RGB").resize((heatmap.shape[1], heatmap.shape[0])))

    # Alpha blend: output = orig * (1 - alpha) + heatmap * alpha
    superimposed = np.uint8(orig_rgb * (1.0 - alpha) + colored_heatmap * alpha)
    superimposed_pil = Image.fromarray(superimposed)

    return superimposed_pil, superimposed
