"""Tests for envoy.fmt formatting module."""

import pytest
from pathlib import Path
from envoy.fmt import sort_keys, group_by_prefix, format_env, format_env_file


# ---------------------------------------------------------------------------
# Unit tests for pure helpers
# ---------------------------------------------------------------------------

def test_sort_keys_returns_alphabetical_order():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_keys(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_does_not_mutate_input():
    env = {"B": "1", "A": "2"}
    sort_keys(env)
    assert list(env.keys()) == ["B", "A"]


def test_group_by_prefix_splits_on_underscore():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "envoy"}
    groups = group_by_prefix(env)
    assert set(groups.keys()) == {"DB", "APP"}
    assert "DB_HOST" in groups["DB"]
    assert "APP_NAME" in groups["APP"]


def test_group_by_prefix_no_underscore_uses_key_as_group():
    env = {"PORT": "8080"}
    groups = group_by_prefix(env)
    assert "PORT" in groups
    assert groups["PORT"]["PORT"] == "8080"


# ---------------------------------------------------------------------------
# format_env
# ---------------------------------------------------------------------------

def test_format_env_sorts_by_default():
    env = {"Z": "26", "A": "1"}
    output = format_env(env)
    lines = [l for l in output.splitlines() if l.strip()]
    assert lines[0].startswith("A=")
    assert lines[1].startswith("Z=")


def test_format_env_no_sort_preserves_order():
    env = {"Z": "26", "A": "1"}
    output = format_env(env, sort=False)
    lines = [l for l in output.splitlines() if l.strip()]
    assert lines[0].startswith("Z=")


def test_format_env_group_adds_blank_lines():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy"}
    output = format_env(env, sort=True, group=True)
    assert "\n\n" in output


def test_format_env_comment_groups_adds_headers():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy"}
    output = format_env(env, sort=True, group=True, comment_groups=True)
    assert "# APP" in output or "# DB" in output


def test_format_env_no_group_no_blank_lines():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy"}
    output = format_env(env, sort=True, group=False)
    assert "\n\n" not in output


# ---------------------------------------------------------------------------
# format_env_file
# ---------------------------------------------------------------------------

@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("ZEBRA=1\nAPPLE=2\n")
    return f


def test_format_env_file_sorts_and_writes(env_file: Path):
    _, changed = format_env_file(str(env_file))
    assert changed
    content = env_file.read_text()
    lines = [l for l in content.splitlines() if l.strip()]
    assert lines[0].startswith("APPLE=")


def test_format_env_file_dry_run_does_not_write(env_file: Path):
    original = env_file.read_text()
    format_env_file(str(env_file), dry_run=True)
    assert env_file.read_text() == original


def test_format_env_file_already_formatted_not_changed(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text("APPLE=2\nZEBRA=1\n")
    _, changed = format_env_file(str(f))
    assert not changed


def test_format_env_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        format_env_file("/nonexistent/.env")
