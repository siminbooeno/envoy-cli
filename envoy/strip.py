"""Strip keys from an env dict or file based on patterns or explicit key lists."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file, serialize_env


@dataclass
class StripResult:
    stripped: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed_keys)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped_keys)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StripResult(removed={self.total_removed}, "
            f"skipped={self.total_skipped})"
        )


def strip_keys(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
) -> StripResult:
    """Return a new env dict with specified keys removed.

    At least one of keys, pattern, or prefix must be provided.
    """
    if not keys and not pattern and not prefix:
        raise ValueError("At least one of keys, pattern, or prefix must be specified.")

    compiled = re.compile(pattern) if pattern else None
    keys_set = set(keys or [])

    removed: List[str] = []
    skipped: List[str] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        should_remove = (
            k in keys_set
            or (compiled is not None and compiled.search(k))
            or (prefix is not None and k.startswith(prefix))
        )
        if should_remove:
            removed.append(k)
        else:
            result[k] = v

    # Track explicitly requested keys that were not present
    for k in keys_set:
        if k not in env:
            skipped.append(k)

    return StripResult(stripped=result, removed_keys=removed, skipped_keys=skipped)


def strip_env_file(
    source: str,
    dest: Optional[str] = None,
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
) -> StripResult:
    """Load an env file, strip keys, and optionally write to dest."""
    env = load_env_file(source)
    result = strip_keys(env, keys=keys, pattern=pattern, prefix=prefix)
    if dest:
        content = serialize_env(result.stripped)
        with open(dest, "w") as fh:
            fh.write(content)
    return result
