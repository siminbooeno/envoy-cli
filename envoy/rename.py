"""Rename keys in .env files with optional cascading across multiple files."""

from pathlib import Path
from typing import Optional
from envoy.parser import load_env_file, serialize_env


class RenameResult:
    def __init__(self):
        self.renamed: list[tuple[str, str]] = []  # (old_key, new_key)
        self.skipped: list[str] = []              # keys not found
        self.conflicts: list[str] = []            # new_key already exists

    @property
    def success(self) -> bool:
        return len(self.renamed) > 0


def rename_key(
    env: dict[str, str],
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> RenameResult:
    """Rename a single key in an env dict. Returns a RenameResult."""
    result = RenameResult()

    if old_key not in env:
        result.skipped.append(old_key)
        return result

    if new_key in env and not overwrite:
        result.conflicts.append(new_key)
        return result

    # Preserve insertion order by rebuilding the dict
    updated = {}
    for k, v in env.items():
        if k == old_key:
            updated[new_key] = v
        elif k != new_key:  # drop old new_key if overwrite
            updated[k] = v

    env.clear()
    env.update(updated)
    result.renamed.append((old_key, new_key))
    return result


def rename_env_file(
    path: Path,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> RenameResult:
    """Rename a key in a .env file on disk."""
    env = load_env_file(path)
    result = rename_key(env, old_key, new_key, overwrite=overwrite)

    if result.success and not dry_run:
        path.write_text(serialize_env(env))

    return result


def rename_across_files(
    paths: list[Path],
    old_key: str,
    new_key: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[Path, RenameResult]:
    """Rename a key across multiple .env files."""
    results: dict[Path, RenameResult] = {}
    for path in paths:
        results[path] = rename_env_file(
            path, old_key, new_key, overwrite=overwrite, dry_run=dry_run
        )
    return results
