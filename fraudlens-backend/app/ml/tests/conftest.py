import pytest

from ml.model_utils import ANOMALY_MODEL_PATH, DATA_DIR, FRAUD_MODEL_PATH
from ml.train import train_models


@pytest.fixture(scope="session", autouse=True)
def trained_models():
    if not FRAUD_MODEL_PATH.exists() or not ANOMALY_MODEL_PATH.exists():
        train_models()
    return True
