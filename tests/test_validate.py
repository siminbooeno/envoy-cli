"""Tests for envoy.validate module."""

import pytest
from envoy.validate import (
    RuleType,
    ValidationError,
    ValidationResult,
    validate_env,
    validate_non_empty,
    validate_regex,
    validate_allowed,
    validate_min_length,
)


SAMPLE_ENV = {
    "APP_ENV": "production",
    "PORT": "8080",
    "SECRET_KEY": "abc123",
    "EMPTY_VAR": "",
    "LOG_LEVEL": "info",
}


def test_validate_non_empty_passes_for_filled_keys():
    result = ValidationResult()
    validate_non_empty(SAMPLE_ENV, ["APP_ENV", "PORT"], result)
    assert result.valid


def test_validate_non_empty_fails_for_empty_value():
    result = ValidationResult()
    validate_non_empty(SAMPLE_ENV, ["EMPTY_VAR"], result)
    assert not result.valid
    assert result.errors[0].key == "EMPTY_VAR"
    assert result.errors[0].rule == RuleType.NON_EMPTY


def test_validate_non_empty_fails_for_missing_key():
    result = ValidationResult()
    validate_non_empty(SAMPLE_ENV, ["MISSING_KEY"], result)
    assert not result.valid


def test_validate_regex_passes_matching_value():
    result = ValidationResult()
    validate_regex(SAMPLE_ENV, {"PORT": r"\d+"}, result)
    assert result.valid


def test_validate_regex_fails_non_matching_value():
    result = ValidationResult()
    validate_regex(SAMPLE_ENV, {"APP_ENV": r"\d+"}, result)
    assert not result.valid
    assert result.errors[0].rule == RuleType.REGEX


def test_validate_regex_skips_missing_key():
    result = ValidationResult()
    validate_regex(SAMPLE_ENV, {"NONEXISTENT": r".*"}, result)
    assert result.valid


def test_validate_allowed_passes_for_valid_value():
    result = ValidationResult()
    validate_allowed(SAMPLE_ENV, {"LOG_LEVEL": ["debug", "info", "warning", "error"]}, result)
    assert result.valid


def test_validate_allowed_fails_for_invalid_value():
    result = ValidationResult()
    validate_allowed(SAMPLE_ENV, {"APP_ENV": ["staging", "development"]}, result)
    assert not result.valid
    assert result.errors[0].rule == RuleType.ALLOWED


def test_validate_min_length_passes():
    result = ValidationResult()
    validate_min_length(SAMPLE_ENV, {"SECRET_KEY": 4}, result)
    assert result.valid


def test_validate_min_length_fails():
    result = ValidationResult()
    validate_min_length(SAMPLE_ENV, {"SECRET_KEY": 100}, result)
    assert not result.valid
    assert result.errors[0].rule == RuleType.MIN_LENGTH


def test_validate_env_combined_all_pass():
    result = validate_env(
        SAMPLE_ENV,
        non_empty=["APP_ENV", "PORT"],
        regex={"PORT": r"\d+"},
        allowed={"LOG_LEVEL": ["debug", "info", "warning"]},
        min_length={"SECRET_KEY": 3},
    )
    assert result.valid
    assert result.summary() == "All validations passed."


def test_validate_env_combined_with_failure():
    result = validate_env(
        SAMPLE_ENV,
        non_empty=["EMPTY_VAR"],
        regex={"APP_ENV": r"\d+"},
    )
    assert not result.valid
    assert len(result.errors) == 2
    assert "2 validation error(s)" in result.summary()


def test_validation_error_str():
    err = ValidationError(key="FOO", rule=RuleType.NON_EMPTY, message="must not be empty")
    assert "non_empty" in str(err)
    assert "FOO" in str(err)
