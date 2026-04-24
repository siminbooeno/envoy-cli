"""Tests for envoy.search."""
import pytest

from envoy.search import search_env, SearchReport


SAMPLE_ENV = {
    "API_KEY": "abc123",
    "DATABASE_URL": "postgres://localhost/mydb",
    "DEBUG": "true",
    "APP_NAME": "myapp",
    "SECRET_TOKEN": "s3cr3t",
}


def test_search_finds_key_substring():
    report = search_env(SAMPLE_ENV, "API")
    assert "API_KEY" in report.keys()


def test_search_finds_value_substring():
    report = search_env(SAMPLE_ENV, "postgres")
    assert "DATABASE_URL" in report.keys()


def test_search_case_insensitive_by_default():
    report = search_env(SAMPLE_ENV, "debug")
    assert "DEBUG" in report.keys()


def test_search_case_sensitive_no_match():
    report = search_env(SAMPLE_ENV, "debug", case_sensitive=True)
    assert "DEBUG" not in report.keys()


def test_search_keys_only_skips_value_match():
    report = search_env(SAMPLE_ENV, "postgres", search_values=False)
    assert report.total == 0


def test_search_values_only_skips_key_match():
    report = search_env(SAMPLE_ENV, "API_KEY", search_keys=False)
    assert report.total == 0


def test_search_exact_match():
    report = search_env(SAMPLE_ENV, "DEBUG", exact=True)
    assert report.total == 1
    assert report.keys() == ["DEBUG"]


def test_search_exact_no_partial_match():
    report = search_env(SAMPLE_ENV, "DEBU", exact=True)
    assert report.total == 0


def test_search_matched_key_flag():
    report = search_env(SAMPLE_ENV, "APP_NAME", search_values=False)
    assert report.results[0].matched_key is True
    assert report.results[0].matched_value is False


def test_search_matched_value_flag():
    report = search_env(SAMPLE_ENV, "true", search_keys=False)
    result = next(r for r in report.results if r.key == "DEBUG")
    assert result.matched_value is True
    assert result.matched_key is False


def test_search_no_results_returns_empty_report():
    report = search_env(SAMPLE_ENV, "NONEXISTENT_XYZ")
    assert report.total == 0
    assert report.keys() == []


def test_search_report_pattern_stored():
    report = search_env(SAMPLE_ENV, "API")
    assert report.pattern == "API"


def test_search_multiple_matches():
    report = search_env(SAMPLE_ENV, "myapp")
    # matches APP_NAME value and DATABASE_URL value contains 'mydb' not 'myapp'
    assert any(r.key == "APP_NAME" for r in report.results)
