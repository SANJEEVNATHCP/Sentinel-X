"""
FraudLens AI - Dashboard Intelligence Service
Computes real, non-fabricated metrics for user investigations and recent risk activity.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.investigation import Investigation

class DashboardService:
    @staticmethod
    def get_user_dashboard(db: Session, user_id: str) -> Dict[str, Any]:
        """Calculates authentic metrics and recent investigations for the current user."""
        all_invs = db.query(Investigation).filter(Investigation.user_id == user_id).order_by(Investigation.created_at.desc()).all()

        total = len(all_invs)
        high_risk = sum(1 for i in all_invs if i.risk_level in ["HIGH_RISK", "LIKELY_SCAM"])
        scam_count = sum(1 for i in all_invs if i.type in ["SCAM_URL", "IMAGE_CHAT", "OFFER_LETTER"])
        upi_count = sum(1 for i in all_invs if i.type == "UPI")

        recent = []
        for i in all_invs[:5]:
            recent.append({
                "id": i.id,
                "type": i.type,
                "target_entity": i.target_entity or i.type,
                "status": i.status,
                "risk_score": i.risk_score,
                "risk_level": i.risk_level,
                "summary": i.summary,
                "created_at": i.created_at.isoformat() + "Z"
            })

        # Calculate weekly risk activity aggregates
        risk_activity = []
        if total > 0:
            for i in all_invs[:7]:
                risk_activity.append({
                    "date": i.created_at.strftime("%Y-%m-%d"),
                    "score": i.risk_score,
                    "level": i.risk_level
                })

        return {
            "total_investigations": total,
            "high_risk_detections": high_risk,
            "scam_investigations": scam_count,
            "upi_analyses": upi_count,
            "recent_investigations": recent,
            "risk_activity": risk_activity
        }
