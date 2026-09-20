"""
FraudLens AI - Evidence Engine
Assembles objective, auditable signal items comparing observed values against reference baselines.
"""

from typing import Dict, Any, List

class EvidenceEngine:
    @staticmethod
    def create_evidence_item(
        category: str,
        signal: str,
        observed_value: str,
        reference_value: str,
        severity: str,
        confidence: float,
        risk_contribution: float,
        source: str,
        explanation: str
    ) -> Dict[str, Any]:
        """Creates a standardized evidence dictionary item."""
        return {
            "category": category,
            "signal": signal,
            "observed_value": str(observed_value),
            "reference_value": str(reference_value),
            "severity": severity, # "LOW", "MEDIUM", "HIGH", "CRITICAL"
            "confidence": round(float(confidence), 2),
            "risk_contribution": round(float(risk_contribution), 1),
            "source": source,
            "explanation": explanation
        }
