"""Tests for envoy.rename module."""

import pytest
from pathlib import Path
from envoy.rename import rename_key, rename_env_file, rename_across_files


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_NAME=myapp\nSECRET_KEY=abc123\nDEBUG=true\n")
    return f


def test_rename_key_success():
    env = {"OLD_NAME": "value", "OTHER": "x"}
    result = rename_key(env, "OLD_NAME", "NEW_NAME")
    assert result.success
    assert ("OLD_NAME", "NEW_NAME") in result.renamed
    assert "NEW_NAME" in env
    assert "OLD_NAME" not in env
    assert env["NEW_NAME"] == "value"


def test_rename_key_preserves_order():
    env = {"A": "1", "B": "2", "C": "3"}
    rename_key(env, "B", "B2")
    assert list(env.keys()) == ["A", "B2", "C"]


def test_rename_key_missing_key():
    env = {"ONLY": "val"}
    result = rename_key(env, "MISSING", "NEW")
    assert not result.success
    assert "MISSING" in result.skipped
    assert "ONLY" in env


def test_rename_key_conflict_without_overwrite():
    env = {"OLD": "1", "NEW": "2"}
    result = rename_key(env, "OLD", "NEW", overwrite=False)
    assert not result.success
    assert "NEW" in result.conflicts
    assert "OLD" in env  # unchanged


def test_rename_key_conflict_with_overwrite():
    env = {"OLD": "1", "NEW": "2"}
    result = rename_key(env, "OLD", "NEW", overwrite=True)
    assert result.success
    assert env["NEW"] == "1"
    assert "OLD" not in env


def test_rename_env_file_writes_to_disk(env_file):
    result = rename_env_file(env_file, "APP_NAME", "APPLICATION_NAME")
    assert result.success
    content = env_file.read_text()
    assert "APPLICATION_NAME" in content
    assert "APP_NAME" not in content


def test_rename_env_file_dry_run_does_not_write(env_file):
    original = env_file.read_text()
    result = rename_env_file(env_file, "APP_NAME", "APPLICATION_NAME", dry_run=True)
    assert result.success
    assert env_file.read_text() == original


def test_rename_env_file_missing_key(env_file):
    result = rename_env_file(env_file, "NONEXISTENT", "WHATEVER")
    assert not result.success
    assert "NONEXISTENT" in result.skipped


def test_rename_across_files(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    f2.write_text("DB_HOST=remotehost\nOTHER=val\n")

    results = rename_across_files([f1, f2], "DB_HOST", "DATABASE_HOST")

    assert results[f1].success
    assert results[f2].success
    assert "DATABASE_HOST" in f1.read_text()
    assert "DATABASE_HOST" in f2.read_text()


def test_rename_across_files_partial_missing(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("TARGET=yes\n")
    f2.write_text("OTHER=no\n")

    results = rename_across_files([f1, f2], "TARGET", "RENAMED")

    assert results[f1].success
    assert not results[f2].success
    assert "TARGET" in results[f2].skipped
