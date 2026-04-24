"""Extract a subset of keys from an env file into a new file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envoy.parser import load_env_file, serialize_env


@dataclass
class ExtractResult:
    extracted: Dict[str, str] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_extracted(self) -> int:
        return len(self.extracted)

    @property
    def total_missing(self) -> int:
        return len(self.missing)

    def __repr__(self) -> str:
        return (
            f"ExtractResult(extracted={self.total_extracted}, "
            f"missing={self.total_missing}, skipped={len(self.skipped)})"
        )


def extract_keys(
    env: Dict[str, str],
    keys: List[str],
    ignore_missing: bool = False,
) -> ExtractResult:
    """Extract specific keys from an env dict."""
    result = ExtractResult()
    for key in keys:
        if key in env:
            result.extracted[key] = env[key]
        else:
            if not ignore_missing:
                result.missing.append(key)
    return result


def extract_env_file(
    source: Path,
    keys: List[str],
    dest: Optional[Path] = None,
    overwrite: bool = False,
    ignore_missing: bool = False,
) -> ExtractResult:
    """Extract keys from source env file, optionally writing to dest."""
    env = load_env_file(source)
    result = extract_keys(env, keys, ignore_missing=ignore_missing)

    if result.missing:
        return result

    if dest is not None:
        if dest.exists() and not overwrite:
            existing = load_env_file(dest)
            for key in list(result.extracted.keys()):
                if key in existing:
                    result.skipped.append(key)
                    del result.extracted[key]

        if dest.exists() and not overwrite:
            existing = load_env_file(dest)
            merged = {**existing, **result.extracted}
            dest.write_text(serialize_env(merged))
        else:
            dest.write_text(serialize_env(result.extracted))

    return result
