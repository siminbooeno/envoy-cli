"""Tests for envoy.template module."""

import pytest
from envoy.template import (
    render_template,
    render_env_template,
    collect_variables,
    missing_variables,
)


def test_render_template_dollar_brace_syntax():
    result = render_template("Hello, ${NAME}!", {"NAME": "World"})
    assert result == "Hello, World!"


def test_render_template_dollar_syntax():
    result = render_template("Hello, $NAME!", {"NAME": "Alice"})
    assert result == "Hello, Alice!"


def test_render_template_multiple_vars():
    result = render_template("${PROTO}://${HOST}:${PORT}", {
        "PROTO": "https",
        "HOST": "example.com",
        "PORT": "443",
    })
    assert result == "https://example.com:443"


def test_render_template_missing_var_leaves_placeholder():
    result = render_template("${MISSING}_value", {})
    assert result == "${MISSING}_value"


def test_render_template_strict_raises_on_missing():
    with pytest.raises(KeyError, match="MISSING"):
        render_template("${MISSING}", {}, strict=True)


def test_render_template_no_vars():
    result = render_template("plain_value", {"UNUSED": "x"})
    assert result == "plain_value"


def test_render_env_template_all_values_substituted():
    env = {
        "DATABASE_URL": "postgres://${DB_USER}:${DB_PASS}@${DB_HOST}/mydb",
        "APP_ENV": "$ENVIRONMENT",
        "STATIC": "no-substitution",
    }
    context = {"DB_USER": "admin", "DB_PASS": "secret", "DB_HOST": "localhost", "ENVIRONMENT": "production"}
    result = render_env_template(env, context)
    assert result["DATABASE_URL"] == "postgres://admin:secret@localhost/mydb"
    assert result["APP_ENV"] == "production"
    assert result["STATIC"] == "no-substitution"


def test_render_env_template_strict_raises():
    env = {"URL": "http://${HOST}"}
    with pytest.raises(KeyError):
        render_env_template(env, {}, strict=True)


def test_collect_variables_brace_and_plain():
    vars_ = collect_variables("${FOO} and $BAR plus ${FOO}")
    assert vars_ == ["BAR", "FOO"]


def test_collect_variables_empty_string():
    assert collect_variables("") == []


def test_missing_variables_returns_absent_keys():
    env = {
        "A": "${X}",
        "B": "$Y",
        "C": "literal",
    }
    missing = missing_variables(env, {"X": "1"})
    assert missing == ["Y"]


def test_missing_variables_none_when_all_provided():
    env = {"A": "${X}", "B": "${Y}"}
    missing = missing_variables(env, {"X": "1", "Y": "2"})
    assert missing == []
