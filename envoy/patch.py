"""Patch module: apply a set of key-value updates to an env file."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file, serialize_env


@dataclass
class PatchResult:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PatchResult(added={self.added}, updated={self.updated}, "
            f"skipped={self.skipped}, removed={self.removed})"
        )


def patch_env(
    env: Dict[str, str],
    updates: Dict[str, Optional[str]],
    *,
    overwrite: bool = True,
    remove_nulls: bool = True,
) -> tuple[Dict[str, str], PatchResult]:
    """Apply *updates* to *env* dict and return a new dict plus a PatchResult.

    If a value in *updates* is None and *remove_nulls* is True the key is
    deleted from the result.  Pass ``overwrite=False`` to keep existing values.
    """
    result = dict(env)
    report = PatchResult()

    for key, value in updates.items():
        if value is None and remove_nulls:
            if key in result:
                del result[key]
                report.removed.append(key)
            else:
                report.skipped.append(key)
        elif key not in result:
            result[key] = value  # type: ignore[assignment]
            report.added.append(key)
        elif overwrite:
            result[key] = value  # type: ignore[assignment]
            report.updated.append(key)
        else:
            report.skipped.append(key)

    return result, report


def patch_env_file(
    path: str,
    updates: Dict[str, Optional[str]],
    *,
    overwrite: bool = True,
    remove_nulls: bool = True,
    dry_run: bool = False,
) -> PatchResult:
    """Load *path*, apply *updates*, write back unless *dry_run* is True."""
    env = load_env_file(path)
    patched, report = patch_env(
        env, updates, overwrite=overwrite, remove_nulls=remove_nulls
    )
    if not dry_run:
        with open(path, "w") as fh:
            fh.write(serialize_env(patched))
    return report
