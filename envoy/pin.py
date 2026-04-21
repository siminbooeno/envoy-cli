"""Pin module: lock specific env keys to exact values and validate against them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


PIN_FILENAME = ".env.pins"


def _pins_path(directory: str = ".") -> Path:
    return Path(directory) / PIN_FILENAME


def load_pins(directory: str = ".") -> Dict[str, str]:
    """Load pinned key-value pairs from the pins file."""
    path = _pins_path(directory)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_pins(pins: Dict[str, str], directory: str = ".") -> None:
    """Persist pinned key-value pairs to the pins file."""
    path = _pins_path(directory)
    path.write_text(json.dumps(pins, indent=2, sort_keys=True), encoding="utf-8")


def add_pin(key: str, value: str, directory: str = ".") -> Dict[str, str]:
    """Add or update a pin for a single key."""
    pins = load_pins(directory)
    pins[key] = value
    save_pins(pins, directory)
    return pins


def remove_pin(key: str, directory: str = ".") -> bool:
    """Remove a pin. Returns True if the key existed, False otherwise."""
    pins = load_pins(directory)
    if key not in pins:
        return False
    del pins[key]
    save_pins(pins, directory)
    return True


def check_pins(env: Dict[str, str], directory: str = ".") -> List[str]:
    """Return a list of violation messages for keys that don't match their pinned values."""
    pins = load_pins(directory)
    violations: List[str] = []
    for key, expected in pins.items():
        if key not in env:
            violations.append(f"{key}: pinned to '{expected}' but key is missing")
        elif env[key] != expected:
            violations.append(f"{key}: expected '{expected}', got '{env[key]}'")
    return violations


def list_pins(directory: str = ".") -> Dict[str, str]:
    """Return all currently pinned key-value pairs."""
    return load_pins(directory)
