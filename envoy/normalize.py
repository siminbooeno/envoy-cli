"""Normalize .env file keys and values to a consistent format."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envoy.parser import load_env_file, serialize_env


@dataclass
class NormalizeResult:
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return len(self.changed)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    def __repr__(self) -> str:
        return f"NormalizeResult(changed={self.total_changed}, skipped={self.total_skipped})"


def normalize_key(key: str) -> str:
    """Normalize a key to uppercase with underscores."""
    return key.strip().upper().replace("-", "_").replace(" ", "_")


def normalize_value(value: str, *, strip: bool = True, lowercase: bool = False) -> str:
    """Normalize a value by stripping whitespace and optionally lowercasing."""
    result = value.strip() if strip else value
    if lowercase:
        result = result.lower()
    return result


def normalize_env(
    env: Dict[str, str],
    *,
    keys: bool = True,
    values: bool = True,
    lowercase_values: bool = False,
    only: Optional[List[str]] = None,
) -> Tuple[Dict[str, str], NormalizeResult]:
    """Normalize keys and/or values in an env dict."""
    result = NormalizeResult()
    normalized: Dict[str, str] = {}

    for key, value in env.items():
        if only and key not in only:
            normalized[key] = value
            result.skipped.append(key)
            continue

        new_key = normalize_key(key) if keys else key
        new_value = normalize_value(value, lowercase=lowercase_values) if values else value

        if new_key != key or new_value != value:
            result.changed.append((key, value, new_value))

        normalized[new_key] = new_value

    return normalized, result


def normalize_env_file(
    path: str,
    *,
    keys: bool = True,
    values: bool = True,
    lowercase_values: bool = False,
    only: Optional[List[str]] = None,
    dry_run: bool = False,
) -> NormalizeResult:
    """Normalize a .env file in place."""
    env = load_env_file(path)
    normalized, result = normalize_env(
        env, keys=keys, values=values, lowercase_values=lowercase_values, only=only
    )
    if not dry_run:
        serialize_env(normalized, path)
    return result
