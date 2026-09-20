"""
FraudLens AI - Validation Utilities
Validates registration parameters, email syntax, and password complexity.
"""

import re
from app.exceptions import ValidationError

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email_format(email: str) -> str:
    if not email or not isinstance(email, str):
        raise ValidationError("Email address is required")
    cleaned = email.strip().lower()
    if not EMAIL_REGEX.match(cleaned):
        raise ValidationError("Invalid email address format")
    return cleaned

def validate_password_strength(password: str) -> None:
    if not password or len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one number")
