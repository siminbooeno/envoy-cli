"""Group-based key management: organize env keys into named groups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _groups_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.stem}.groups.json"


def load_groups(env_file: Path) -> Dict[str, List[str]]:
    """Load groups for a given env file. Returns empty dict if none exist."""
    path = _groups_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_groups(env_file: Path, groups: Dict[str, List[str]]) -> None:
    """Persist groups to disk."""
    path = _groups_path(env_file)
    path.write_text(json.dumps(groups, indent=2))


def add_to_group(env_file: Path, group: str, keys: List[str]) -> Dict[str, List[str]]:
    """Add keys to a named group, creating it if necessary."""
    groups = load_groups(env_file)
    existing = set(groups.get(group, []))
    existing.update(keys)
    groups[group] = sorted(existing)
    save_groups(env_file, groups)
    return groups


def remove_from_group(env_file: Path, group: str, keys: List[str]) -> Dict[str, List[str]]:
    """Remove keys from a named group."""
    groups = load_groups(env_file)
    if group not in groups:
        return groups
    remaining = [k for k in groups[group] if k not in keys]
    if remaining:
        groups[group] = remaining
    else:
        del groups[group]
    save_groups(env_file, groups)
    return groups


def delete_group(env_file: Path, group: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    groups = load_groups(env_file)
    if group not in groups:
        return False
    del groups[group]
    save_groups(env_file, groups)
    return True


def get_group_keys(env_file: Path, group: str) -> Optional[List[str]]:
    """Return keys in a group, or None if the group does not exist."""
    groups = load_groups(env_file)
    return groups.get(group)


def list_groups(env_file: Path) -> List[str]:
    """Return all group names for a given env file."""
    return list(load_groups(env_file).keys())


def rename_group(env_file: Path, old_name: str, new_name: str) -> bool:
    """Rename a group from old_name to new_name.

    Returns True if the rename succeeded, False if old_name does not exist.
    Raises ValueError if new_name already exists.
    """
    groups = load_groups(env_file)
    if old_name not in groups:
        return False
    if new_name in groups:
        raise ValueError(f"Group '{new_name}' already exists.")
    groups[new_name] = groups.pop(old_name)
    save_groups(env_file, groups)
    return True
