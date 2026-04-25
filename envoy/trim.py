"""Trim whitespace and normalize values in .env files."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file, serialize_env


@dataclass
class TrimResult:
    trimmed: Dict[str, str] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)
    original: Dict[str, str] = field(default_factory=dict)

    @property
    def total_trimmed(self) -> int:
        return len(self.trimmed)

    @property
    def total_unchanged(self) -> int:
        return len(self.unchanged)

    def __repr__(self) -> str:
        return (
            f"TrimResult(trimmed={self.total_trimmed}, "
            f"unchanged={self.total_unchanged})"
        )


def trim_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    strip_quotes: bool = False,
) -> TrimResult:
    """Trim leading/trailing whitespace from values in an env dict.

    Args:
        env: The source env dictionary.
        keys: If provided, only trim these specific keys.
        strip_quotes: If True, also strip surrounding quote characters.

    Returns:
        A TrimResult describing what changed.
    """
    result = TrimResult(original=dict(env))
    target_keys = keys if keys is not None else list(env.keys())

    for k, v in env.items():
        if k not in target_keys:
            result.unchanged[k] = v
            continue

        new_v = v.strip()
        if strip_quotes and len(new_v) >= 2:
            if (new_v.startswith('"') and new_v.endswith('"')) or (
                new_v.startswith("'") and new_v.endswith("'")
            ):
                new_v = new_v[1:-1]

        if new_v != v:
            result.trimmed[k] = new_v
        else:
            result.unchanged[k] = v

    return result


def trim_env_file(
    path: str,
    keys: Optional[List[str]] = None,
    strip_quotes: bool = False,
    dry_run: bool = False,
) -> TrimResult:
    """Trim values in an .env file in place."""
    env = load_env_file(path)
    result = trim_env(env, keys=keys, strip_quotes=strip_quotes)

    if not dry_run and result.total_trimmed > 0:
        merged = {**env, **result.trimmed}
        # preserve original key order
        ordered = {k: merged[k] for k in env}
        serialize_env(ordered, path)

    return result
