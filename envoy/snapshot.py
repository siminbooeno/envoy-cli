"""Snapshot support: save and restore .env file states for rollback."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from envoy.parser import parse_env_file, serialize_env

DEFAULT_SNAPSHOT_DIR = ".envoy_snapshots"


def _snapshot_dir(base_dir: str = ".") -> Path:
    return Path(base_dir) / DEFAULT_SNAPSHOT_DIR


def create_snapshot(env_path: str, label: Optional[str] = None, base_dir: str = ".") -> str:
    """Save a snapshot of the given .env file. Returns the snapshot filename."""
    snap_dir = _snapshot_dir(base_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    env_data = parse_env_file(env_path)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    env_name = Path(env_path).name.replace(".", "_")
    label_part = f"_{label}" if label else ""
    filename = f"{env_name}{label_part}_{timestamp}.json"

    snapshot = {
        "source": str(env_path),
        "timestamp": timestamp,
        "label": label,
        "data": env_data,
    }

    snap_path = snap_dir / filename
    snap_path.write_text(json.dumps(snapshot, indent=2))
    return str(snap_path)


def list_snapshots(env_path: str, base_dir: str = ".") -> list[dict]:
    """List all snapshots for a given .env file, newest first."""
    snap_dir = _snapshot_dir(base_dir)
    if not snap_dir.exists():
        return []

    env_name = Path(env_path).name.replace(".", "_")
    snapshots = []
    for f in sorted(snap_dir.glob(f"{env_name}_*.json"), reverse=True):
        meta = json.loads(f.read_text())
        snapshots.append({"file": str(f), "timestamp": meta["timestamp"], "label": meta.get("label")})
    return snapshots


def restore_snapshot(snapshot_path: str, target_path: Optional[str] = None) -> str:
    """Restore a .env file from a snapshot. Returns the path written to."""
    snapshot = json.loads(Path(snapshot_path).read_text())
    out_path = target_path or snapshot["source"]
    content = serialize_env(snapshot["data"])
    Path(out_path).write_text(content)
    return out_path


def delete_snapshot(snapshot_path: str) -> None:
    """Delete a snapshot file."""
    path = Path(snapshot_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")
    path.unlink()
