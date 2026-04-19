"""Diff utilities for comparing two .env variable sets."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class ChangeType(str, Enum):
    ADDED = 'added'
    REMOVED = 'removed'
    MODIFIED = 'modified'
    UNCHANGED = 'unchanged'


@dataclass
class EnvDiff:
    key: str
    change: ChangeType
    old_value: str | None = None
    new_value: str | None = None


def compute_diff(base: Dict[str, str], target: Dict[str, str]) -> List[EnvDiff]:
    """Compute the diff between two env dictionaries."""
    diffs: List[EnvDiff] = []
    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        if key in base and key not in target:
            diffs.append(EnvDiff(key, ChangeType.REMOVED, old_value=base[key]))
        elif key not in base and key in target:
            diffs.append(EnvDiff(key, ChangeType.ADDED, new_value=target[key]))
        elif base[key] != target[key]:
            diffs.append(EnvDiff(key, ChangeType.MODIFIED, old_value=base[key], new_value=target[key]))
        else:
            diffs.append(EnvDiff(key, ChangeType.UNCHANGED, old_value=base[key], new_value=target[key]))

    return diffs


def has_changes(diffs: List[EnvDiff]) -> bool:
    return any(d.change != ChangeType.UNCHANGED for d in diffs)
