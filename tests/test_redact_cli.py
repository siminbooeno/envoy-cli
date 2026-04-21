"""Tests for the redact CLI command integration."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
import io

from envoy.redact import redact_env, diff_redacted


@pytest.fixture
def env_file(tmp_path):
    """Create a temporary .env file with mixed secret/non-secret keys."""
    f = tmp_path / ".env"
    f.write_text(
        "APP_NAME=myapp\n"
        "API_KEY=supersecret123\n"
        "DB_PASSWORD=hunter2\n"
        "DEBUG=true\n"
        "PORT=8080\n"
    )
    return f


@pytest.fixture
def redacted_file(tmp_path):
    """Create a temporary already-redacted .env file."""
    f = tmp_path / ".env.redacted"
    f.write_text(
        "APP_NAME=myapp\n"
        "API_KEY=***REDACTED***\n"
        "DB_PASSWORD=***REDACTED***\n"
        "DEBUG=true\n"
        "PORT=8080\n"
    )
    return f


def test_redact_env_output_masks_secrets(env_file):
    """redact_env should mask keys identified as secrets."""
    from envoy.parser import load_env_file

    env = load_env_file(str(env_file))
    result = redact_env(env)

    assert result["API_KEY"] != "supersecret123"
    assert result["DB_PASSWORD"] != "hunter2"
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"
    assert result["PORT"] == "8080"


def test_redact_env_uses_custom_placeholder(env_file):
    """redact_env should use the provided placeholder string."""
    from envoy.parser import load_env_file

    env = load_env_file(str(env_file))
    result = redact_env(env, placeholder="<hidden>")

    assert result["API_KEY"] == "<hidden>"
    assert result["DB_PASSWORD"] == "<hidden>"


def test_redact_env_with_extra_keys(env_file):
    """redact_env should also mask explicitly listed extra keys."""
    from envoy.parser import load_env_file

    env = load_env_file(str(env_file))
    result = redact_env(env, extra_keys=["PORT"])

    assert result["PORT"] != "8080"
    assert result["APP_NAME"] == "myapp"


def test_diff_redacted_shows_no_diff_for_matching(env_file, redacted_file):
    """diff_redacted should return empty diff when redacted output matches expected."""
    from envoy.parser import load_env_file

    original = load_env_file(str(env_file))
    redacted = redact_env(original)
    # Compare redacted against itself — no differences expected
    diff = diff_redacted(redacted, redacted)

    assert diff == {} or all(v is None for v in diff.values())


def test_diff_redacted_detects_unmasked_secret(env_file):
    """diff_redacted should surface keys that differ between two redacted views."""
    from envoy.parser import load_env_file

    original = load_env_file(str(env_file))
    redacted_a = redact_env(original)
    # Simulate a version where API_KEY was accidentally left unmasked
    redacted_b = dict(redacted_a)
    redacted_b["API_KEY"] = "supersecret123"

    diff = diff_redacted(redacted_a, redacted_b)

    assert "API_KEY" in diff


def test_redact_env_returns_new_dict(env_file):
    """redact_env must not mutate the original env dict."""
    from envoy.parser import load_env_file

    env = load_env_file(str(env_file))
    original_api_key = env.get("API_KEY")
    redact_env(env)

    assert env.get("API_KEY") == original_api_key


def test_redact_empty_env():
    """redact_env on an empty dict should return an empty dict."""
    result = redact_env({})
    assert result == {}


def test_redact_env_all_non_secret_keys_unchanged():
    """Non-secret keys should pass through redact_env unchanged."""
    env = {"APP_NAME": "myapp", "DEBUG": "false", "PORT": "3000"}
    result = redact_env(env)

    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "false"
    assert result["PORT"] == "3000"
