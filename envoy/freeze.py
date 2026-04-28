"""Freeze and unfreeze env keys to prevent accidental modification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set


def _freeze_path(env_file: Path) -> Path:
    return env_file.parent / ".envoy" / f"{env_file.name}.frozen.json"


def load_frozen(env_file: Path) -> Set[str]:
    """Return the set of currently frozen keys for an env file."""
    path = _freeze_path(env_file)
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return set(data.get("frozen", []))


def save_frozen(env_file: Path, keys: Set[str]) -> None:
    """Persist the frozen key set to disk."""
    path = _freeze_path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"frozen": sorted(keys)}, indent=2))


def freeze_keys(env_file: Path, keys: List[str]) -> List[str]:
    """Add keys to the frozen set. Returns list of newly frozen keys."""
    current = load_frozen(env_file)
    added = [k for k in keys if k not in current]
    current.update(keys)
    save_frozen(env_file, current)
    return added


def unfreeze_keys(env_file: Path, keys: List[str]) -> List[str]:
    """Remove keys from the frozen set. Returns list of actually unfrozen keys."""
    current = load_frozen(env_file)
    removed = [k for k in keys if k in current]
    current.difference_update(keys)
    save_frozen(env_file, current)
    return removed


def is_frozen(env_file: Path, key: str) -> bool:
    """Return True if the given key is frozen."""
    return key in load_frozen(env_file)


def check_frozen(env_file: Path, proposed: Dict[str, str]) -> List[str]:
    """Return keys in proposed that are frozen (i.e. would be blocked)."""
    frozen = load_frozen(env_file)
    return [k for k in proposed if k in frozen]
