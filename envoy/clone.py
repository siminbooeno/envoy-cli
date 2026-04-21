"""Clone an env file to a new location with optional key filtering and masking."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envoy.parser import load_env_file, serialize_env
from envoy.masking import mask_env


class CloneResult:
    def __init__(self, source: str, destination: str, keys_copied: list[str], keys_skipped: list[str]):
        self.source = source
        self.destination = destination
        self.keys_copied = keys_copied
        self.keys_skipped = keys_skipped

    @property
    def total_copied(self) -> int:
        return len(self.keys_copied)

    @property
    def total_skipped(self) -> int:
        return len(self.keys_skipped)


def clone_env(
    source: str,
    destination: str,
    include_keys: Optional[list[str]] = None,
    exclude_keys: Optional[list[str]] = None,
    masked: bool = False,
    overwrite: bool = False,
) -> CloneResult:
    """Clone a .env file to a destination path with optional filtering."""
    src_path = Path(source)
    dst_path = Path(destination)

    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    if dst_path.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {destination}. Use overwrite=True to replace.")

    env = load_env_file(source)

    keys_copied: list[str] = []
    keys_skipped: list[str] = []
    filtered: dict[str, str] = {}

    for key, value in env.items():
        if include_keys is not None and key not in include_keys:
            keys_skipped.append(key)
            continue
        if exclude_keys is not None and key in exclude_keys:
            keys_skipped.append(key)
            continue
        filtered[key] = value
        keys_copied.append(key)

    if masked:
        filtered = mask_env(filtered)

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(serialize_env(filtered))

    return CloneResult(
        source=source,
        destination=destination,
        keys_copied=keys_copied,
        keys_skipped=keys_skipped,
    )
