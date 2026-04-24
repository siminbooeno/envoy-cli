"""Search and filter env file keys/values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file


@dataclass
class SearchResult:
    key: str
    value: str
    matched_key: bool = False
    matched_value: bool = False


@dataclass
class SearchReport:
    pattern: str
    results: List[SearchResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    def keys(self) -> List[str]:
        return [r.key for r in self.results]


def search_env(
    env: Dict[str, str],
    pattern: str,
    *,
    search_keys: bool = True,
    search_values: bool = True,
    case_sensitive: bool = False,
    exact: bool = False,
) -> SearchReport:
    """Search an env dict for keys/values matching *pattern*."""
    flags = 0 if case_sensitive else re.IGNORECASE
    if exact:
        regex = re.compile(r"^" + re.escape(pattern) + r"$", flags)
    else:
        regex = re.compile(re.escape(pattern), flags)

    report = SearchReport(pattern=pattern)
    for key, value in env.items():
        matched_key = search_keys and bool(regex.search(key))
        matched_value = search_values and bool(regex.search(value))
        if matched_key or matched_value:
            report.results.append(
                SearchResult(
                    key=key,
                    value=value,
                    matched_key=matched_key,
                    matched_value=matched_value,
                )
            )
    return report


def search_env_file(
    path: str,
    pattern: str,
    **kwargs,
) -> SearchReport:
    """Load *path* and run :func:`search_env` with *kwargs*."""
    env = load_env_file(path)
    return search_env(env, pattern, **kwargs)
