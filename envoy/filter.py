"""Filter env variables by key patterns, prefixes, or value conditions."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    @property
    def total_matched(self) -> int:
        return len(self.matched)

    @property
    def total_excluded(self) -> int:
        return len(self.excluded)


def filter_by_prefix(env: Dict[str, str], prefix: str) -> FilterResult:
    """Keep only keys starting with the given prefix."""
    result = FilterResult()
    for k, v in env.items():
        if k.startswith(prefix):
            result.matched[k] = v
        else:
            result.excluded[k] = v
    return result


def filter_by_pattern(env: Dict[str, str], pattern: str) -> FilterResult:
    """Keep only keys matching a regex pattern."""
    compiled = re.compile(pattern)
    result = FilterResult()
    for k, v in env.items():
        if compiled.search(k):
            result.matched[k] = v
        else:
            result.excluded[k] = v
    return result


def filter_by_value(env: Dict[str, str], value_pattern: str) -> FilterResult:
    """Keep only entries whose value matches a regex pattern."""
    compiled = re.compile(value_pattern)
    result = FilterResult()
    for k, v in env.items():
        if compiled.search(v):
            result.matched[k] = v
        else:
            result.excluded[k] = v
    return result


def filter_empty(env: Dict[str, str]) -> FilterResult:
    """Keep only entries with non-empty values."""
    result = FilterResult()
    for k, v in env.items():
        if v.strip():
            result.matched[k] = v
        else:
            result.excluded[k] = v
    return result


def filter_env(
    env: Dict[str, str],
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    exclude_empty: bool = False,
) -> FilterResult:
    """Apply one or more filters to an env dict, returning a FilterResult."""
    current = dict(env)
    excluded: Dict[str, str] = {}

    def _apply(result: FilterResult) -> None:
        excluded.update(result.excluded)
        return result.matched

    if prefix is not None:
        current = _apply(filter_by_prefix(current, prefix))
    if pattern is not None:
        current = _apply(filter_by_pattern(current, pattern))
    if value_pattern is not None:
        current = _apply(filter_by_value(current, value_pattern))
    if exclude_empty:
        current = _apply(filter_empty(current))

    return FilterResult(matched=current, excluded=excluded)
