"""
FraudLens AI - Company & String Normalization Utilities
Strips legal designations and corporate suffixes to enable fuzzy matching.
"""

import re

LEGAL_SUFFIXES = [
    r"\bindia\s+private\s+limited\b",
    r"\bindia\s+pvt\s+ltd\b",
    r"\bprivate\s+limited\b",
    r"\bpvt\s+ltd\b",
    r"\bsoftware\s+pvt\s+ltd\b",
    r"\btechnologies\s+private\s+limited\b",
    r"\blimited\b",
    r"\bltd\b",
    r"\bllp\b",
    r"\binc\b",
    r"\bincorporated\b",
    r"\bcorp\b",
    r"\bcorporation\b",
    r"\bplc\b",
    r"\bgmbh\b",
    r"\bindia\b",
    r"\btechnologies\b",
    r"\btechnology\b",
    r"\bsolutions\b",
    r"\bsystems\b"
]

def normalize_company_name(name: str) -> str:
    """
    Normalizes a corporate name by removing legal identifiers, punctuation,
    and trailing designations (e.g., 'Infosys Limited' -> 'infosys').
    """
    if not name or not isinstance(name, str):
        return ""

    cleaned = name.strip().lower()
    
    # Remove punctuation
    cleaned = re.sub(r"[\.,\(\)\-\&]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Iteratively remove legal suffixes
    for suffix in LEGAL_SUFFIXES:
        cleaned = re.sub(suffix, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
