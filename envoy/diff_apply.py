"""Apply a diff (patch) from one env file onto another."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.diff import ChangeType, EnvDiff, compute_diff
from envoy.parser import load_env_file, serialize_env


@dataclass
class ApplyResult:
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def total_applied(self) -> int:
        return len(self.applied)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def __repr__(self) -> str:
        return (
            f"ApplyResult(applied={self.total_applied}, "
            f"skipped={self.total_skipped}, "
            f"removed={len(self.removed)}, "
            f"conflicts={len(self.conflicts)})"
        )


def apply_diff(
    base: Dict[str, str],
    diff: EnvDiff,
    *,
    overwrite: bool = False,
    remove_deleted: bool = True,
) -> tuple[Dict[str, str], ApplyResult]:
    """Apply an EnvDiff to a base env dict, returning the updated dict and a result."""
    result = ApplyResult()
    updated = dict(base)

    for entry in diff.changes:
        key = entry.key

        if entry.change_type == ChangeType.ADDED:
            if key in updated and not overwrite:
                result.skipped.append(key)
            elif key in updated and updated[key] != entry.new_value:
                result.conflicts.append(key)
                if overwrite:
                    updated[key] = entry.new_value
                    result.applied.append(key)
            else:
                updated[key] = entry.new_value
                result.applied.append(key)

        elif entry.change_type == ChangeType.REMOVED:
            if remove_deleted and key in updated:
                del updated[key]
                result.removed.append(key)
            else:
                result.skipped.append(key)

        elif entry.change_type == ChangeType.CHANGED:
            if key not in updated:
                updated[key] = entry.new_value
                result.applied.append(key)
            elif overwrite:
                updated[key] = entry.new_value
                result.applied.append(key)
            else:
                result.conflicts.append(key)

    return updated, result


def apply_diff_files(
    base_path: str,
    source_path: str,
    reference_path: str,
    output_path: Optional[str] = None,
    *,
    overwrite: bool = False,
    remove_deleted: bool = True,
) -> ApplyResult:
    """Compute diff between source and reference, then apply it to base."""
    base = load_env_file(base_path)
    source = load_env_file(source_path)
    reference = load_env_file(reference_path)

    diff = compute_diff(source, reference)
    updated, result = apply_diff(
        base, diff, overwrite=overwrite, remove_deleted=remove_deleted
    )

    dest = output_path or base_path
    with open(dest, "w") as fh:
        fh.write(serialize_env(updated))

    return result
