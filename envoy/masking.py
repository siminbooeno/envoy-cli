"""Secret masking utilities for sensitive .env values."""

import re
from typing import Dict, Set

DEFAULT_SECRET_PATTERNS = [
    re.compile(r'.*SECRET.*', re.IGNORECASE),
    re.compile(r'.*PASSWORD.*', re.IGNORECASE),
    re.compile(r'.*TOKEN.*', re.IGNORECASE),
    re.compile(r'.*API_KEY.*', re.IGNORECASE),
    re.compile(r'.*PRIVATE.*', re.IGNORECASE),
    re.compile(r'.*CREDENTIALS.*', re.IGNORECASE),
]

MASK_PLACEHOLDER = '********'


def is_secret(key: str, extra_patterns: list | None = None) -> bool:
    """Determine if a key is considered sensitive."""
    patterns = DEFAULT_SECRET_PATTERNS + (extra_patterns or [])
    return any(p.match(key) for p in patterns)


def mask_value(value: str, visible_chars: int = 0) -> str:
    """Mask a secret value, optionally showing the last N characters."""
    if visible_chars > 0 and len(value) > visible_chars:
        return MASK_PLACEHOLDER + value[-visible_chars:]
    return MASK_PLACEHOLDER


def mask_env(data: Dict[str, str], visible_chars: int = 0) -> Dict[str, str]:
    """Return a copy of the env dict with secret values masked."""
    result = {}
    for key, value in data.items():
        result[key] = mask_value(value, visible_chars) if is_secret(key) else value
    return result


def get_secret_keys(data: Dict[str, str]) -> Set[str]:
    """Return the set of keys identified as secrets."""
    return {key for key in data if is_secret(key)}
