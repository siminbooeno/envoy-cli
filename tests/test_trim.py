"""Tests for envoy.trim module."""

import pytest
from pathlib import Path

from envoy.trim import trim_env, trim_env_file


# ---------------------------------------------------------------------------
# Unit tests — trim_env
# ---------------------------------------------------------------------------

def test_trim_env_removes_leading_whitespace():
    env = {"KEY": "  hello"}
    result = trim_env(env)
    assert result.trimmed == {"KEY": "hello"}
    assert result.total_trimmed == 1


def test_trim_env_removes_trailing_whitespace():
    env = {"KEY": "hello   "}
    result = trim_env(env)
    assert result.trimmed == {"KEY": "hello"}


def test_trim_env_removes_both_sides():
    env = {"KEY": "  hello  "}
    result = trim_env(env)
    assert result.trimmed["KEY"] == "hello"


def test_trim_env_clean_value_is_unchanged():
    env = {"KEY": "clean"}
    result = trim_env(env)
    assert result.total_trimmed == 0
    assert "KEY" in result.unchanged


def test_trim_env_only_specified_keys():
    env = {"A": "  a  ", "B": "  b  "}
    result = trim_env(env, keys=["A"])
    assert "A" in result.trimmed
    assert "B" in result.unchanged
    assert result.unchanged["B"] == "  b  "


def test_trim_env_strip_quotes_double():
    env = {"KEY": '"hello"'}
    result = trim_env(env, strip_quotes=True)
    assert result.trimmed["KEY"] == "hello"


def test_trim_env_strip_quotes_single():
    env = {"KEY": "'world'"}
    result = trim_env(env, strip_quotes=True)
    assert result.trimmed["KEY"] == "world"


def test_trim_env_strip_quotes_false_leaves_quotes():
    env = {"KEY": '"hello"'}
    result = trim_env(env, strip_quotes=False)
    assert result.total_trimmed == 0


def test_trim_env_preserves_original():
    env = {"KEY": "  val  "}
    result = trim_env(env)
    assert result.original["KEY"] == "  val  "


def test_trim_result_repr():
    env = {"A": " a ", "B": "b"}
    result = trim_env(env)
    assert "TrimResult" in repr(result)


# ---------------------------------------------------------------------------
# Integration tests — trim_env_file
# ---------------------------------------------------------------------------

@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=  secret  \nHOST=localhost\n")
    return p


def test_trim_env_file_writes_changes(env_file: Path):
    result = trim_env_file(str(env_file))
    assert result.total_trimmed == 1
    content = env_file.read_text()
    assert "secret" in content
    assert "  secret  " not in content


def test_trim_env_file_dry_run_no_write(env_file: Path):
    original = env_file.read_text()
    result = trim_env_file(str(env_file), dry_run=True)
    assert result.total_trimmed == 1
    assert env_file.read_text() == original


def test_trim_env_file_no_changes_when_clean(tmp_path: Path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=8080\n")
    result = trim_env_file(str(p))
    assert result.total_trimmed == 0
