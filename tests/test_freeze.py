"""Tests for envoy.freeze."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.freeze import (
    load_frozen,
    freeze_keys,
    unfreeze_keys,
    is_frozen,
    check_frozen,
    save_frozen,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASS=secret\nAPI_KEY=abc123\n")
    return f


def test_load_frozen_empty_when_no_file(env_file: Path) -> None:
    assert load_frozen(env_file) == set()


def test_freeze_keys_adds_keys(env_file: Path) -> None:
    added = freeze_keys(env_file, ["DB_HOST", "API_KEY"])
    assert set(added) == {"DB_HOST", "API_KEY"}
    assert load_frozen(env_file) == {"DB_HOST", "API_KEY"}


def test_freeze_keys_no_duplicates(env_file: Path) -> None:
    freeze_keys(env_file, ["DB_HOST"])
    added = freeze_keys(env_file, ["DB_HOST", "API_KEY"])
    assert added == ["API_KEY"]
    assert load_frozen(env_file) == {"DB_HOST", "API_KEY"}


def test_unfreeze_keys_removes_keys(env_file: Path) -> None:
    freeze_keys(env_file, ["DB_HOST", "API_KEY"])
    removed = unfreeze_keys(env_file, ["DB_HOST"])
    assert removed == ["DB_HOST"]
    assert load_frozen(env_file) == {"API_KEY"}


def test_unfreeze_keys_returns_empty_when_not_frozen(env_file: Path) -> None:
    removed = unfreeze_keys(env_file, ["NONEXISTENT"])
    assert removed == []


def test_is_frozen_true_after_freeze(env_file: Path) -> None:
    freeze_keys(env_file, ["DB_PASS"])
    assert is_frozen(env_file, "DB_PASS") is True


def test_is_frozen_false_when_not_frozen(env_file: Path) -> None:
    assert is_frozen(env_file, "DB_PASS") is False


def test_is_frozen_false_after_unfreeze(env_file: Path) -> None:
    freeze_keys(env_file, ["DB_PASS"])
    unfreeze_keys(env_file, ["DB_PASS"])
    assert is_frozen(env_file, "DB_PASS") is False


def test_check_frozen_returns_blocked_keys(env_file: Path) -> None:
    freeze_keys(env_file, ["DB_HOST", "API_KEY"])
    proposed = {"DB_HOST": "newhost", "DB_PASS": "newpass"}
    blocked = check_frozen(env_file, proposed)
    assert blocked == ["DB_HOST"]


def test_check_frozen_empty_when_none_frozen(env_file: Path) -> None:
    proposed = {"DB_HOST": "newhost", "API_KEY": "xyz"}
    assert check_frozen(env_file, proposed) == []


def test_save_and_load_roundtrip(env_file: Path) -> None:
    keys = {"FOO", "BAR", "BAZ"}
    save_frozen(env_file, keys)
    assert load_frozen(env_file) == keys
