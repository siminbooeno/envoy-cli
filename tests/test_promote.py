"""Tests for envoy.promote module."""

import pytest
from pathlib import Path
from envoy.promote import promote_keys, promote_env_file


@pytest.fixture
def source_file(tmp_path):
    p = tmp_path / "source.env"
    p.write_text("DB_HOST=prod-db\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return str(p)


@pytest.fixture
def target_file(tmp_path):
    p = tmp_path / "target.env"
    p.write_text("DB_HOST=staging-db\nAPP_ENV=staging\n")
    return str(p)


def test_promote_keys_adds_missing():
    source = {"A": "1", "B": "2"}
    target = {"C": "3"}
    result, promoted = promote_keys(source, target)
    assert "A" in result
    assert "B" in result
    assert promoted == ["A", "B"]


def test_promote_keys_skips_existing_without_overwrite():
    source = {"A": "new"}
    target = {"A": "old"}
    result, promoted = promote_keys(source, target, overwrite=False)
    assert result["A"] == "old"
    assert promoted == []


def test_promote_keys_overwrites_when_flag_set():
    source = {"A": "new"}
    target = {"A": "old"}
    result, promoted = promote_keys(source, target, overwrite=True)
    assert result["A"] == "new"
    assert "A" in promoted


def test_promote_keys_with_key_filter():
    source = {"A": "1", "B": "2", "C": "3"}
    target = {}
    result, promoted = promote_keys(source, target, keys=["A", "C"])
    assert "A" in result
    assert "C" in result
    assert "B" not in result
    assert promoted == ["A", "C"]


def test_promote_keys_ignores_missing_filter_keys():
    source = {"A": "1"}
    target = {}
    result, promoted = promote_keys(source, target, keys=["A", "Z"])
    assert "A" in result
    assert "Z" not in result
    assert promoted == ["A"]


def test_promote_env_file_writes_target(source_file, target_file):
    promoted = promote_env_file(source_file, target_file, keys=["DB_PORT"])
    assert "DB_PORT" in promoted
    content = Path(target_file).read_text()
    assert "DB_PORT=5432" in content


def test_promote_env_file_dry_run_no_write(source_file, target_file):
    original = Path(target_file).read_text()
    promoted = promote_env_file(source_file, target_file, keys=["DB_PORT"], dry_run=True)
    assert "DB_PORT" in promoted
    assert Path(target_file).read_text() == original


def test_promote_env_file_returns_empty_when_nothing_to_promote(source_file, target_file):
    promoted = promote_env_file(source_file, target_file, keys=["DB_HOST"], overwrite=False)
    assert promoted == []
