"""Tests for envoy.cast."""

import pytest

from envoy.cast import (
    CastError,
    cast_bool,
    cast_float,
    cast_int,
    cast_list,
    cast_value,
    cast_env,
)


# ---------------------------------------------------------------------------
# cast_bool
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["1", "true", "True", "TRUE", "yes", "on"])
def test_cast_bool_truthy(raw):
    assert cast_bool("KEY", raw) is True


@pytest.mark.parametrize("raw", ["0", "false", "False", "FALSE", "no", "off"])
def test_cast_bool_falsy(raw):
    assert cast_bool("KEY", raw) is False


def test_cast_bool_invalid_raises():
    with pytest.raises(CastError) as exc_info:
        cast_bool("FLAG", "maybe")
    assert "FLAG" in str(exc_info.value)
    assert exc_info.value.target == "bool"


# ---------------------------------------------------------------------------
# cast_int
# ---------------------------------------------------------------------------

def test_cast_int_valid():
    assert cast_int("PORT", "8080") == 8080


def test_cast_int_with_whitespace():
    assert cast_int("PORT", "  42  ") == 42


def test_cast_int_invalid_raises():
    with pytest.raises(CastError) as exc_info:
        cast_int("PORT", "abc")
    assert exc_info.value.key == "PORT"
    assert exc_info.value.target == "int"


# ---------------------------------------------------------------------------
# cast_float
# ---------------------------------------------------------------------------

def test_cast_float_valid():
    assert cast_float("RATIO", "3.14") == pytest.approx(3.14)


def test_cast_float_invalid_raises():
    with pytest.raises(CastError):
        cast_float("RATIO", "not_a_float")


# ---------------------------------------------------------------------------
# cast_list
# ---------------------------------------------------------------------------

def test_cast_list_comma_separated():
    assert cast_list("HOSTS", "a,b,c") == ["a", "b", "c"]


def test_cast_list_strips_whitespace():
    assert cast_list("HOSTS", " a , b , c ") == ["a", "b", "c"]


def test_cast_list_custom_delimiter():
    assert cast_list("HOSTS", "a|b|c", delimiter="|") == ["a", "b", "c"]


def test_cast_list_ignores_empty_segments():
    assert cast_list("HOSTS", "a,,b") == ["a", "b"]


# ---------------------------------------------------------------------------
# cast_value dispatch
# ---------------------------------------------------------------------------

def test_cast_value_str_passthrough():
    assert cast_value("K", "hello", "str") == "hello"


def test_cast_value_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown target type"):
        cast_value("K", "x", "bytes")


# ---------------------------------------------------------------------------
# cast_env
# ---------------------------------------------------------------------------

def test_cast_env_applies_schema():
    env = {"PORT": "9000", "DEBUG": "true", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool"}
    result = cast_env(env, schema)
    assert result["PORT"] == 9000
    assert result["DEBUG"] is True
    assert result["NAME"] == "app"


def test_cast_env_strict_raises_on_bad_value():
    env = {"PORT": "not_a_number"}
    schema = {"PORT": "int"}
    with pytest.raises(CastError):
        cast_env(env, schema, strict=True)


def test_cast_env_non_strict_keeps_raw_on_error():
    env = {"PORT": "not_a_number"}
    schema = {"PORT": "int"}
    result = cast_env(env, schema, strict=False)
    assert result["PORT"] == "not_a_number"


def test_cast_env_list_with_custom_delimiter():
    env = {"HOSTS": "a|b|c"}
    schema = {"HOSTS": "list"}
    result = cast_env(env, schema, delimiter="|")
    assert result["HOSTS"] == ["a", "b", "c"]
