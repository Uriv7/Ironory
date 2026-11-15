"""Unit tests for Ironory Deep Learning models and inference engine."""

import os
from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from ml.datasets.neu_loader import (
    DEFECT_CLASSES,
    ensure_dataset,
    get_dataset_statistics,
    prepare_dataset_splits,
)
from ml.models.cnn.baseline_cnn import build_baseline_cnn
from ml.models.transfer_learning.mobilenet import build_mobilenet_v2
from ml.models.transfer_learning.efficientnet import build_efficientnet_b0
from ml.models.autoencoder.conv_autoencoder import build_conv_autoencoder
from ml.models.segmentation.unet import build_unet
from ml.models.gan.dcgan import build_generator, build_discriminator
from ml.models.lstm.forecast_lstm import build_defect_forecasting_lstm
from ml.inference.service import InferenceEngine


def test_neu_dataset_structure():
    data_dir = ensure_dataset()
    stats = get_dataset_statistics(data_dir)
    assert len(stats["classes"]) == 6
    assert stats["total_images"] > 0
    for cls_name in DEFECT_CLASSES:
        assert (data_dir / cls_name).exists()
        assert len(list((data_dir / cls_name).glob("*.jpg"))) > 0


def test_dataset_splits():
    splits = prepare_dataset_splits(split_ratios=(0.7, 0.15, 0.15), seed=42)
    assert "train" in splits
    assert "val" in splits
    assert "test" in splits
    assert len(splits["train"]) > len(splits["val"])


def test_baseline_cnn_architecture():
    model = build_baseline_cnn(input_shape=(224, 224, 3), num_classes=6)
    assert model.input_shape == (None, 224, 224, 3)
    assert model.output_shape == (None, 6)
    assert model.name == "Ironory_Baseline_CNN"


def test_mobilenet_architecture():
    model, base = build_mobilenet_v2(input_shape=(224, 224, 3), num_classes=6, weights=None)
    assert model.output_shape == (None, 6)
    assert not base.trainable


def test_efficientnet_architecture():
    model, base = build_efficientnet_b0(input_shape=(224, 224, 3), num_classes=6, weights=None)
    assert model.output_shape == (None, 6)


def test_autoencoder_architecture():
    ae, enc = build_conv_autoencoder(input_shape=(224, 224, 3), latent_dim=32)
    assert ae.input_shape == (None, 224, 224, 3)
    assert ae.output_shape == (None, 224, 224, 3)


def test_unet_architecture():
    model = build_unet(input_shape=(224, 224, 3), num_classes=1)
    assert model.input_shape == (None, 224, 224, 3)
    assert model.output_shape == (None, 224, 224, 1)


def test_gan_architecture():
    gen = build_generator(latent_dim=100)
    disc = build_discriminator(input_shape=(224, 224, 3))
    assert gen.output_shape == (None, 224, 224, 3)
    assert disc.output_shape == (None, 1)


def test_lstm_forecasting_architecture():
    model = build_defect_forecasting_lstm(lookback_window=14, num_features=4, forecast_horizon=7)
    assert model.input_shape == (None, 14, 4)
    assert model.output_shape == (None, 7)
