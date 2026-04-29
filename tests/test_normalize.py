"""Tests for envoy/normalize.py"""

import pytest

from envoy.normalize import (
    NormalizeResult,
    normalize_env,
    normalize_env_file,
    normalize_key,
    normalize_value,
)


def test_normalize_key_uppercases():
    assert normalize_key("my_key") == "MY_KEY"


def test_normalize_key_replaces_dashes():
    assert normalize_key("my-key") == "MY_KEY"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  KEY  ") == "KEY"


def test_normalize_value_strips_whitespace():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_no_strip_preserves_whitespace():
    assert normalize_value("  hello  ", strip=False) == "  hello  "


def test_normalize_value_lowercase():
    assert normalize_value("HELLO", lowercase=True) == "hello"


def test_normalize_env_uppercases_keys():
    env = {"my_key": "value"}
    result_env, report = normalize_env(env)
    assert "MY_KEY" in result_env
    assert result_env["MY_KEY"] == "value"


def test_normalize_env_strips_values():
    env = {"KEY": "  spaced  "}
    result_env, report = normalize_env(env)
    assert result_env["KEY"] == "spaced"
    assert report.total_changed == 1


def test_normalize_env_no_change_not_reported():
    env = {"KEY": "clean"}
    _, report = normalize_env(env)
    assert report.total_changed == 0


def test_normalize_env_only_filter_skips_other_keys():
    env = {"KEY_A": "  val  ", "KEY_B": "  val  "}
    _, report = normalize_env(env, only=["KEY_A"])
    assert report.total_skipped == 1
    assert report.total_changed == 1


def test_normalize_env_lowercase_values():
    env = {"KEY": "UPPER"}
    result_env, report = normalize_env(env, lowercase_values=True)
    assert result_env["KEY"] == "upper"


def test_normalize_env_no_keys_preserves_case():
    env = {"lower_key": "value"}
    result_env, _ = normalize_env(env, keys=False)
    assert "lower_key" in result_env


def test_normalize_env_no_values_preserves_whitespace():
    env = {"KEY": "  spaced  "}
    result_env, report = normalize_env(env, values=False)
    assert result_env["KEY"] == "  spaced  "
    assert report.total_changed == 0


def test_normalize_result_repr():
    r = NormalizeResult(changed=[("K", "a", "b")], skipped=["X"])
    assert "NormalizeResult" in repr(r)
    assert "1" in repr(r)


def test_normalize_env_file_writes_changes(tmp_path):
    f = tmp_path / ".env"
    f.write_text("my-key=  hello  \n")
    result = normalize_env_file(str(f))
    content = f.read_text()
    assert "MY_KEY" in content
    assert "hello" in content
    assert result.total_changed == 1


def test_normalize_env_file_dry_run_no_write(tmp_path):
    f = tmp_path / ".env"
    f.write_text("my-key=  hello  \n")
    original = f.read_text()
    normalize_env_file(str(f), dry_run=True)
    assert f.read_text() == original


def test_normalize_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        normalize_env_file("/nonexistent/.env")
