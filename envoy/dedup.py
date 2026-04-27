"""Deduplication of .env file keys — detect and remove duplicate keys, keeping first or last occurrence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envoy.parser import parse_env_file, serialize_env


@dataclass
class DedupResult:
    kept: Dict[str, str]
    duplicates: Dict[str, List[str]]  # key -> list of duplicate values removed
    total_removed: int = 0

    def __repr__(self) -> str:
        return (
            f"DedupResult(kept={len(self.kept)} keys, "
            f"duplicates={len(self.duplicates)}, removed={self.total_removed})"
        )


def find_duplicates(pairs: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Return a mapping of keys that appear more than once to all their values."""
    seen: Dict[str, List[str]] = {}
    for key, value in pairs:
        seen.setdefault(key, []).append(value)
    return {k: v for k, v in seen.items() if len(v) > 1}


def dedup_env(
    pairs: List[Tuple[str, str]],
    keep: str = "last",
) -> DedupResult:
    """Remove duplicate keys from a list of (key, value) pairs.

    Args:
        pairs: Ordered list of key-value pairs (may contain duplicate keys).
        keep: 'first' to keep the first occurrence, 'last' to keep the last.

    Returns:
        DedupResult with the deduplicated env and info about what was removed.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    duplicates = find_duplicates(pairs)
    seen: Dict[str, str] = {}
    removed_values: Dict[str, List[str]] = {k: [] for k in duplicates}

    if keep == "first":
        for key, value in pairs:
            if key in seen:
                removed_values.setdefault(key, []).append(value)
            else:
                seen[key] = value
    else:  # last
        for key, value in pairs:
            if key in seen and key in duplicates:
                removed_values.setdefault(key, []).append(seen[key])
            seen[key] = value

    total_removed = sum(len(v) for v in removed_values.values())
    return DedupResult(kept=seen, duplicates=removed_values, total_removed=total_removed)


def dedup_env_file(
    path: str,
    keep: str = "last",
    dry_run: bool = False,
    output: Optional[str] = None,
) -> DedupResult:
    """Deduplicate keys in an .env file, optionally writing the result."""
    pairs = parse_env_file(path)
    result = dedup_env(pairs, keep=keep)

    if not dry_run:
        dest = output or path
        content = serialize_env(result.kept)
        with open(dest, "w") as fh:
            fh.write(content)

    return result
