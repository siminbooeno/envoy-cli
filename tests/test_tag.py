"""Tests for envoy/tag.py"""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.tag import (
    load_tags,
    save_tags,
    add_tag,
    remove_tag,
    get_tags,
    keys_with_tag,
    all_tags,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nDEBUG=true\n")
    return f


def test_load_tags_empty_when_no_file(env_file: Path) -> None:
    assert load_tags(env_file) == {}


def test_add_tag_stores_tag(env_file: Path) -> None:
    result = add_tag(env_file, "API_KEY", "secret")
    assert "API_KEY" in result
    assert "secret" in result["API_KEY"]


def test_add_tag_persists(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    tags = load_tags(env_file)
    assert tags["API_KEY"] == ["secret"]


def test_add_tag_no_duplicates(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "API_KEY", "secret")
    tags = load_tags(env_file)
    assert tags["API_KEY"].count("secret") == 1


def test_add_multiple_tags(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "API_KEY", "required")
    tags = get_tags(env_file, "API_KEY")
    assert "secret" in tags
    assert "required" in tags


def test_remove_tag(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    remove_tag(env_file, "API_KEY", "secret")
    assert get_tags(env_file, "API_KEY") == []


def test_remove_tag_cleans_up_empty_key(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    remove_tag(env_file, "API_KEY", "secret")
    tags = load_tags(env_file)
    assert "API_KEY" not in tags


def test_remove_nonexistent_tag_is_safe(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    result = remove_tag(env_file, "API_KEY", "nonexistent")
    assert "secret" in result["API_KEY"]


def test_get_tags_returns_empty_for_unknown_key(env_file: Path) -> None:
    assert get_tags(env_file, "MISSING_KEY") == []


def test_keys_with_tag(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "DB_PASS", "secret")
    add_tag(env_file, "DEBUG", "optional")
    keys = keys_with_tag(env_file, "secret")
    assert "API_KEY" in keys
    assert "DB_PASS" in keys
    assert "DEBUG" not in keys


def test_keys_with_tag_empty_when_none_match(env_file: Path) -> None:
    add_tag(env_file, "DEBUG", "optional")
    assert keys_with_tag(env_file, "secret") == []


def test_all_tags_returns_unique_set(env_file: Path) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "DB_PASS", "secret")
    add_tag(env_file, "DEBUG", "optional")
    tags = all_tags(env_file)
    assert tags == {"secret", "optional"}


def test_all_tags_empty_when_no_tags(env_file: Path) -> None:
    assert all_tags(env_file) == set()
