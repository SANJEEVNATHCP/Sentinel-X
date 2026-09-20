"""
FraudLens AI - PDF Processing Service
Extracts text safely from employment documents and offer letters using PyMuPDF.
"""

from typing import Optional
from app.exceptions import FileProcessingError

class PDFService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extracts text content from a PDF document."""
        try:
            import fitz # PyMuPDF
            doc = fitz.open(file_path)
            full_text = []
            for page in doc:
                full_text.append(page.get_text())
            doc.close()
            return "\n".join(full_text)
        except Exception as e:
            # Fallback reading
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                raise FileProcessingError(f"Could not extract text from document: {str(e)}")
