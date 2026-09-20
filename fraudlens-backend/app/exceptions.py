"""
FraudLens AI - Custom Domain Exceptions
Provides consistent error codes and messages without exposing stack traces.
"""

from fastapi import HTTPException, status

class FraudLensException(Exception):
    """Base exception for FraudLens domain errors."""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class AuthenticationError(FraudLensException):
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message=message, error_code="AUTHENTICATION_FAILED", status_code=status.HTTP_401_UNAUTHORIZED)

class NotFoundError(FraudLensException):
    def __init__(self, message: str = "Requested resource was not found"):
        super().__init__(message=message, error_code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

class ValidationError(FraudLensException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, error_code="VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)

class SSRFSecurityError(FraudLensException):
    def __init__(self, message: str = "Requested URL target is restricted for security reasons"):
        super().__init__(message=message, error_code="SECURITY_RESTRICTION", status_code=status.HTTP_400_BAD_REQUEST)

class FileProcessingError(FraudLensException):
    def __init__(self, message: str = "File could not be parsed or processed"):
        super().__init__(message=message, error_code="FILE_PROCESSING_ERROR", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class ServiceUnavailableError(FraudLensException):
    def __init__(self, message: str = "External verification service is currently unavailable"):
        super().__init__(message=message, error_code="SERVICE_UNAVAILABLE", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
