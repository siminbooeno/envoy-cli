"""Tests for envoy.filter module."""
import pytest
from envoy.filter import (
    filter_by_prefix,
    filter_by_pattern,
    filter_by_value,
    filter_empty,
    filter_env,
    FilterResult,
)

SAMPLE = {
    "APP_NAME": "myapp",
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "abc123",
    "EMPTY_VAR": "",
}


def test_filter_by_prefix_keeps_matching_keys():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert set(result.matched.keys()) == {"APP_NAME", "APP_ENV"}


def test_filter_by_prefix_excludes_non_matching():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert "DB_HOST" in result.excluded
    assert "SECRET_KEY" in result.excluded


def test_filter_by_pattern_matches_regex():
    result = filter_by_pattern(SAMPLE, r"^DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_pattern_partial_match():
    result = filter_by_pattern(SAMPLE, r"PORT")
    assert "DB_PORT" in result.matched


def test_filter_by_value_matches_value_content():
    result = filter_by_value(SAMPLE, r"\d+")
    assert "DB_PORT" in result.matched
    assert "SECRET_KEY" in result.matched  # abc123 contains digits


def test_filter_by_value_excludes_non_matching():
    result = filter_by_value(SAMPLE, r"^localhost$")
    assert set(result.matched.keys()) == {"DB_HOST"}


def test_filter_empty_excludes_blank_values():
    result = filter_empty(SAMPLE)
    assert "EMPTY_VAR" not in result.matched
    assert "EMPTY_VAR" in result.excluded


def test_filter_empty_keeps_non_empty():
    result = filter_empty(SAMPLE)
    assert "APP_NAME" in result.matched
    assert "DB_HOST" in result.matched


def test_filter_env_prefix_only():
    result = filter_env(SAMPLE, prefix="DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_env_combined_prefix_and_exclude_empty():
    env = {"APP_NAME": "myapp", "APP_EMPTY": "", "DB_HOST": "localhost"}
    result = filter_env(env, prefix="APP_", exclude_empty=True)
    assert result.matched == {"APP_NAME": "myapp"}
    assert "APP_EMPTY" in result.excluded
    assert "DB_HOST" in result.excluded


def test_filter_result_counts():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert result.total_matched == 2
    assert result.total_excluded == len(SAMPLE) - 2


def test_filter_env_no_filters_returns_all():
    result = filter_env(SAMPLE)
    assert result.matched == SAMPLE
    assert result.total_excluded == 0


def test_filter_env_pattern_and_value_pattern():
    result = filter_env(SAMPLE, pattern=r"^DB_", value_pattern=r"^\d+$")
    assert result.matched == {"DB_PORT": "5432"}
