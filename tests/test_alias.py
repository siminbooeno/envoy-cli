"""Tests for envoy.alias module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.alias import (
    load_aliases,
    save_aliases,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    apply_aliases,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASSWORD=secret\n")
    return f


def test_load_aliases_empty_when_no_file(env_file):
    assert load_aliases(env_file) == {}


def test_save_and_load_aliases(env_file):
    save_aliases(env_file, {"HOST": "DB_HOST"})
    assert load_aliases(env_file) == {"HOST": "DB_HOST"}


def test_add_alias_stores_entry(env_file):
    add_alias(env_file, "HOST", "DB_HOST")
    aliases = load_aliases(env_file)
    assert aliases["HOST"] == "DB_HOST"


def test_add_alias_persists_multiple(env_file):
    add_alias(env_file, "HOST", "DB_HOST")
    add_alias(env_file, "PASS", "DB_PASSWORD")
    aliases = load_aliases(env_file)
    assert len(aliases) == 2
    assert aliases["PASS"] == "DB_PASSWORD"


def test_remove_alias_returns_true_when_found(env_file):
    add_alias(env_file, "HOST", "DB_HOST")
    result = remove_alias(env_file, "HOST")
    assert result is True
    assert load_aliases(env_file) == {}


def test_remove_alias_returns_false_when_missing(env_file):
    result = remove_alias(env_file, "NONEXISTENT")
    assert result is False


def test_resolve_alias_returns_original(env_file):
    add_alias(env_file, "HOST", "DB_HOST")
    assert resolve_alias(env_file, "HOST") == "DB_HOST"


def test_resolve_alias_returns_none_when_missing(env_file):
    assert resolve_alias(env_file, "GHOST") is None


def test_list_aliases_returns_entries(env_file):
    add_alias(env_file, "HOST", "DB_HOST")
    add_alias(env_file, "PASS", "DB_PASSWORD")
    entries = list_aliases(env_file)
    keys = {e["alias"] for e in entries}
    assert "HOST" in keys
    assert "PASS" in keys


def test_list_aliases_empty(env_file):
    assert list_aliases(env_file) == []


def test_apply_aliases_injects_values(env_file):
    env = {"DB_HOST": "localhost", "DB_PASSWORD": "secret"}
    aliases = {"HOST": "DB_HOST"}
    result = apply_aliases(env, aliases)
    assert result["HOST"] == "localhost"
    assert result["DB_HOST"] == "localhost"  # original preserved


def test_apply_aliases_skips_missing_original(env_file):
    env = {"DB_HOST": "localhost"}
    aliases = {"PASS": "DB_PASSWORD"}  # DB_PASSWORD not in env
    result = apply_aliases(env, aliases)
    assert "PASS" not in result
