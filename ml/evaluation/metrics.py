"""Model Evaluation and Metrics Module for Industrial Defect Classification.

Calculates comprehensive classification performance metrics:
- Multiclass Confusion Matrix
- Per-class Precision, Recall, F1-Score, and Support
- Macro and Weighted Averages
- Saves visual evaluation artifacts and JSON metrics reports.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("ironory.ml.evaluation")


def evaluate_classifier(
    model,
    test_ds,
    class_names: List[str],
    output_dir: Optional[Path] = None,
) -> Dict[str, object]:
    """Evaluate trained model on test dataset and calculate detailed metrics.

    Args:
        model: Trained tf.keras.Model.
        test_ds: tf.data.Dataset providing (image_batch, label_batch).
        class_names: List of class names.
        output_dir: Directory to save confusion matrix plot and metrics.json.

    Returns:
        Dictionary containing overall accuracy, per-class metrics, and confusion matrix.
    """
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt

    y_true_list: List[int] = []
    y_pred_list: List[int] = []

    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true_list.extend(labels.numpy().tolist())
        y_pred_list.extend(np.argmax(preds, axis=1).tolist())

    y_true = np.array(y_true_list)
    y_pred = np.array(y_pred_list)

    # Scikit-learn classification report
    report_dict = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))

    accuracy = float(np.mean(y_true == y_pred))

    results = {
        "accuracy": accuracy,
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist(),
        "total_samples": len(y_true),
        "class_names": class_names,
    }

    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # Save metrics JSON
        metrics_file = out_path / "metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(results, f, indent=2)

        # Plot confusion matrix
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        ax.figure.colorbar(im, ax=ax)
        ax.set(
            xticks=np.arange(cm.shape[1]),
            yticks=np.arange(cm.shape[0]),
            xticklabels=class_names,
            yticklabels=class_names,
            title="Confusion Matrix — Industrial Defect Classification",
            ylabel="Ground Truth",
            xlabel="Predicted Defect",
        )
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j,
                    i,
                    format(cm[i, j], "d"),
                    ha="center",
                    va="center",
                    color="white" if cm[i, j] > thresh else "black",
                )

        fig.tight_layout()
        cm_plot_file = out_path / "confusion_matrix.png"
        fig.savefig(cm_plot_file, dpi=180)
        plt.close(fig)
        logger.info(f"Saved evaluation metrics to {metrics_file} and confusion matrix to {cm_plot_file}")

    return results
