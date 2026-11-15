"""Ironory Industrial Image Augmentation & Sensor Drift Simulation Module.

Simulates real-world manufacturing line optical conditions:
1. High-speed strip conveyance motion blur.
2. Uneven factory halogen / LED illumination gradients.
3. Sensor thermal noise and metal scale particulate fouling.
4. Classical geometric invariance (flips, rotations, scaling).
"""

from __future__ import annotations

import logging
from typing import Any, Tuple

import numpy as np

logger = logging.getLogger("ironory.ml.preprocessing.augmentation")


def build_augmentation_pipeline(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    rotation_range: float = 0.1,
    zoom_range: float = 0.08,
    contrast_range: float = 0.1,
) -> Any:
    """Build TensorFlow Keras preprocessing sequential model for data augmentation."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    pipeline = models.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.RandomFlip("horizontal_and_vertical"),
            layers.RandomRotation(rotation_range, fill_mode="reflect"),
            layers.RandomZoom(zoom_range, fill_mode="reflect"),
            layers.RandomContrast(contrast_range),
        ],
        name="Ironory_Augmentation_Pipeline",
    )
    return pipeline


def apply_industrial_noise(
    image: np.ndarray,
    noise_type: str = "gaussian",
    intensity: float = 0.05,
) -> np.ndarray:
    """Apply sensor noise or particulate interference to normalized [0, 1] RGB image.

    Args:
        image: Normalized float32 ndarray of shape (H, W, C) in [0, 1].
        noise_type: 'gaussian', 'salt_pepper', or 'scale_particulate'.
        intensity: Magnitude factor of perturbation in [0.01, 0.2].
    """
    img = np.copy(image)
    h, w, c = img.shape

    if noise_type == "gaussian":
        noise = np.random.normal(0.0, intensity, (h, w, c)).astype(np.float32)
        noisy_img = np.clip(img + noise, 0.0, 1.0)
        return noisy_img

    elif noise_type == "salt_pepper":
        mask = np.random.rand(h, w)
        # Salt (bright speckles)
        img[mask < (intensity / 2.0)] = 1.0
        # Pepper (dark scale spots)
        img[mask > (1.0 - (intensity / 2.0))] = 0.0
        return img

    elif noise_type == "scale_particulate":
        # Simulates random small flecks of airborne iron oxide
        num_speckles = int(intensity * 100)
        for _ in range(num_speckles):
            cy, cx = np.random.randint(0, h), np.random.randint(0, w)
            radius = np.random.randint(1, 4)
            y_min, y_max = max(0, cy - radius), min(h, cy + radius)
            x_min, x_max = max(0, cx - radius), min(w, cx + radius)
            img[y_min:y_max, x_min:x_max, :] *= np.random.uniform(0.1, 0.4)
        return img

    return img


def simulate_factory_drift(
    image: np.ndarray,
    motion_blur: bool = True,
    lighting_gradient: bool = True,
    sensor_noise: bool = True,
) -> np.ndarray:
    """Simulate composite factory floor acquisition degradation on steel surface frame.

    Args:
        image: Normalized float32 ndarray of shape (H, W, C) in [0, 1].
    """
    import cv2

    img = np.copy(image)
    h, w, _ = img.shape

    # 1. Non-uniform factory lighting gradient across strip width
    if lighting_gradient:
        # Create 1D linear ramp along horizontal axis
        x_grad = np.linspace(0.85, 1.15, w, dtype=np.float32)
        gradient_2d = np.tile(x_grad, (h, 1))[:, :, np.newaxis]
        img = np.clip(img * gradient_2d, 0.0, 1.0)

    # 2. Conveyance motion blur along rolling direction (vertical axis)
    if motion_blur:
        kernel_size = 5
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        kernel[:, int((kernel_size - 1) / 2)] = np.ones(kernel_size)
        kernel /= kernel_size
        img = cv2.filter2D(img, -1, kernel)

    # 3. Sensor thermal noise
    if sensor_noise:
        img = apply_industrial_noise(img, noise_type="gaussian", intensity=0.03)

    return np.clip(img, 0.0, 1.0)
