"""Sync .env files between environments."""
from pathlib import Path
from typing import Optional

from envoy.parser import load_env_file, serialize_env
from envoy.diff import compute_diff, has_changes, ChangeType


def sync_env(
    source_path: str,
    target_path: str,
    overwrite: bool = False,
    add_missing: bool = True,
    remove_extra: bool = False,
) -> dict:
    """Sync source env into target env.

    Returns a summary dict with counts of applied changes.
    """
    source = load_env_file(source_path)
    target_path_obj = Path(target_path)

    if target_path_obj.exists():
        target = load_env_file(target_path)
    else:
        target = {}

    diff = compute_diff(target, source)

    if not has_changes(diff):
        return {"added": 0, "updated": 0, "removed": 0, "skipped": 0}

    added = updated = removed = skipped = 0
    merged = dict(target)

    for entry in diff:
        if entry.change_type == ChangeType.ADDED and add_missing:
            merged[entry.key] = entry.new_value
            added += 1
        elif entry.change_type == ChangeType.MODIFIED:
            if overwrite:
                merged[entry.key] = entry.new_value
                updated += 1
            else:
                skipped += 1
        elif entry.change_type == ChangeType.REMOVED and remove_extra:
            merged.pop(entry.key, None)
            removed += 1
        else:
            skipped += 1

    target_path_obj.write_text(serialize_env(merged))

    return {"added": added, "updated": updated, "removed": removed, "skipped": skipped}


def merge_envs(base: dict, override: dict) -> dict:
    """Return a new dict merging override into base."""
    merged = dict(base)
    merged.update(override)
    return merged
