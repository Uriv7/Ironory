"""LSTM Sequence Model for Manufacturing Defect Rate Forecasting.

Predicts defect rates and failure likelihood across upcoming shifts/days based on
historical rolling inspection logs and quality degradation trends.
"""

from __future__ import annotations

import logging
from typing import Tuple

import numpy as np

logger = logging.getLogger("ironory.ml.models.lstm")


def build_defect_forecasting_lstm(
    lookback_window: int = 14,
    num_features: int = 4,
    forecast_horizon: int = 7,
    learning_rate: float = 1e-3,
):
    """Build and compile LSTM sequential model for quality drift forecasting."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    inputs = layers.Input(shape=(lookback_window, num_features), name="historical_quality_metrics")

    x = layers.LSTM(64, return_sequences=True, name="lstm_layer_1")(inputs)
    x = layers.Dropout(0.2, name="dropout_1")(x)
    x = layers.LSTM(32, return_sequences=False, name="lstm_layer_2")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    x = layers.Dense(32, activation="relu", name="dense_features")(x)
    outputs = layers.Dense(forecast_horizon, activation="linear", name="predicted_defect_rates")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Ironory_Defect_Forecasting_LSTM")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mse",
        metrics=["mae"],
    )

    return model
