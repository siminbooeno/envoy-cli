"""Tests for envoy.dedup module."""

from __future__ import annotations

import pytest

from envoy.dedup import DedupResult, dedup_env, dedup_env_file, find_duplicates


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

def test_find_duplicates_detects_repeated_key():
    pairs = [("A", "1"), ("B", "2"), ("A", "3")]
    dupes = find_duplicates(pairs)
    assert "A" in dupes
    assert dupes["A"] == ["1", "3"]


def test_find_duplicates_returns_empty_when_no_dupes():
    pairs = [("A", "1"), ("B", "2")]
    assert find_duplicates(pairs) == {}


def test_find_duplicates_multiple_keys():
    pairs = [("A", "1"), ("B", "x"), ("A", "2"), ("B", "y")]
    dupes = find_duplicates(pairs)
    assert set(dupes.keys()) == {"A", "B"}


# ---------------------------------------------------------------------------
# dedup_env — keep='last'
# ---------------------------------------------------------------------------

def test_dedup_env_keep_last_retains_final_value():
    pairs = [("KEY", "old"), ("KEY", "new")]
    result = dedup_env(pairs, keep="last")
    assert result.kept["KEY"] == "new"


def test_dedup_env_keep_last_counts_removed():
    pairs = [("KEY", "a"), ("KEY", "b"), ("KEY", "c")]
    result = dedup_env(pairs, keep="last")
    assert result.total_removed == 2


# ---------------------------------------------------------------------------
# dedup_env — keep='first'
# ---------------------------------------------------------------------------

def test_dedup_env_keep_first_retains_initial_value():
    pairs = [("KEY", "first"), ("KEY", "second")]
    result = dedup_env(pairs, keep="first")
    assert result.kept["KEY"] == "first"


def test_dedup_env_keep_first_counts_removed():
    pairs = [("KEY", "a"), ("KEY", "b")]
    result = dedup_env(pairs, keep="first")
    assert result.total_removed == 1


# ---------------------------------------------------------------------------
# dedup_env — no duplicates
# ---------------------------------------------------------------------------

def test_dedup_env_no_duplicates_returns_zero_removed():
    pairs = [("A", "1"), ("B", "2"), ("C", "3")]
    result = dedup_env(pairs)
    assert result.total_removed == 0
    assert result.duplicates == {}
    assert result.kept == {"A": "1", "B": "2", "C": "3"}


def test_dedup_env_invalid_keep_raises():
    with pytest.raises(ValueError):
        dedup_env([("A", "1")], keep="middle")


# ---------------------------------------------------------------------------
# dedup_env_file
# ---------------------------------------------------------------------------

def test_dedup_env_file_dry_run_does_not_modify_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=old\nKEY=new\n")
    original = env_file.read_text()

    result = dedup_env_file(str(env_file), keep="last", dry_run=True)

    assert result.total_removed == 1
    assert env_file.read_text() == original  # unchanged


def test_dedup_env_file_writes_deduplicated_result(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=old\nOTHER=x\nKEY=new\n")

    dedup_env_file(str(env_file), keep="last", dry_run=False)

    content = env_file.read_text()
    assert content.count("KEY=") == 1
    assert "new" in content


def test_dedup_env_file_writes_to_output_path(tmp_path):
    env_file = tmp_path / ".env"
    out_file = tmp_path / "out.env"
    env_file.write_text("A=1\nA=2\n")

    dedup_env_file(str(env_file), keep="first", dry_run=False, output=str(out_file))

    assert out_file.exists()
    content = out_file.read_text()
    assert "A=1" in content
    assert content.count("A=") == 1


def test_dedup_env_file_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        dedup_env_file(str(tmp_path / "missing.env"))


def test_dedup_result_repr():
    r = DedupResult(kept={"A": "1"}, duplicates={"A": ["0"]}, total_removed=1)
    assert "DedupResult" in repr(r)
    assert "1 keys" in repr(r)
