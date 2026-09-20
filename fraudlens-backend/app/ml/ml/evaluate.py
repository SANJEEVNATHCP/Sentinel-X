"""Evaluate persisted models and save real metrics/artifacts."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, ConfusionMatrixDisplay

from .features import engineer_features
from .model_utils import ARTIFACT_DIR, DATA_DIR, EVALUATION_PATH, load_fraud_model


def evaluate_model() -> dict:
    import pandas as pd
    data = pd.read_csv(DATA_DIR / "demo_transactions.csv")
    split = json.loads((DATA_DIR / "split.json").read_text(encoding="utf-8"))
    test = data.iloc[split["test_indices"]]
    features = engineer_features(test)
    labels = test["fraud_label"].astype(int)
    probabilities = load_fraud_model().predict_proba(features)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    tn, fp, _, _ = matrix.ravel()
    metrics = {"precision": float(precision_score(labels, predictions, zero_division=0)), "recall": float(recall_score(labels, predictions, zero_division=0)), "f1_score": float(f1_score(labels, predictions, zero_division=0)), "pr_auc": float(average_precision_score(labels, probabilities)), "false_positive_rate": float(fp / max(1, tn + fp)), "confusion_matrix": matrix.tolist()}
    EVALUATION_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    ARTIFACT_DIR.mkdir(exist_ok=True)
    ConfusionMatrixDisplay(matrix, display_labels=["Normal", "Suspicious"]).plot(cmap="Blues")
    plt.tight_layout(); plt.savefig(ARTIFACT_DIR / "confusion_matrix.png", dpi=140); plt.close()
    model = load_fraud_model()
    importance = np.asarray(model.feature_importances_)
    order = np.argsort(importance)
    plt.figure(figsize=(8, 5))
    plt.barh(np.asarray(features.columns)[order], importance[order], color="#2563eb")
    plt.title("XGBoost Feature Importance")
    plt.tight_layout(); plt.savefig(ARTIFACT_DIR / "risk_feature_importance.png", dpi=140); plt.close()
    try:
        import shap
        shap_values = shap.TreeExplainer(model)(features).values
        if shap_values.ndim == 3:
            shap_values = shap_values[:, :, 1]
        shap.summary_plot(shap_values, features, show=False, plot_size=(9, 5))
        plt.tight_layout(); plt.savefig(ARTIFACT_DIR / "shap_summary.png", dpi=140); plt.close()
    except Exception:
        pass
    return metrics


if __name__ == "__main__":
    print(json.dumps(evaluate_model(), indent=2))
