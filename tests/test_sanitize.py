"""Tests for envoy.sanitize."""

from __future__ import annotations

import pytest

from envoy.sanitize import sanitize_env, sanitize_value


# ---------------------------------------------------------------------------
# sanitize_value
# ---------------------------------------------------------------------------

def test_sanitize_value_strips_whitespace():
    assert sanitize_value("  hello  ") == "hello"


def test_sanitize_value_no_strip_preserves_whitespace():
    assert sanitize_value("  hello  ", strip_whitespace=False) == "  hello  "


def test_sanitize_value_removes_control_chars():
    assert sanitize_value("hel\x01lo") == "hello"


def test_sanitize_value_collapses_newlines():
    assert sanitize_value("line1\nline2") == "line1 line2"


def test_sanitize_value_custom_newline_replacement():
    assert sanitize_value("a\nb", newline_replacement="|") == "a|b"


def test_sanitize_value_max_length_truncates():
    assert sanitize_value("hello world", max_length=5) == "hello"


def test_sanitize_value_clean_value_unchanged():
    assert sanitize_value("clean_value") == "clean_value"


# ---------------------------------------------------------------------------
# sanitize_env
# ---------------------------------------------------------------------------

def test_sanitize_env_changes_dirty_value():
    env = {"KEY": "  dirty  "}
    result = sanitize_env(env)
    assert result.sanitized["KEY"] == "dirty"
    assert "KEY" in result.changes
    assert result.total_changed == 1


def test_sanitize_env_clean_value_no_change():
    env = {"KEY": "clean"}
    result = sanitize_env(env)
    assert result.total_changed == 0
    assert result.sanitized["KEY"] == "clean"


def test_sanitize_env_records_original_and_sanitized():
    env = {"KEY": "  val  "}
    result = sanitize_env(env)
    orig, clean = result.changes["KEY"]
    assert orig == "  val  "
    assert clean == "val"


def test_sanitize_env_only_specified_keys():
    env = {"A": "  a  ", "B": "  b  "}
    result = sanitize_env(env, keys=["A"])
    assert result.sanitized["A"] == "a"
    assert result.sanitized["B"] == "  b  "


def test_sanitize_env_skips_missing_keys():
    env = {"A": "value"}
    result = sanitize_env(env, keys=["A", "MISSING"])
    assert "MISSING" in result.skipped
    assert result.total_skipped == 1


def test_sanitize_env_removes_control_chars():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env)
    assert result.sanitized["KEY"] == "value"


def test_sanitize_env_max_length():
    env = {"KEY": "toolongvalue"}
    result = sanitize_env(env, max_length=4)
    assert result.sanitized["KEY"] == "tool"


def test_sanitize_env_returns_copy_not_mutated():
    env = {"KEY": "  val  "}
    original_env = dict(env)
    sanitize_env(env)
    assert env == original_env


def test_sanitize_result_repr():
    env = {"A": "  x  ", "B": "clean"}
    result = sanitize_env(env)
    assert "SanitizeResult" in repr(result)
    assert "changed=1" in repr(result)
