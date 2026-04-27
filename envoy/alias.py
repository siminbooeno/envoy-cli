"""alias.py — Manage short aliases for .env file paths.

Allows users to register named aliases for frequently used env files,
so they can refer to them by name instead of full path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _aliases_path(env_dir: Optional[Path] = None) -> Path:
    """Return the path to the aliases store file."""
    base = env_dir or Path(".") / ".envoy"
    base.mkdir(parents=True, exist_ok=True)
    return base / "aliases.json"


def load_aliases(env_dir: Optional[Path] = None) -> dict[str, str]:
    """Load all registered aliases from disk.

    Returns an empty dict if no aliases file exists.
    """
    path = _aliases_path(env_dir)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_aliases(aliases: dict[str, str], env_dir: Optional[Path] = None) -> None:
    """Persist the aliases dict to disk."""
    path = _aliases_path(env_dir)
    with path.open("w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2)
        f.write("\n")


def add_alias(name: str, file_path: str, env_dir: Optional[Path] = None) -> None:
    """Register a new alias pointing to the given file path.

    Overwrites any existing alias with the same name.
    """
    aliases = load_aliases(env_dir)
    aliases[name] = str(file_path)
    save_aliases(aliases, env_dir)


def remove_alias(name: str, env_dir: Optional[Path] = None) -> bool:
    """Remove an alias by name.

    Returns True if the alias existed and was removed, False otherwise.
    """
    aliases = load_aliases(env_dir)
    if name not in aliases:
        return False
    del aliases[name]
    save_aliases(aliases, env_dir)
    return True


def get_alias(name: str, env_dir: Optional[Path] = None) -> Optional[str]:
    """Look up a file path by alias name.

    Returns None if the alias is not registered.
    """
    aliases = load_aliases(env_dir)
    return aliases.get(name)


def resolve_path(name_or_path: str, env_dir: Optional[Path] = None) -> str:
    """Resolve a value that may be either an alias name or a literal path.

    If the value matches a registered alias, returns the aliased path.
    Otherwise returns the original value unchanged.
    """
    resolved = get_alias(name_or_path, env_dir)
    return resolved if resolved is not None else name_or_path


def list_aliases(env_dir: Optional[Path] = None) -> list[tuple[str, str]]:
    """Return all aliases as a sorted list of (name, path) tuples."""
    aliases = load_aliases(env_dir)
    return sorted(aliases.items())
