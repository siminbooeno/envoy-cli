"""Alias management for env keys — create, remove, and resolve key aliases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _aliases_path(env_file: Path) -> Path:
    return env_file.parent / ".envoy" / f"{env_file.stem}.aliases.json"


def load_aliases(env_file: Path) -> Dict[str, str]:
    """Load aliases for the given env file. Returns {alias: original_key}."""
    path = _aliases_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_aliases(env_file: Path, aliases: Dict[str, str]) -> None:
    path = _aliases_path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2))


def add_alias(env_file: Path, alias: str, original: str) -> None:
    """Register an alias pointing to an original key."""
    aliases = load_aliases(env_file)
    aliases[alias] = original
    save_aliases(env_file, aliases)


def remove_alias(env_file: Path, alias: str) -> bool:
    """Remove an alias. Returns True if it existed."""
    aliases = load_aliases(env_file)
    if alias not in aliases:
        return False
    del aliases[alias]
    save_aliases(env_file, aliases)
    return True


def resolve_alias(env_file: Path, alias: str) -> Optional[str]:
    """Return the original key for an alias, or None if not found."""
    return load_aliases(env_file).get(alias)


def list_aliases(env_file: Path) -> List[Dict[str, str]]:
    """Return all aliases as a list of {alias, original} dicts."""
    return [
        {"alias": k, "original": v}
        for k, v in load_aliases(env_file).items()
    ]


def apply_aliases(env: Dict[str, str], aliases: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of env with aliased keys added (alias -> original value)."""
    result = dict(env)
    for alias, original in aliases.items():
        if original in env:
            result[alias] = env[original]
    return result
