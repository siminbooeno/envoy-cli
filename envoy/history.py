"""Track and display change history for .env files."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from envoy.diff import compute_diff, has_changes
from envoy.parser import load_env_file


def _history_dir(env_path: str) -> Path:
    base = Path(env_path).resolve().parent
    return base / ".envoy" / "history"


def _history_file(env_path: str) -> Path:
    name = Path(env_path).name
    return _history_dir(env_path) / f"{name}.history.jsonl"


def record_snapshot(env_path: str, label: Optional[str] = None) -> dict:
    """Record the current state of an env file into history."""
    env_data = load_env_file(env_path)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "label": label or "",
        "data": env_data,
    }
    hist_file = _history_file(env_path)
    hist_file.parent.mkdir(parents=True, exist_ok=True)
    with hist_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def load_history(env_path: str) -> List[dict]:
    """Return all recorded history entries for an env file."""
    hist_file = _history_file(env_path)
    if not hist_file.exists():
        return []
    entries = []
    with hist_file.open() as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def diff_history(env_path: str, index_a: int, index_b: int) -> list:
    """Compute diff between two history entries by index."""
    entries = load_history(env_path)
    if index_a >= len(entries) or index_b >= len(entries):
        raise IndexError("History index out of range")
    env_a = entries[index_a]["data"]
    env_b = entries[index_b]["data"]
    return compute_diff(env_a, env_b)


def clear_history(env_path: str) -> None:
    """Delete all history for an env file."""
    hist_file = _history_file(env_path)
    if hist_file.exists():
        hist_file.unlink()
