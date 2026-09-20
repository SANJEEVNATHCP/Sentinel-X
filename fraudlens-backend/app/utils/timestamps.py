"""
FraudLens AI - Timestamp Utilities
Generates uniform ISO 8601 UTC timestamps.
"""

from datetime import datetime, timezone

def utc_now() -> datetime:
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)

def utc_now_iso() -> str:
    """Returns the current UTC timestamp formatted as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
