"""Tests for envoy.redact module."""

import pytest
from envoy.redact import (
    REDACTED_PLACEHOLDER,
    redact_env,
    redact_value,
    diff_redacted,
)


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_masks_secret_keys():
    env = {"API_KEY": "abc123", "HOST": "localhost"}
    result = redact_env(env)
    assert result["API_KEY"] == REDACTED_PLACEHOLDER
    assert result["HOST"] == "localhost"


def test_redact_env_masks_extra_keys():
    env = {"CUSTOM_TOKEN": "secret", "APP_NAME": "envoy"}
    # APP_NAME is not a secret by heuristic, but we force-redact it
    result = redact_env(env, extra_keys=["APP_NAME"])
    assert result["APP_NAME"] == REDACTED_PLACEHOLDER
    assert result["CUSTOM_TOKEN"] == REDACTED_PLACEHOLDER


def test_redact_env_custom_placeholder():
    env = {"SECRET_KEY": "s3cr3t"}
    result = redact_env(env, placeholder="***")
    assert result["SECRET_KEY"] == "***"


def test_redact_env_preserves_non_secret_keys():
    env = {"PORT": "8080", "DEBUG": "true", "LOG_LEVEL": "info"}
    result = redact_env(env)
    assert result == env


def test_redact_env_returns_copy():
    env = {"API_SECRET": "original"}
    result = redact_env(env)
    assert result is not env
    # Original unchanged
    assert env["API_SECRET"] == "original"


def test_redact_env_empty_dict():
    assert redact_env({}) == {}


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_secret_key():
    assert redact_value("PASSWORD", "hunter2") == REDACTED_PLACEHOLDER


def test_redact_value_non_secret_key():
    assert redact_value("HOST", "localhost") == "localhost"


def test_redact_value_extra_key_case_insensitive():
    assert redact_value("my_token", "abc", extra_keys=["MY_TOKEN"]) == REDACTED_PLACEHOLDER


# ---------------------------------------------------------------------------
# diff_redacted
# ---------------------------------------------------------------------------

def test_diff_redacted_detects_changed_value():
    before = {"HOST": "old", "PORT": "80"}
    after = {"HOST": "new", "PORT": "80"}
    changes = diff_redacted(before, after)
    assert "HOST" in changes
    assert changes["HOST"]["before"] == "old"
    assert changes["HOST"]["after"] == "new"
    assert "PORT" not in changes


def test_diff_redacted_masks_secret_changes():
    before = {"API_KEY": "key1"}
    after = {"API_KEY": "key2"}
    changes = diff_redacted(before, after)
    assert changes["API_KEY"]["before"] == REDACTED_PLACEHOLDER
    assert changes["API_KEY"]["after"] == REDACTED_PLACEHOLDER


def test_diff_redacted_added_key():
    before = {}
    after = {"NEW_VAR": "hello"}
    changes = diff_redacted(before, after)
    assert changes["NEW_VAR"]["before"] is None
    assert changes["NEW_VAR"]["after"] == "hello"


def test_diff_redacted_removed_key():
    before = {"OLD_VAR": "bye"}
    after = {}
    changes = diff_redacted(before, after)
    assert changes["OLD_VAR"]["before"] == "bye"
    assert changes["OLD_VAR"]["after"] is None


def test_diff_redacted_no_changes():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert diff_redacted(env, env.copy()) == {}
