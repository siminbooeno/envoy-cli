"""Tests for envoy.inject."""

from __future__ import annotations

import pytest

from envoy.inject import inject_env, InjectResult


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "true",
}


def test_inject_env_adds_all_keys_to_empty_base():
    result = inject_env(SAMPLE_ENV, base={})
    assert result.injected == SAMPLE_ENV
    assert result.skipped == []


def test_inject_env_skips_existing_without_overwrite():
    base = {"APP_NAME": "existing"}
    result = inject_env(SAMPLE_ENV, base=base, overwrite=False)
    assert "APP_NAME" not in result.injected
    assert "APP_NAME" in result.skipped
    assert base["APP_NAME"] == "existing"


def test_inject_env_overwrites_when_flag_set():
    base = {"APP_NAME": "existing"}
    result = inject_env(SAMPLE_ENV, base=base, overwrite=True)
    assert "APP_NAME" in result.injected
    assert result.injected["APP_NAME"] == "myapp"
    assert "APP_NAME" not in result.skipped


def test_inject_env_keys_filter_limits_injection():
    result = inject_env(SAMPLE_ENV, base={}, keys=["APP_NAME"])
    assert list(result.injected.keys()) == ["APP_NAME"]
    assert "SECRET_KEY" not in result.injected
    assert "DEBUG" not in result.injected


def test_inject_env_keys_filter_unknown_key_is_ignored():
    result = inject_env(SAMPLE_ENV, base={}, keys=["NONEXISTENT"])
    assert result.total_injected == 0
    assert result.skipped == []


def test_inject_env_total_injected_property():
    result = inject_env(SAMPLE_ENV, base={})
    assert result.total_injected == len(SAMPLE_ENV)


def test_inject_env_repr_contains_counts():
    result = inject_env(SAMPLE_ENV, base={})
    r = repr(result)
    assert "injected=" in r
    assert "skipped=" in r


def test_inject_env_uses_os_environ_as_default_base(monkeypatch):
    monkeypatch.setenv("EXISTING_VAR", "yes")
    result = inject_env({"NEW_VAR": "hello"}, overwrite=False)
    assert "NEW_VAR" in result.injected
    assert result.skipped == []


def test_inject_env_does_not_mutate_source_dict():
    original = dict(SAMPLE_ENV)
    inject_env(SAMPLE_ENV, base={"APP_NAME": "x"}, overwrite=False)
    assert SAMPLE_ENV == original
