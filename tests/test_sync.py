"""Tests for envoy.sync module."""
import pytest
from pathlib import Path

from envoy.sync import sync_env, merge_envs
from envoy.parser import load_env_file


@pytest.fixture
def tmp_source(tmp_path):
    p = tmp_path / "source.env"
    p.write_text("APP_NAME=envoy\nDEBUG=true\nSECRET_KEY=abc123\n")
    return str(p)


@pytest.fixture
def tmp_target(tmp_path):
    p = tmp_path / "target.env"
    p.write_text("APP_NAME=old_name\nEXTRA=keep\n")
    return str(p)


def test_sync_adds_missing_keys(tmp_source, tmp_target):
    result = sync_env(tmp_source, tmp_target, overwrite=False, add_missing=True)
    env = load_env_file(tmp_target)
    assert env["DEBUG"] == "true"
    assert env["SECRET_KEY"] == "abc123"
    assert result["added"] == 2


def test_sync_skips_existing_without_overwrite(tmp_source, tmp_target):
    result = sync_env(tmp_source, tmp_target, overwrite=False, add_missing=True)
    env = load_env_file(tmp_target)
    assert env["APP_NAME"] == "old_name"
    assert result["skipped"] >= 1


def test_sync_overwrites_when_flag_set(tmp_source, tmp_target):
    result = sync_env(tmp_source, tmp_target, overwrite=True, add_missing=True)
    env = load_env_file(tmp_target)
    assert env["APP_NAME"] == "envoy"
    assert result["updated"] == 1


def test_sync_preserves_extra_keys_by_default(tmp_source, tmp_target):
    sync_env(tmp_source, tmp_target, overwrite=True, add_missing=True, remove_extra=False)
    env = load_env_file(tmp_target)
    assert "EXTRA" in env


def test_sync_removes_extra_keys_when_flag_set(tmp_source, tmp_target):
    result = sync_env(tmp_source, tmp_target, overwrite=True, add_missing=True, remove_extra=True)
    env = load_env_file(tmp_target)
    assert "EXTRA" not in env
    assert result["removed"] == 1


def test_sync_creates_target_if_missing(tmp_source, tmp_path):
    target = str(tmp_path / "new.env")
    result = sync_env(tmp_source, target, add_missing=True)
    env = load_env_file(target)
    assert env["APP_NAME"] == "envoy"
    assert result["added"] == 3


def test_merge_envs_override():
    base = {"A": "1", "B": "2"}
    override = {"B": "99", "C": "3"}
    merged = merge_envs(base, override)
    assert merged == {"A": "1", "B": "99", "C": "3"}


def test_merge_envs_does_not_mutate_base():
    base = {"A": "1"}
    merge_envs(base, {"A": "2"})
    assert base["A"] == "1"
