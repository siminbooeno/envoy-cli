"""Tests for envoy/group.py"""

import pytest
from pathlib import Path

from envoy.group import (
    add_to_group,
    delete_group,
    get_group_keys,
    list_groups,
    load_groups,
    remove_from_group,
    save_groups,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc\n")
    return f


def test_load_groups_empty_when_no_file(env_file: Path):
    assert load_groups(env_file) == {}


def test_save_and_load_groups(env_file: Path):
    groups = {"database": ["DB_HOST", "DB_PORT"]}
    save_groups(env_file, groups)
    loaded = load_groups(env_file)
    assert loaded == groups


def test_add_to_group_creates_group(env_file: Path):
    result = add_to_group(env_file, "database", ["DB_HOST", "DB_PORT"])
    assert "database" in result
    assert "DB_HOST" in result["database"]
    assert "DB_PORT" in result["database"]


def test_add_to_group_merges_keys(env_file: Path):
    add_to_group(env_file, "database", ["DB_HOST"])
    result = add_to_group(env_file, "database", ["DB_PORT"])
    assert set(result["database"]) == {"DB_HOST", "DB_PORT"}


def test_add_to_group_deduplicates(env_file: Path):
    add_to_group(env_file, "database", ["DB_HOST", "DB_HOST"])
    keys = get_group_keys(env_file, "database")
    assert keys is not None
    assert keys.count("DB_HOST") == 1


def test_remove_from_group_removes_key(env_file: Path):
    add_to_group(env_file, "database", ["DB_HOST", "DB_PORT"])
    result = remove_from_group(env_file, "database", ["DB_HOST"])
    assert "DB_HOST" not in result["database"]
    assert "DB_PORT" in result["database"]


def test_remove_from_group_deletes_empty_group(env_file: Path):
    add_to_group(env_file, "solo", ["DB_HOST"])
    result = remove_from_group(env_file, "solo", ["DB_HOST"])
    assert "solo" not in result


def test_remove_from_nonexistent_group_is_noop(env_file: Path):
    result = remove_from_group(env_file, "ghost", ["DB_HOST"])
    assert result == {}


def test_delete_group_removes_it(env_file: Path):
    add_to_group(env_file, "database", ["DB_HOST"])
    existed = delete_group(env_file, "database")
    assert existed is True
    assert "database" not in load_groups(env_file)


def test_delete_nonexistent_group_returns_false(env_file: Path):
    assert delete_group(env_file, "missing") is False


def test_get_group_keys_returns_none_for_missing(env_file: Path):
    assert get_group_keys(env_file, "nope") is None


def test_list_groups_returns_names(env_file: Path):
    add_to_group(env_file, "database", ["DB_HOST"])
    add_to_group(env_file, "secrets", ["SECRET_KEY"])
    names = list_groups(env_file)
    assert set(names) == {"database", "secrets"}


def test_list_groups_empty_when_no_groups(env_file: Path):
    assert list_groups(env_file) == []
