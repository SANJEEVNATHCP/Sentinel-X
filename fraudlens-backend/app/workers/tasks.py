"""
FraudLens AI - Asynchronous Celery Tasks
Handles background report generation, scheduled data purging, and large batch processing.
"""

from app.workers.celery_app import celery_app
from app.services.cleanup_service import CleanupService
from app.services.report_service import ReportService
from app.logging_config import logger

@celery_app.task(name="tasks.cleanup_expired_files")
def task_cleanup_expired_files():
    """Periodic worker task to clean stale files."""
    cleaned = CleanupService.cleanup_old_temp_files(max_age_hours=24)
    logger.info(f"Celery cleanup task completed. Purged {cleaned} stale files.")
    return {"cleaned_files": cleaned}

@celery_app.task(name="tasks.generate_report_async")
def task_generate_report_async(result_data: dict):
    """Background PDF report compilation."""
    pdf_path = ReportService.generate_pdf_report(result_data)
    logger.info(f"Asynchronous PDF report compiled at {pdf_path}")
    return {"pdf_path": pdf_path}
