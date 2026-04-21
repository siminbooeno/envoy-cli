"""Tests for envoy.history module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.history import (
    clear_history,
    diff_history,
    load_history,
    record_snapshot,
)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret123\nDEBUG=true\n")
    return str(f)


def test_record_snapshot_creates_entry(env_file):
    entry = record_snapshot(env_file)
    assert "timestamp" in entry
    assert "data" in entry
    assert entry["data"]["API_KEY"] == "secret123"
    assert entry["data"]["DEBUG"] == "true"


def test_record_snapshot_with_label(env_file):
    entry = record_snapshot(env_file, label="initial")
    assert entry["label"] == "initial"


def test_load_history_empty_when_no_file(env_file):
    entries = load_history(env_file)
    assert entries == []


def test_load_history_returns_all_entries(env_file):
    record_snapshot(env_file, label="first")
    record_snapshot(env_file, label="second")
    entries = load_history(env_file)
    assert len(entries) == 2
    assert entries[0]["label"] == "first"
    assert entries[1]["label"] == "second"


def test_diff_history_detects_added_key(env_file):
    record_snapshot(env_file)
    env_path = Path(env_file)
    env_path.write_text("API_KEY=secret123\nDEBUG=true\nNEW_KEY=hello\n")
    record_snapshot(env_file)
    changes = diff_history(env_file, 0, 1)
    keys = [c.key for c in changes]
    assert "NEW_KEY" in keys


def test_diff_history_detects_removed_key(env_file):
    record_snapshot(env_file)
    env_path = Path(env_file)
    env_path.write_text("DEBUG=true\n")
    record_snapshot(env_file)
    changes = diff_history(env_file, 0, 1)
    keys = [c.key for c in changes]
    assert "API_KEY" in keys


def test_diff_history_index_out_of_range(env_file):
    record_snapshot(env_file)
    with pytest.raises(IndexError):
        diff_history(env_file, 0, 5)


def test_clear_history_removes_file(env_file):
    record_snapshot(env_file)
    assert len(load_history(env_file)) == 1
    clear_history(env_file)
    assert load_history(env_file) == []


def test_clear_history_no_error_when_empty(env_file):
    # Should not raise even if no history exists
    clear_history(env_file)
