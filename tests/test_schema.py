"""Tests for envoy.schema validation module."""

import pytest

from envoy.schema import (
    FieldSchema,
    FieldType,
    SchemaViolation,
    SchemaResult,
    validate_env,
)


def test_valid_env_passes():
    schema = {
        "APP_NAME": FieldSchema(type=FieldType.STRING, required=True),
        "PORT": FieldSchema(type=FieldType.INTEGER, required=True),
    }
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = validate_env(env, schema)
    assert result.is_valid


def test_missing_required_key_fails():
    schema = {"SECRET_KEY": FieldSchema(required=True)}
    result = validate_env({}, schema)
    assert not result.is_valid
    assert any("required" in str(v) for v in result.violations)


def test_missing_optional_key_passes():
    schema = {"OPTIONAL_VAR": FieldSchema(required=False)}
    result = validate_env({}, schema)
    assert result.is_valid


def test_integer_type_valid():
    schema = {"WORKERS": FieldSchema(type=FieldType.INTEGER)}
    result = validate_env({"WORKERS": "4"}, schema)
    assert result.is_valid


def test_integer_type_invalid():
    schema = {"WORKERS": FieldSchema(type=FieldType.INTEGER)}
    result = validate_env({"WORKERS": "four"}, schema)
    assert not result.is_valid
    assert any("integer" in str(v) for v in result.violations)


def test_boolean_type_valid():
    schema = {"DEBUG": FieldSchema(type=FieldType.BOOLEAN)}
    for val in ["true", "false", "1", "0", "yes", "no"]:
        result = validate_env({"DEBUG": val}, schema)
        assert result.is_valid, f"Expected {val!r} to be valid boolean"


def test_boolean_type_invalid():
    schema = {"DEBUG": FieldSchema(type=FieldType.BOOLEAN)}
    result = validate_env({"DEBUG": "maybe"}, schema)
    assert not result.is_valid


def test_url_type_valid():
    schema = {"API_URL": FieldSchema(type=FieldType.URL)}
    result = validate_env({"API_URL": "https://example.com/api"}, schema)
    assert result.is_valid


def test_url_type_invalid():
    schema = {"API_URL": FieldSchema(type=FieldType.URL)}
    result = validate_env({"API_URL": "not-a-url"}, schema)
    assert not result.is_valid


def test_email_type_valid():
    schema = {"ADMIN_EMAIL": FieldSchema(type=FieldType.EMAIL)}
    result = validate_env({"ADMIN_EMAIL": "admin@example.com"}, schema)
    assert result.is_valid


def test_email_type_invalid():
    schema = {"ADMIN_EMAIL": FieldSchema(type=FieldType.EMAIL)}
    result = validate_env({"ADMIN_EMAIL": "not-an-email"}, schema)
    assert not result.is_valid


def test_pattern_match_valid():
    schema = {"VERSION": FieldSchema(pattern=r"\d+\.\d+\.\d+")}
    result = validate_env({"VERSION": "1.2.3"}, schema)
    assert result.is_valid


def test_pattern_match_invalid():
    schema = {"VERSION": FieldSchema(pattern=r"\d+\.\d+\.\d+")}
    result = validate_env({"VERSION": "v1.2"}, schema)
    assert not result.is_valid
    assert any("pattern" in str(v) for v in result.violations)


def test_schema_result_str_valid():
    result = SchemaResult(violations=[])
    assert result.is_valid
    assert "valid" in str(result).lower()


def test_schema_result_str_invalid():
    violation = SchemaViolation(field="MY_VAR", message="is required")
    result = SchemaResult(violations=[violation])
    assert not result.is_valid
    assert "MY_VAR" in str(result)
