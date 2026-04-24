"""Tests for envoy.extract module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.extract import extract_keys, extract_env_file


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\nDEBUG=true\n")
    return f


def test_extract_keys_returns_subset():
    env = {"A": "1", "B": "2", "C": "3"}
    result = extract_keys(env, ["A", "C"])
    assert result.extracted == {"A": "1", "C": "3"}
    assert result.total_missing == 0


def test_extract_keys_reports_missing():
    env = {"A": "1"}
    result = extract_keys(env, ["A", "Z"])
    assert "Z" in result.missing
    assert result.total_missing == 1


def test_extract_keys_ignore_missing_skips_error():
    env = {"A": "1"}
    result = extract_keys(env, ["A", "MISSING"], ignore_missing=True)
    assert result.total_missing == 0
    assert "A" in result.extracted


def test_extract_env_file_no_dest(source_file: Path):
    result = extract_env_file(source_file, ["DB_HOST", "DB_PORT"])
    assert result.extracted == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result.total_missing == 0


def test_extract_env_file_writes_dest(source_file: Path, tmp_path: Path):
    dest = tmp_path / "extracted.env"
    result = extract_env_file(source_file, ["DB_HOST"], dest=dest)
    assert dest.exists()
    content = dest.read_text()
    assert "DB_HOST=localhost" in content
    assert result.total_extracted == 1


def test_extract_env_file_missing_key_stops_write(source_file: Path, tmp_path: Path):
    dest = tmp_path / "out.env"
    result = extract_env_file(source_file, ["DB_HOST", "NONEXISTENT"], dest=dest)
    assert "NONEXISTENT" in result.missing
    assert not dest.exists()


def test_extract_env_file_no_overwrite_skips_existing(source_file: Path, tmp_path: Path):
    dest = tmp_path / "out.env"
    dest.write_text("DB_HOST=already_set\n")
    result = extract_env_file(source_file, ["DB_HOST", "DB_PORT"], dest=dest, overwrite=False)
    assert "DB_HOST" in result.skipped
    content = dest.read_text()
    assert "already_set" in content


def test_extract_env_file_overwrite_replaces_existing(source_file: Path, tmp_path: Path):
    dest = tmp_path / "out.env"
    dest.write_text("DB_HOST=already_set\n")
    result = extract_env_file(source_file, ["DB_HOST"], dest=dest, overwrite=True)
    content = dest.read_text()
    assert "localhost" in content
    assert result.total_extracted == 1


def test_extract_result_repr():
    from envoy.extract import ExtractResult
    r = ExtractResult(extracted={"A": "1"}, missing=["B"], skipped=["C"])
    rep = repr(r)
    assert "ExtractResult" in rep
    assert "extracted=1" in rep
