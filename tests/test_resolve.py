"""Tests for envoy.resolve."""

import pytest
from envoy.resolve import (
    resolve_value,
    resolve_env,
    unresolved_references,
    ResolutionError,
)


# ---------------------------------------------------------------------------
# resolve_value
# ---------------------------------------------------------------------------

def test_resolve_value_dollar_brace_syntax():
    env = {"HOST": "localhost"}
    assert resolve_value("http://${HOST}:8080", env) == "http://localhost:8080"


def test_resolve_value_dollar_syntax():
    env = {"PORT": "5432"}
    assert resolve_value("$PORT", env) == "5432"


def test_resolve_value_multiple_refs():
    env = {"PROTO": "https", "HOST": "example.com"}
    assert resolve_value("${PROTO}://${HOST}", env) == "https://example.com"


def test_resolve_value_unknown_ref_leaves_placeholder():
    result = resolve_value("${UNDEFINED}", {}, strict=False)
    assert result == "${UNDEFINED}"


def test_resolve_value_strict_raises_on_unknown():
    with pytest.raises(ResolutionError, match="UNDEFINED"):
        resolve_value("${UNDEFINED}", {}, strict=True)


def test_resolve_value_no_refs_unchanged():
    assert resolve_value("plain-value", {}) == "plain-value"


# ---------------------------------------------------------------------------
# resolve_env
# ---------------------------------------------------------------------------

def test_resolve_env_expands_cross_references():
    env = {"A": "hello", "B": "${A}_world"}
    result = resolve_env(env)
    assert result["B"] == "hello_world"


def test_resolve_env_chained_references():
    env = {"A": "foo", "B": "${A}bar", "C": "${B}baz"}
    result = resolve_env(env)
    assert result["C"] == "foobarbaz"


def test_resolve_env_does_not_mutate_original():
    env = {"X": "${Y}", "Y": "42"}
    original = dict(env)
    resolve_env(env)
    assert env == original


def test_resolve_env_strict_raises_for_undefined():
    env = {"A": "${MISSING}"}
    with pytest.raises(ResolutionError):
        resolve_env(env, strict=True)


def test_resolve_env_leaves_unresolvable_in_non_strict():
    env = {"A": "${NOPE}"}
    result = resolve_env(env, strict=False)
    assert result["A"] == "${NOPE}"


def test_resolve_env_plain_values_unchanged():
    env = {"DB": "postgres", "PORT": "5432"}
    assert resolve_env(env) == env


# ---------------------------------------------------------------------------
# unresolved_references
# ---------------------------------------------------------------------------

def test_unresolved_references_detects_missing_key():
    env = {"URL": "http://${HOST}"}
    dangling = unresolved_references(env)
    assert "URL" in dangling
    assert "HOST" in dangling["URL"]


def test_unresolved_references_empty_when_all_resolved():
    env = {"HOST": "localhost", "URL": "http://${HOST}"}
    # After resolution the value no longer contains placeholders.
    resolved = resolve_env(env)
    assert unresolved_references(resolved) == {}


def test_unresolved_references_multiple_missing():
    env = {"CONN": "${USER}:${PASS}@${HOST}"}
    dangling = unresolved_references(env)
    assert set(dangling["CONN"]) == {"USER", "PASS", "HOST"}
