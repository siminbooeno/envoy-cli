"""Tests for envoy.merge."""

import pytest
from envoy.merge import (
    merge_env_dicts,
    merge_env_files,
    MergeStrategy,
    MergeConflict,
)


# ---------------------------------------------------------------------------
# merge_env_dicts
# ---------------------------------------------------------------------------

def test_merge_last_strategy_keeps_last_value():
    a = {"KEY": "from_a", "ONLY_A": "1"}
    b = {"KEY": "from_b", "ONLY_B": "2"}
    result = merge_env_dicts([a, b], strategy=MergeStrategy.LAST)
    assert result["KEY"] == "from_b"
    assert result["ONLY_A"] == "1"
    assert result["ONLY_B"] == "2"


def test_merge_first_strategy_keeps_first_value():
    a = {"KEY": "from_a"}
    b = {"KEY": "from_b"}
    result = merge_env_dicts([a, b], strategy=MergeStrategy.FIRST)
    assert result["KEY"] == "from_a"


def test_merge_strict_raises_on_conflict():
    a = {"KEY": "val1"}
    b = {"KEY": "val2"}
    with pytest.raises(MergeConflict) as exc_info:
        merge_env_dicts([a, b], strategy=MergeStrategy.STRICT)
    assert exc_info.value.key == "KEY"


def test_merge_strict_no_conflict_passes():
    a = {"A": "1"}
    b = {"B": "2"}
    result = merge_env_dicts([a, b], strategy=MergeStrategy.STRICT)
    assert result == {"A": "1", "B": "2"}


def test_merge_strict_same_value_no_conflict():
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = merge_env_dicts([a, b], strategy=MergeStrategy.STRICT)
    assert result["KEY"] == "same"


def test_merge_three_files_last_wins():
    a = {"X": "1"}
    b = {"X": "2"}
    c = {"X": "3"}
    result = merge_env_dicts([a, b, c], strategy=MergeStrategy.LAST)
    assert result["X"] == "3"


def test_merge_empty_list_returns_empty():
    assert merge_env_dicts([]) == {}


# ---------------------------------------------------------------------------
# merge_env_files
# ---------------------------------------------------------------------------

@pytest.fixture
def env_a(tmp_path):
    p = tmp_path / "a.env"
    p.write_text("HOST=localhost\nPORT=5432\n")
    return str(p)


@pytest.fixture
def env_b(tmp_path):
    p = tmp_path / "b.env"
    p.write_text("PORT=9999\nDEBUG=true\n")
    return str(p)


def test_merge_env_files_returns_merged_dict(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "9999"   # last wins
    assert result["DEBUG"] == "true"


def test_merge_env_files_writes_output(tmp_path, env_a, env_b):
    out = str(tmp_path / "merged.env")
    merge_env_files([env_a, env_b], output_path=out)
    content = open(out).read()
    assert "HOST" in content
    assert "DEBUG" in content


def test_merge_env_files_missing_file_raises(env_a):
    with pytest.raises(FileNotFoundError):
        merge_env_files([env_a, "/nonexistent/.env"])
