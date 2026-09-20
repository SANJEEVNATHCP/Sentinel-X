"""Transparent, configurable risk score. This is not a calibrated probability."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskWeights:
    model: float = 55.0
    anomaly: float = 25.0
    behavior: float = 20.0

WEIGHTS = RiskWeights()


def risk_level(score: int | float) -> str:
    value = float(score)
    if value < 30:
        return "Low"
    if value < 60:
        return "Medium"
    if value < 80:
        return "High"
    return "Critical"


def calculate_risk_score(model_signal: float, anomaly_score: float, features: dict[str, float], weights: RiskWeights = WEIGHTS) -> dict[str, int | str]:
    behavioral = min(1.0, sum([
        0.30 * float(features.get("is_new_device", 0)),
        0.25 * float(features.get("is_new_beneficiary", 0)),
        0.20 * float(features.get("unusual_hour_flag", 0)),
        0.15 * float(features.get("high_velocity_flag", 0)),
        0.10 * float(features.get("high_amount_flag", 0)),
    ]))
    score = round(100 * (weights.model * float(model_signal) + weights.anomaly * float(anomaly_score) + weights.behavior * behavioral) / 100)
    score = max(0, min(100, score))
    return {"risk_score": score, "risk_level": risk_level(score)}
