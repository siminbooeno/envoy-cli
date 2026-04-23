"""Tag management for .env keys — assign, remove, and filter by tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


def _tags_path(env_file: Path) -> Path:
    return env_file.parent / ".envoy" / f"{env_file.name}.tags.json"


def load_tags(env_file: Path) -> Dict[str, List[str]]:
    """Load tag mapping {key: [tag, ...]} for the given env file."""
    path = _tags_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_tags(env_file: Path, tags: Dict[str, List[str]]) -> None:
    """Persist tag mapping to disk."""
    path = _tags_path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tags, indent=2))


def add_tag(env_file: Path, key: str, tag: str) -> Dict[str, List[str]]:
    """Add a tag to a key. Returns updated tag mapping."""
    tags = load_tags(env_file)
    existing: List[str] = tags.get(key, [])
    if tag not in existing:
        existing.append(tag)
    tags[key] = existing
    save_tags(env_file, tags)
    return tags


def remove_tag(env_file: Path, key: str, tag: str) -> Dict[str, List[str]]:
    """Remove a tag from a key. Returns updated tag mapping."""
    tags = load_tags(env_file)
    existing: List[str] = tags.get(key, [])
    tags[key] = [t for t in existing if t != tag]
    if not tags[key]:
        del tags[key]
    save_tags(env_file, tags)
    return tags


def get_tags(env_file: Path, key: str) -> List[str]:
    """Return all tags assigned to a key."""
    return load_tags(env_file).get(key, [])


def keys_with_tag(env_file: Path, tag: str) -> List[str]:
    """Return all keys that have the given tag."""
    tags = load_tags(env_file)
    return [k for k, tag_list in tags.items() if tag in tag_list]


def all_tags(env_file: Path) -> Set[str]:
    """Return the set of all unique tags used in the env file."""
    tags = load_tags(env_file)
    result: Set[str] = set()
    for tag_list in tags.values():
        result.update(tag_list)
    return result
