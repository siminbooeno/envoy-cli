"""Merge multiple .env files into one, with conflict resolution strategies."""

from enum import Enum
from typing import Dict, List, Optional
from envoy.parser import load_env_file, serialize_env


class MergeStrategy(str, Enum):
    FIRST = "first"   # keep value from first file that defines the key
    LAST = "last"     # keep value from last file that defines the key
    STRICT = "strict" # raise on any conflicting key


class MergeConflict(Exception):
    """Raised when STRICT strategy encounters a conflicting key."""

    def __init__(self, key: str, values: List[str]):
        self.key = key
        self.values = values
        super().__init__(
            f"Conflict on key '{key}': {values}"
        )


def merge_env_dicts(
    envs: List[Dict[str, str]],
    strategy: MergeStrategy = MergeStrategy.LAST,
) -> Dict[str, str]:
    """Merge a list of env dicts according to the given strategy."""
    merged: Dict[str, str] = {}
    origins: Dict[str, str] = {}  # key -> value already stored

    for env in envs:
        for key, value in env.items():
            if key in merged:
                if strategy == MergeStrategy.STRICT and merged[key] != value:
                    raise MergeConflict(key, [merged[key], value])
                if strategy == MergeStrategy.LAST:
                    merged[key] = value
                # FIRST: do nothing, keep existing
            else:
                merged[key] = value

    return merged


def merge_env_files(
    paths: List[str],
    output_path: Optional[str] = None,
    strategy: MergeStrategy = MergeStrategy.LAST,
) -> Dict[str, str]:
    """Load multiple .env files and merge them.

    If *output_path* is given the merged result is written there.
    Returns the merged dict.
    """
    envs = [load_env_file(p) for p in paths]
    merged = merge_env_dicts(envs, strategy=strategy)

    if output_path:
        content = serialize_env(merged)
        with open(output_path, "w") as fh:
            fh.write(content)

    return merged
