# FraudSentinel X: Person 1 AI/ML Module

This is a self-contained hackathon MVP for synthetic transaction fraud analysis. It supports statement ingestion, shared feature engineering, XGBoost supervised scoring, Isolation Forest behavioral anomaly detection, transparent risk scoring, and SHAP explanations.

> This system is a hackathon MVP using synthetic/public data and is not a production banking fraud detection system.

## Install and run

From the project root:

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m ml.train
py -3.13 -m ml.evaluate
py -3.13 run_demo.py
py -3.13 -m pytest -q
```

The `python` command can be used instead when Python is on PATH. Training creates `ml/data/demo_transactions.csv`, `ml/fraud_model.pkl`, `ml/anomaly_model.pkl`, `ml/feature_metadata.json`, and evaluation artifacts. The generated demo includes controlled synthetic transaction `TXN5721`.

## Backend integration

```python
from ml.predict import predict_transaction, predict_dataframe, get_model_working

result = predict_transaction(transaction_dict)
results = predict_dataframe(dataframe)
working = get_model_working(transaction_dict)
```

The result is JSON-serializable and contains `risk_score` (0-100), `risk_level`, model signal, normalized anomaly signal, anomaly flag, SHAP-derived risk factors, and processed features.

## Statements

`ml.data_loader.load_statement("statement.csv")` and the same function for `.xlsx` accept common aliases for date, description, debit, credit, amount, balance, and reference. Device, beneficiary, and location fields unavailable in a statement are marked `UNKNOWN` or set to documented neutral values; they are never invented. Invalid dates and non-positive amounts are discarded by the loader and can be inspected with `validation.py` for strict validation.

## Risk and models

The risk score combines the XGBoost model signal (55%), normalized Isolation Forest anomaly signal (25%), and configurable behavioral indicators (20%). These weights are a transparent demo policy, not a scientifically validated score or calibrated fraud probability. Isolation Forest's negative `score_samples` output is transformed with `clip(0.5 - raw, 0, 1)` and is explicitly not a probability. SHAP TreeExplainer contributions are mapped to human-readable evidence.

## Outputs and limitations

`ml/evaluation_results.json` contains real held-out precision, recall, F1, PR-AUC, false-positive rate, and confusion matrix. `ml/artifacts/confusion_matrix.png` is generated during evaluation. The synthetic data is designed for demonstration and does not represent NPCI, bank, UPI, or any real customer behavior. Real deployment would require approved data governance, calibration, drift monitoring, privacy controls, and security review.
