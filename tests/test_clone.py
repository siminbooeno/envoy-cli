"""Tests for envoy.clone module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.clone import clone_env, CloneResult
from envoy.parser import load_env_file


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / "source.env"
    f.write_text("APP_NAME=myapp\nDB_PASSWORD=secret123\nDEBUG=true\nAPI_KEY=abc123\n")
    return f


def test_clone_creates_destination(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    result = clone_env(str(source_file), str(dest))
    assert dest.exists()
    assert isinstance(result, CloneResult)


def test_clone_copies_all_keys_by_default(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    result = clone_env(str(source_file), str(dest))
    env = load_env_file(str(dest))
    assert env["APP_NAME"] == "myapp"
    assert env["DEBUG"] == "true"
    assert result.total_copied == 4
    assert result.total_skipped == 0


def test_clone_include_keys(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    result = clone_env(str(source_file), str(dest), include_keys=["APP_NAME", "DEBUG"])
    env = load_env_file(str(dest))
    assert "APP_NAME" in env
    assert "DEBUG" in env
    assert "DB_PASSWORD" not in env
    assert result.total_copied == 2
    assert result.total_skipped == 2


def test_clone_exclude_keys(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    result = clone_env(str(source_file), str(dest), exclude_keys=["DB_PASSWORD", "API_KEY"])
    env = load_env_file(str(dest))
    assert "DB_PASSWORD" not in env
    assert "API_KEY" not in env
    assert "APP_NAME" in env
    assert result.total_skipped == 2


def test_clone_masked_hides_secrets(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    clone_env(str(source_file), str(dest), masked=True)
    env = load_env_file(str(dest))
    assert env["DB_PASSWORD"] != "secret123"
    assert env["APP_NAME"] == "myapp"


def test_clone_raises_if_source_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        clone_env(str(tmp_path / "nope.env"), str(tmp_path / "dest.env"))


def test_clone_raises_if_dest_exists_no_overwrite(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    dest.write_text("EXISTING=1\n")
    with pytest.raises(FileExistsError):
        clone_env(str(source_file), str(dest), overwrite=False)


def test_clone_overwrites_when_flag_set(source_file: Path, tmp_path: Path):
    dest = tmp_path / "dest.env"
    dest.write_text("EXISTING=1\n")
    clone_env(str(source_file), str(dest), overwrite=True)
    env = load_env_file(str(dest))
    assert "APP_NAME" in env
    assert "EXISTING" not in env


def test_clone_creates_nested_destination(source_file: Path, tmp_path: Path):
    dest = tmp_path / "subdir" / "nested" / "dest.env"
    clone_env(str(source_file), str(dest))
    assert dest.exists()
