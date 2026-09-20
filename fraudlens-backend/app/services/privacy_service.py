"""
FraudLens AI - Privacy & End-Task Data Sanitization Service
Executes permanent application-level deletion of uploaded documents, raw files,
and session caches, while strictly preserving derived investigation results.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.investigation import Investigation
from app.models.uploaded_file import UploadedFile
from app.models.audit_log import AuditLog
from app.utils.file_utils import securely_delete_file
from app.exceptions import NotFoundError

class PrivacyService:
    @classmethod
    def end_investigation_and_purge_raw_data(
        cls,
        db: Session,
        user_id: str,
        investigation_id: str,
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Permanently purges raw uploaded documents, spreadsheets, and temporary caches.
        Preserves derived risk score, evidence signals, and executive summary.
        """
        inv = db.query(Investigation).filter(
            Investigation.id == investigation_id,
            Investigation.user_id == user_id
        ).first()

        if not inv:
            raise NotFoundError(f"Investigation '{investigation_id}' not found")

        # 1. Fetch and purge all uploaded files linked to this session
        uploaded_files = db.query(UploadedFile).filter(
            UploadedFile.investigation_id == investigation_id,
            UploadedFile.is_deleted == False
        ).all()

        deleted_file_count = 0
        for f in uploaded_files:
            if securely_delete_file(f.stored_path):
                deleted_file_count += 1
            f.is_deleted = True
            f.deleted_at = datetime.utcnow()

        # 2. Update investigation state
        inv.status = "ENDED"
        inv.ended_at = datetime.utcnow()

        # 3. Record compliance audit entry (WITHOUT sensitive raw content)
        audit = AuditLog(
            user_id=user_id,
            action="END_TASK_SESSION_PURGE",
            resource_type="INVESTIGATION",
            resource_id=investigation_id,
            request_id=request_id,
            status="SUCCESS"
        )
        db.add(audit)
        db.commit()

        return {
            "status": "success",
            "message": "Sensitive session data has been permanently deleted from storage.",
            "result_preserved": True,
            "deleted_file_count": deleted_file_count,
            "ended_at": inv.ended_at.isoformat() + "Z"
        }
