"""Manage default values for .env keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _defaults_path(env_file: str) -> Path:
    base = Path(env_file).resolve().parent
    return base / ".envoy" / "defaults.json"


def load_defaults(env_file: str) -> Dict[str, str]:
    """Load stored defaults for the given env file."""
    path = _defaults_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_defaults(env_file: str, defaults: Dict[str, str]) -> None:
    """Persist defaults to disk."""
    path = _defaults_path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(defaults, indent=2))


def set_default(env_file: str, key: str, value: str) -> None:
    """Set or update a default value for a key."""
    defaults = load_defaults(env_file)
    defaults[key] = value
    save_defaults(env_file, defaults)


def remove_default(env_file: str, key: str) -> bool:
    """Remove a default. Returns True if the key existed."""
    defaults = load_defaults(env_file)
    if key not in defaults:
        return False
    del defaults[key]
    save_defaults(env_file, defaults)
    return True


def apply_defaults(
    env: Dict[str, str],
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new dict with defaults applied for missing (or all) keys."""
    result = dict(env)
    for key, value in defaults.items():
        if overwrite or key not in result or result[key] == "":
            result[key] = value
    return result


def missing_defaults(
    env: Dict[str, str], defaults: Dict[str, str]
) -> Dict[str, str]:
    """Return defaults whose keys are absent or empty in env."""
    return {
        k: v
        for k, v in defaults.items()
        if k not in env or env[k] == ""
    }
