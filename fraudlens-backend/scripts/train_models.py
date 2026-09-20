"""
FraudLens AI - ML Training Pipeline
Generates synthetic behavioral UPI records, trains RandomForest fraud classifier
and IsolationForest anomaly detector, and saves models to models/ directory.
"""

import os
import sys
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def train_and_save_models():
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(models_dir, exist_ok=True)

    np.random.seed(42)
    n_samples = 2000

    # Synthetic features: [amount, amount_ratio, hour, failed_attempts, is_night_txn]
    # Normal distribution for legitimate transactions
    amounts_legit = np.random.exponential(scale=1500, size=int(n_samples * 0.9))
    ratios_legit = np.random.normal(loc=1.0, scale=0.4, size=int(n_samples * 0.9))
    hours_legit = np.random.choice(range(6, 23), size=int(n_samples * 0.9))
    failed_legit = np.random.choice([0, 1], p=[0.95, 0.05], size=int(n_samples * 0.9))
    night_legit = np.zeros(int(n_samples * 0.9))

    # Anomalous / Fraud transactions
    amounts_fraud = np.random.exponential(scale=45000, size=int(n_samples * 0.1))
    ratios_fraud = np.random.uniform(low=8.0, high=35.0, size=int(n_samples * 0.1))
    hours_fraud = np.random.choice(range(0, 6), size=int(n_samples * 0.1))
    failed_fraud = np.random.choice([1, 2, 3, 4], p=[0.2, 0.4, 0.3, 0.1], size=int(n_samples * 0.1))
    night_fraud = np.ones(int(n_samples * 0.1))

    X_legit = np.column_stack([amounts_legit, ratios_legit, hours_legit, failed_legit, night_legit])
    y_legit = np.zeros(len(X_legit))

    X_fraud = np.column_stack([amounts_fraud, ratios_fraud, hours_fraud, failed_fraud, night_fraud])
    y_fraud = np.ones(len(X_fraud))

    X = np.vstack([X_legit, X_fraud])
    y = np.concatenate([y_legit, y_fraud])

    # 1. Train Supervised RandomForestClassifier
    print("Training Supervised Fraud Classifier (RandomForest)...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X, y)
    fraud_path = os.path.join(models_dir, "fraud_model.pkl")
    joblib.dump(clf, fraud_path)
    print(f"  Saved to {fraud_path}")

    # 2. Train Unsupervised IsolationForest (uses amount, ratio, hour)
    print("Training Unsupervised Anomaly Detector (IsolationForest)...")
    X_unsupervised = X[:, [0, 1, 2]]
    iso = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
    iso.fit(X_unsupervised)
    iso_path = os.path.join(models_dir, "anomaly_model.pkl")
    joblib.dump(iso, iso_path)
    print(f"  Saved to {iso_path}")

    # 3. Fit and save Scaler
    scaler = StandardScaler()
    scaler.fit(X)
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"  Saved to {scaler_path}")

    print("Model training completed successfully.")

if __name__ == "__main__":
    train_and_save_models()
