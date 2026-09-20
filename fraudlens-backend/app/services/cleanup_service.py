"""
FraudLens AI - Temporary File Cleanup Service
Purges expired scratch files and temp uploads.
"""

import os
import time
from app.config import settings
from app.logging_config import logger

class CleanupService:
    @staticmethod
    def cleanup_old_temp_files(max_age_hours: int = 24) -> int:
        """Removes orphaned temp uploads older than max_age_hours."""
        cleaned = 0
        now = time.time()
        max_age_sec = max_age_hours * 3600

        if not os.path.exists(settings.TEMP_UPLOAD_DIR):
            return 0

        for f in os.listdir(settings.TEMP_UPLOAD_DIR):
            full_path = os.path.join(settings.TEMP_UPLOAD_DIR, f)
            try:
                if os.path.isfile(full_path):
                    if now - os.path.getmtime(full_path) > max_age_sec:
                        os.remove(full_path)
                        cleaned += 1
            except Exception as e:
                logger.warning(f"Failed to remove stale file {f}: {str(e)}")

        return cleaned
