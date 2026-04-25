"""Tests for envoy.defaults."""
import json
import pytest
from pathlib import Path

from envoy.defaults import (
    load_defaults,
    save_defaults,
    set_default,
    remove_default,
    apply_defaults,
    missing_defaults,
    _defaults_path,
)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


def test_load_defaults_empty_when_no_file(env_file):
    assert load_defaults(env_file) == {}


def test_save_and_load_defaults(env_file):
    defaults = {"HOST": "localhost", "PORT": "5432"}
    save_defaults(env_file, defaults)
    loaded = load_defaults(env_file)
    assert loaded == defaults


def test_save_creates_envoy_dir(env_file):
    save_defaults(env_file, {"X": "1"})
    assert _defaults_path(env_file).exists()


def test_set_default_adds_key(env_file):
    set_default(env_file, "DEBUG", "false")
    assert load_defaults(env_file)["DEBUG"] == "false"


def test_set_default_overwrites_existing(env_file):
    set_default(env_file, "DEBUG", "false")
    set_default(env_file, "DEBUG", "true")
    assert load_defaults(env_file)["DEBUG"] == "true"


def test_remove_default_returns_true_when_found(env_file):
    set_default(env_file, "KEY", "val")
    assert remove_default(env_file, "KEY") is True
    assert "KEY" not in load_defaults(env_file)


def test_remove_default_returns_false_when_missing(env_file):
    assert remove_default(env_file, "GHOST") is False


def test_apply_defaults_fills_missing_keys():
    env = {"A": "1"}
    defaults = {"A": "99", "B": "2"}
    result = apply_defaults(env, defaults)
    assert result["A"] == "1"   # existing key preserved
    assert result["B"] == "2"   # missing key filled


def test_apply_defaults_fills_empty_values():
    env = {"A": ""}
    defaults = {"A": "default_a"}
    result = apply_defaults(env, defaults)
    assert result["A"] == "default_a"


def test_apply_defaults_overwrite_flag():
    env = {"A": "original"}
    defaults = {"A": "new"}
    result = apply_defaults(env, defaults, overwrite=True)
    assert result["A"] == "new"


def test_apply_defaults_does_not_mutate_original():
    env = {"A": "1"}
    defaults = {"B": "2"}
    apply_defaults(env, defaults)
    assert "B" not in env


def test_missing_defaults_returns_absent_keys():
    env = {"A": "1"}
    defaults = {"A": "x", "B": "y", "C": "z"}
    result = missing_defaults(env, defaults)
    assert "A" not in result
    assert result == {"B": "y", "C": "z"}


def test_missing_defaults_includes_empty_values():
    env = {"A": ""}
    defaults = {"A": "fallback"}
    result = missing_defaults(env, defaults)
    assert "A" in result
