"""Sanitize .env values by removing or replacing unsafe characters."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SanitizeResult:
    sanitized: Dict[str, str]
    changes: Dict[str, tuple]  # key -> (original, sanitized)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return len(self.changes)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    def __repr__(self) -> str:
        return (
            f"SanitizeResult(changed={self.total_changed}, "
            f"skipped={self.total_skipped})"
        )


_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_NEWLINE_RE = re.compile(r"[\r\n]+")


def sanitize_value(
    value: str,
    *,
    strip_whitespace: bool = True,
    remove_control_chars: bool = True,
    collapse_newlines: bool = True,
    newline_replacement: str = " ",
    max_length: Optional[int] = None,
) -> str:
    """Return a sanitized copy of *value*."""
    result = value
    if strip_whitespace:
        result = result.strip()
    if collapse_newlines:
        result = _NEWLINE_RE.sub(newline_replacement, result)
    if remove_control_chars:
        result = _CONTROL_RE.sub("", result)
    if max_length is not None:
        result = result[:max_length]
    return result


def sanitize_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    strip_whitespace: bool = True,
    remove_control_chars: bool = True,
    collapse_newlines: bool = True,
    newline_replacement: str = " ",
    max_length: Optional[int] = None,
) -> SanitizeResult:
    """Sanitize values in *env*, returning a SanitizeResult."""
    target_keys = set(keys) if keys else set(env.keys())
    sanitized: Dict[str, str] = dict(env)
    changes: Dict[str, tuple] = {}
    skipped: List[str] = []

    for k in target_keys:
        if k not in env:
            skipped.append(k)
            continue
        original = env[k]
        clean = sanitize_value(
            original,
            strip_whitespace=strip_whitespace,
            remove_control_chars=remove_control_chars,
            collapse_newlines=collapse_newlines,
            newline_replacement=newline_replacement,
            max_length=max_length,
        )
        if clean != original:
            sanitized[k] = clean
            changes[k] = (original, clean)

    return SanitizeResult(sanitized=sanitized, changes=changes, skipped=skipped)
