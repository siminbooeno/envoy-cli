"""Watch an .env file for changes and report diffs automatically."""

import time
import os
from typing import Callable, Optional

from envoy.parser import load_env_file
from envoy.diff import compute_diff, has_changes
from envoy.audit import log_event


def _read_mtime(path: str) -> float:
    """Return the last modified time of a file."""
    return os.path.getmtime(path)


def _read_env_safe(path: str) -> dict:
    """Load env file, returning empty dict on failure."""
    try:
        return load_env_file(path)
    except Exception:
        return {}


def watch_env_file(
    path: str,
    on_change: Callable[[object], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll *path* every *interval* seconds and call *on_change* with an
    :class:`~envoy.diff.EnvDiff` whenever the file changes.

    Parameters
    ----------
    path:           Path to the .env file to watch.
    on_change:      Callback invoked with the diff when a change is detected.
    interval:       Polling interval in seconds.
    max_iterations: Stop after this many iterations (useful for testing).
    """
    last_mtime = _read_mtime(path) if os.path.exists(path) else None
    previous = _read_env_safe(path)
    iteration = 0

    while True:
        if max_iterations is not None and iteration >= max_iterations:
            break
        iteration += 1
        time.sleep(interval)

        if not os.path.exists(path):
            last_mtime = None
            previous = {}
            continue

        current_mtime = _read_mtime(path)
        if current_mtime == last_mtime:
            continue

        last_mtime = current_mtime
        current = _read_env_safe(path)
        diff = compute_diff(previous, current)

        if has_changes(diff):
            log_event("watch", path, metadata={"changes": len(diff.changes)})
            on_change(diff)

        previous = current
