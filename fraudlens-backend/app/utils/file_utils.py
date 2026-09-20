"""
FraudLens AI - File Utilities
Handles secure upload storage, UUID filename generation, and privacy deletion.
"""

import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile
from app.config import settings
from app.exceptions import FileProcessingError

def save_upload_file_temporarily(upload_file: UploadFile) -> str:
    """
    Saves an uploaded file with a randomized UUID filename inside the temp directory.
    Validates file extension and size.
    """
    filename = upload_file.filename or "upload.bin"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise FileProcessingError(f"Unsupported file format '.{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}")

    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    destination_path = os.path.join(settings.TEMP_UPLOAD_DIR, unique_filename)

    try:
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise FileProcessingError(f"Could not persist upload: {str(e)}")

    file_size_mb = os.path.getsize(destination_path) / (1024 * 1024)
    if file_size_mb > settings.UPLOAD_MAX_SIZE_MB:
        os.remove(destination_path)
        raise FileProcessingError(f"File exceeds maximum allowed size of {settings.UPLOAD_MAX_SIZE_MB}MB")

    return destination_path

def securely_delete_file(file_path: Optional[str]) -> bool:
    """Securely deletes a file from disk if it exists."""
    if not file_path:
        return False
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False
