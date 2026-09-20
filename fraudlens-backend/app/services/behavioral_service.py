"""
FraudLens AI - Behavioral Baseline Service
Calculates individual user financial patterns to spot sudden anomalies.
"""

from typing import Dict, Any, List
import numpy as np

class BehavioralService:
    @staticmethod
    def calculate_user_profile(amounts: List[float]) -> Dict[str, float]:
        """Calculates user historical mean, standard deviation, and median."""
        if not amounts:
            return {"mean": 0.0, "std": 0.0, "median": 0.0, "count": 0}

        arr = np.array(amounts)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr)) if len(arr) > 1 else 0.0
        median_val = float(np.median(arr))

        return {
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "median": round(median_val, 2),
            "count": len(amounts)
        }

    @staticmethod
    def evaluate_transaction_deviation(amount: float, user_mean: float, user_std: float) -> Dict[str, Any]:
        """Compares a specific transaction against the user baseline."""
        if user_mean <= 0:
            return {"ratio": 1.0, "z_score": 0.0, "is_outlier": False}

        ratio = round(amount / user_mean, 2)
        z_score = round((amount - user_mean) / (user_std + 1e-5), 2) if user_std > 0 else 0.0
        is_outlier = ratio > 4.0 or z_score > 3.0

        return {
            "ratio": ratio,
            "z_score": z_score,
            "is_outlier": is_outlier
        }
