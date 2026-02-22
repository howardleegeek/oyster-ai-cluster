"""
Utilities to validate and fix external API keys.
"""

from typing import Optional


def is_valid_api_key(key: Optional[str]) -> bool:
    """
    Basic validation for API keys. This is intentionally lightweight:
    - non-empty string
    - no whitespace
    - minimum length to catch obviously invalid keys
    """
    if not isinstance(key, str):
        return False
    k = key.strip()
    if not k:
        return False
    if any(c.isspace() for c in k):
        return False
    # A minimal length heuristic. Most API keys are longer than 6 chars.
    if len(k) < 6:
        return False
    return True


def fix_external_api_key(key: Optional[str]) -> str:
    """
    Normalize and fix an external API key.
    - If the key is valid, returns the trimmed key.
    - If the key is invalid, returns an empty string to signal missing/invalid key.
    This function is intentionally simple to avoid side effects.
    """
    if is_valid_api_key(key):
        return key.strip()
    return ""
