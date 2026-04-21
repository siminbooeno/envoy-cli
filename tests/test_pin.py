"""Tests for envoy.pin module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.pin import (
    load_pins,
    save_pins,
    add_pin,
    remove_pin,
    check_pins,
    list_pins,
    PIN_FILENAME,
)


@pytest.fixture
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_pins_empty_when_no_file(pin_dir):
    result = load_pins(str(pin_dir))
    assert result == {}


def test_save_and_load_pins(pin_dir):
    pins = {"API_KEY": "abc123", "DB_HOST": "localhost"}
    save_pins(pins, str(pin_dir))
    loaded = load_pins(str(pin_dir))
    assert loaded == pins


def test_save_pins_creates_file(pin_dir):
    save_pins({"FOO": "bar"}, str(pin_dir))
    assert (pin_dir / PIN_FILENAME).exists()


def test_add_pin_stores_key_value(pin_dir):
    result = add_pin("SECRET", "mysecret", directory=str(pin_dir))
    assert result["SECRET"] == "mysecret"
    assert load_pins(str(pin_dir))["SECRET"] == "mysecret"


def test_add_pin_overwrites_existing(pin_dir):
    add_pin("KEY", "old", directory=str(pin_dir))
    add_pin("KEY", "new", directory=str(pin_dir))
    assert load_pins(str(pin_dir))["KEY"] == "new"


def test_remove_pin_returns_true_when_exists(pin_dir):
    add_pin("TO_REMOVE", "val", directory=str(pin_dir))
    result = remove_pin("TO_REMOVE", directory=str(pin_dir))
    assert result is True
    assert "TO_REMOVE" not in load_pins(str(pin_dir))


def test_remove_pin_returns_false_when_missing(pin_dir):
    result = remove_pin("NONEXISTENT", directory=str(pin_dir))
    assert result is False


def test_check_pins_no_violations(pin_dir):
    save_pins({"HOST": "localhost", "PORT": "5432"}, str(pin_dir))
    env = {"HOST": "localhost", "PORT": "5432", "EXTRA": "ignored"}
    violations = check_pins(env, directory=str(pin_dir))
    assert violations == []


def test_check_pins_wrong_value(pin_dir):
    save_pins({"HOST": "localhost"}, str(pin_dir))
    env = {"HOST": "remotehost"}
    violations = check_pins(env, directory=str(pin_dir))
    assert len(violations) == 1
    assert "HOST" in violations[0]
    assert "remotehost" in violations[0]


def test_check_pins_missing_key(pin_dir):
    save_pins({"REQUIRED": "value"}, str(pin_dir))
    violations = check_pins({}, directory=str(pin_dir))
    assert len(violations) == 1
    assert "missing" in violations[0]


def test_list_pins_returns_all(pin_dir):
    save_pins({"A": "1", "B": "2"}, str(pin_dir))
    result = list_pins(str(pin_dir))
    assert result == {"A": "1", "B": "2"}


def test_check_pins_no_pins_defined(pin_dir):
    env = {"FOO": "bar"}
    violations = check_pins(env, directory=str(pin_dir))
    assert violations == []
