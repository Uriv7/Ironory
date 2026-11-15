"""Training script for LSTM Time-Series Defect Rate Forecasting.

Simulates rolling production defect metrics over 180 shifts, trains the 2-layer LSTM
forecasting network, and saves to ml/artifacts/forecast_lstm.keras.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ironory.ml.training.lstm")


def train_lstm_forecast(
    epochs: int = 15,
    lookback_window: int = 14,
    forecast_horizon: int = 7,
    output_dir: Path = Path("ml/artifacts"),
):
    import numpy as np
    import tensorflow as tf
    from ml.models.lstm.forecast_lstm import build_defect_forecasting_lstm

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "forecast_lstm.keras"

    # Generate synthetic time-series production quality drift data
    rng = np.random.RandomState(42)
    n_days = 240
    # Features: [defect_rate, total_inspections, severity_index, machine_temp_c]
    time = np.linspace(0, 12 * np.pi, n_days)
    base_rate = 0.05 + 0.03 * np.sin(time) + rng.normal(0, 0.01, n_days).clip(-0.02, 0.04)
    total_inspections = (rng.normal(1200, 150, n_days) / 2000.0).clip(0.1, 1.0)
    severity_index = (base_rate * 4.0 + rng.normal(0.2, 0.05, n_days)).clip(0.0, 1.0)
    machine_temp = (0.5 + 0.2 * np.cos(time / 2) + rng.normal(0, 0.03, n_days)).clip(0.0, 1.0)

    series = np.stack([base_rate, total_inspections, severity_index, machine_temp], axis=1)

    # Prepare rolling windows
    x_windows = []
    y_targets = []
    for i in range(len(series) - lookback_window - forecast_horizon):
        x_windows.append(series[i : i + lookback_window])
        # Target: defect rate over future forecast_horizon days
        y_targets.append(series[i + lookback_window : i + lookback_window + forecast_horizon, 0])

    x = np.array(x_windows, dtype=np.float32)
    y = np.array(y_targets, dtype=np.float32)

    n_train = int(len(x) * 0.8)
    x_train, y_train = x[:n_train], y[:n_train]
    x_val, y_val = x[n_train:], y[n_train:]

    logger.info(f"Training LSTM on {len(x_train)} sequences, validating on {len(x_val)} sequences...")
    model = build_defect_forecasting_lstm(
        lookback_window=lookback_window,
        num_features=4,
        forecast_horizon=forecast_horizon,
    )

    model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=16,
        verbose=1,
    )

    model.save(str(checkpoint_path))
    logger.info(f"Saved forecasting LSTM model to: {checkpoint_path}")
    return model


if __name__ == "__main__":
    train_lstm_forecast()
