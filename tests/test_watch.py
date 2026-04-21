"""Tests for envoy.watch (file-watching feature)."""

import os
import time
import pytest

from envoy.watch import watch_env_file


@pytest.fixture()
def env_file(tmp_path):
    """Return a writable .env file path inside a temp directory."""
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return str(f)


def _write(path: str, content: str) -> None:
    """Write *content* to *path* and bump mtime by nudging the file."""
    with open(path, "w") as fh:
        fh.write(content)
    # Ensure mtime changes even on fast filesystems
    stat = os.stat(path)
    os.utime(path, (stat.st_atime, stat.st_mtime + 1))


def test_watch_detects_added_key(env_file):
    collected = []

    def on_change(diff):
        collected.append(diff)

    # Modify the file before the first poll tick
    _write(env_file, "FOO=bar\nBAZ=qux\nNEW=value\n")

    watch_env_file(env_file, on_change, interval=0.05, max_iterations=3)

    assert len(collected) >= 1
    keys_changed = {c.key for diff in collected for c in diff.changes}
    assert "NEW" in keys_changed


def test_watch_detects_removed_key(env_file):
    collected = []

    _write(env_file, "FOO=bar\n")  # BAZ removed

    watch_env_file(env_file, lambda d: collected.append(d), interval=0.05, max_iterations=3)

    keys_changed = {c.key for diff in collected for c in diff.changes}
    assert "BAZ" in keys_changed


def test_watch_no_callback_when_unchanged(env_file):
    collected = []

    # Do NOT modify the file — mtime stays the same
    watch_env_file(env_file, lambda d: collected.append(d), interval=0.05, max_iterations=4)

    assert collected == []


def test_watch_handles_missing_file(tmp_path):
    """watch_env_file should not crash when the file does not exist yet."""
    missing = str(tmp_path / "missing.env")
    collected = []

    # Should complete without exception
    watch_env_file(missing, lambda d: collected.append(d), interval=0.05, max_iterations=3)

    assert collected == []


def test_watch_stops_after_max_iterations(env_file):
    """Ensure the loop terminates after max_iterations."""
    call_count = [0]

    def on_change(diff):
        call_count[0] += 1

    _write(env_file, "FOO=changed\n")
    watch_env_file(env_file, on_change, interval=0.02, max_iterations=5)

    # The function must have returned (not hung)
    assert True
