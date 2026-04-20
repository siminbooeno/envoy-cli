"""Profile management: named sets of env overrides per environment (dev, staging, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_PROFILES_FILENAME = ".envoy_profiles.json"


def _profiles_path(directory: str = ".") -> Path:
    return Path(directory) / _PROFILES_FILENAME


def load_profiles(directory: str = ".") -> Dict[str, Dict[str, str]]:
    """Load all profiles from the profiles file. Returns empty dict if not found."""
    path = _profiles_path(directory)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(profiles: Dict[str, Dict[str, str]], directory: str = ".") -> None:
    """Persist all profiles to disk."""
    path = _profiles_path(directory)
    with path.open("w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
        f.write("\n")


def set_profile(name: str, values: Dict[str, str], directory: str = ".") -> None:
    """Create or overwrite a named profile."""
    profiles = load_profiles(directory)
    profiles[name] = values
    save_profiles(profiles, directory)


def get_profile(name: str, directory: str = ".") -> Optional[Dict[str, str]]:
    """Return the key/value mapping for a profile, or None if it doesn't exist."""
    return load_profiles(directory).get(name)


def delete_profile(name: str, directory: str = ".") -> bool:
    """Delete a profile. Returns True if it existed, False otherwise."""
    profiles = load_profiles(directory)
    if name not in profiles:
        return False
    del profiles[name]
    save_profiles(profiles, directory)
    return True


def list_profiles(directory: str = ".") -> List[str]:
    """Return sorted list of profile names."""
    return sorted(load_profiles(directory).keys())


def apply_profile(base: Dict[str, str], name: str, directory: str = ".") -> Dict[str, str]:
    """Merge a named profile on top of *base*, returning a new dict."""
    profile = get_profile(name, directory)
    if profile is None:
        raise KeyError(f"Profile '{name}' not found.")
    merged = dict(base)
    merged.update(profile)
    return merged
