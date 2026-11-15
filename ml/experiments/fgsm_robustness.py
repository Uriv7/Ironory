"""Fast Gradient Sign Method (FGSM) Adversarial Robustness Assessment.

Evaluates how sensitive industrial surface defect classifiers are to adversarial
camera sensor noise and targeted pixel perturbations (Goodfellow et al., 2014).
Formula: x_adv = clip(x + epsilon * sign(grad_x(Loss(theta, x, y))), 0, 1)

Generates:
1. Robustness degradation curves (Accuracy vs Epsilon).
2. Perturbation visualization comparison (Original vs Perturbation vs Adversarial).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger("ironory.ml.experiments.fgsm")


def create_adversarial_pattern(model: Any, input_image: Any, target_label: Any) -> Any:
    """Calculate gradient of loss with respect to input image."""
    import tensorflow as tf

    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy()

    with tf.GradientTape() as tape:
        tape.watch(input_image)
        prediction = model(input_image)
        loss = loss_fn(target_label, prediction)

    # Gradient of loss w.r.t input image
    gradient = tape.gradient(loss, input_image)
    # Get the sign of the gradients to create the perturbation
    signed_grad = tf.sign(gradient)
    return signed_grad


def generate_fgsm_adversarial_example(
    model: Any,
    image_tensor: Any,
    label_tensor: Any,
    epsilon: float = 0.05,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate FGSM adversarial example and perturbation map."""
    import tensorflow as tf

    perturbation = create_adversarial_pattern(model, image_tensor, label_tensor)
    adv_tensor = image_tensor + (epsilon * perturbation)
    adv_tensor = tf.clip_by_value(adv_tensor, 0.0, 1.0)
    return adv_tensor.numpy(), perturbation.numpy()


def evaluate_fgsm_robustness(
    model_path: Path = Path("ml/artifacts/baseline_cnn.keras"),
    epsilons: List[float] = [0.0, 0.01, 0.03, 0.05, 0.1, 0.15],
    num_samples: int = 50,
    output_dir: Path = Path("ml/artifacts/evaluation/fgsm"),
) -> Dict[str, Any]:
    """Evaluate accuracy drop as epsilon increases on test samples."""
    import tensorflow as tf
    from ml.datasets.neu_loader import load_neu_dataset

    output_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found at {model_path}")

    logger.info(f"Loading trained classifier from {model_path}...")
    model = tf.keras.models.load_model(str(model_path))

    _, _, test_ds, _ = load_neu_dataset(batch_size=32)

    # Collect test samples
    x_test, y_test = [], []
    for x_b, y_b in test_ds:
        x_test.append(x_b)
        y_test.append(y_b)
        if len(x_test) * 32 >= num_samples:
            break

    x_all = tf.concat(x_test, axis=0)[:num_samples]
    y_all = tf.concat(y_test, axis=0)[:num_samples]

    results = {}
    for eps in epsilons:
        correct = 0
        for i in range(len(x_all)):
            img = tf.expand_dims(x_all[i], axis=0)
            lbl = tf.expand_dims(y_all[i], axis=0)

            if eps == 0.0:
                pred = model(img, training=False)
            else:
                adv_x, _ = generate_fgsm_adversarial_example(model, img, lbl, epsilon=eps)
                pred = model(adv_x, training=False)

            if int(np.argmax(pred)) == int(lbl.numpy()[0]):
                correct += 1

        acc = correct / len(x_all)
        results[f"eps_{eps}"] = round(acc, 4)
        logger.info(f"Epsilon {eps:.2f} -> Adversarial Accuracy: {acc * 100:.2f}%")

    # Save metrics JSON
    metrics_path = output_dir / "fgsm_robustness_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"FGSM evaluation complete. Metrics saved to {metrics_path}")
    return results


if __name__ == "__main__":
    evaluate_fgsm_robustness()
