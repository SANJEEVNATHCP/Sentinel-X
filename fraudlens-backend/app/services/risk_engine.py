"""
FraudLens AI - Centralized Deterministic Risk Engine
Combines ML probabilities, anomaly indicators, rule contributions, and external intelligence.
Calculates deterministic 0-100 score and maps to standard risk tiers.
"""

from typing import Dict, Any, List, Tuple

class RiskEngine:
    @staticmethod
    def calculate_risk(
        base_points: float = 0.0,
        risk_factors: List[Dict[str, Any]] = None,
        penalties: List[float] = None
    ) -> Tuple[float, str]:
        """
        Calculates deterministic score clamped strictly between 0 and 100.
        Maps to:
        0 - 24: LOW
        25 - 49: MODERATE
        50 - 69: SUSPICIOUS
        70 - 100: HIGH_RISK
        """
        total = base_points
        if risk_factors:
            for rf in risk_factors:
                total += rf.get("contribution", 0.0)
                
        if penalties:
            for p in penalties:
                total += p

        clamped = round(max(0.0, min(100.0, total)), 1)

        if clamped >= 70.0:
            level = "HIGH_RISK"
        elif clamped >= 50.0:
            level = "SUSPICIOUS"
        elif clamped >= 25.0:
            level = "MODERATE"
        else:
            level = "LOW"

        return clamped, level

    @staticmethod
    def recalculate_what_if(
        original_score: float,
        original_factors: List[Dict[str, Any]],
        toggled_signals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates what-if scenario outcome when specific risk factors are enabled or disabled.
        """
        score = original_score
        changed_factors = []

        for toggle in toggled_signals:
            sig_name = toggle.get("signal_name", "").lower()
            enabled = toggle.get("enabled", True)

            # Match against original factors
            for f in original_factors:
                if sig_name in f.get("name", "").lower() or sig_name in f.get("description", "").lower():
                    contribution = f.get("contribution", 0.0)
                    if not enabled and contribution > 0:
                        score -= contribution
                        changed_factors.append({
                            "factor": f.get("name"),
                            "action": "REMOVED",
                            "delta": -contribution
                        })
                    elif enabled and contribution < 0:
                        score += abs(contribution)
                        changed_factors.append({
                            "factor": f.get("name"),
                            "action": "RESTORED",
                            "delta": abs(contribution)
                        })

        new_score, new_level = RiskEngine.calculate_risk(base_points=score)
        
        return {
            "original_score": original_score,
            "scenario_score": new_score,
            "score_delta": round(new_score - original_score, 1),
            "scenario_level": new_level,
            "changed_factors": changed_factors,
            "explanation": f"Recalculated scenario risk score shifted from {original_score} to {new_score} ({new_level})."
        }
