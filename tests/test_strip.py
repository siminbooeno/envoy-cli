"""Tests for envoy.strip module."""

from __future__ import annotations

import pytest

from envoy.strip import StripResult, strip_keys, strip_env_file


SAMPLE = {
    "APP_NAME": "myapp",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
}


def test_strip_explicit_keys_removes_them():
    result = strip_keys(SAMPLE, keys=["DEBUG", "APP_NAME"])
    assert "DEBUG" not in result.stripped
    assert "APP_NAME" not in result.stripped
    assert result.total_removed == 2


def test_strip_explicit_keys_preserves_others():
    result = strip_keys(SAMPLE, keys=["DEBUG"])
    assert "DB_HOST" in result.stripped
    assert "SECRET_KEY" in result.stripped


def test_strip_by_prefix_removes_matching():
    result = strip_keys(SAMPLE, prefix="DB_")
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped
    assert result.total_removed == 2


def test_strip_by_prefix_preserves_non_matching():
    result = strip_keys(SAMPLE, prefix="DB_")
    assert "APP_NAME" in result.stripped
    assert "SECRET_KEY" in result.stripped


def test_strip_by_pattern_removes_matching():
    result = strip_keys(SAMPLE, pattern=r"^DB_")
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped


def test_strip_by_pattern_partial_match():
    result = strip_keys(SAMPLE, pattern=r"SECRET")
    assert "SECRET_KEY" not in result.stripped
    assert result.total_removed == 1


def test_strip_skips_missing_explicit_key():
    result = strip_keys(SAMPLE, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped_keys
    assert result.total_skipped == 1
    assert result.total_removed == 0


def test_strip_no_criteria_raises():
    with pytest.raises(ValueError, match="At least one"):
        strip_keys(SAMPLE)


def test_strip_returns_copy_not_mutating_input():
    original = dict(SAMPLE)
    strip_keys(SAMPLE, keys=["DEBUG"])
    assert SAMPLE == original


def test_strip_combined_keys_and_prefix():
    result = strip_keys(SAMPLE, keys=["APP_NAME"], prefix="DB_")
    assert "APP_NAME" not in result.stripped
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped
    assert result.total_removed == 3


def test_strip_env_file_writes_output(tmp_path):
    src = tmp_path / ".env"
    src.write_text("APP_NAME=myapp\nDB_HOST=localhost\nDEBUG=true\n")
    dest = tmp_path / ".env.stripped"

    result = strip_env_file(str(src), dest=str(dest), keys=["DEBUG"])

    assert dest.exists()
    content = dest.read_text()
    assert "DEBUG" not in content
    assert "APP_NAME" in content
    assert result.total_removed == 1


def test_strip_env_file_no_dest_does_not_write(tmp_path):
    src = tmp_path / ".env"
    src.write_text("APP_NAME=myapp\nDEBUG=true\n")
    dest = tmp_path / ".env.stripped"

    strip_env_file(str(src), keys=["DEBUG"])

    assert not dest.exists()
